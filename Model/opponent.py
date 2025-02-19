import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import chess
import chess.pgn
import numpy as np
import os
from pathlib import Path

class ChessboardEncoder:
    def __init__(self):
        self.piece_mapping = {
            'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
            'p': -1, 'n': -2, 'b': -3, 'r': -4, 'q': -5, 'k': -6
        }
    
    def encode_board(self, board):
        # 13 channels: 12 for pieces + 1 for turn indicator
        encoded = np.zeros((13, 8, 8), dtype=np.float32)
        
        # Encode pieces
        for i in range(8):
            for j in range(8):
                piece = board.piece_at(chess.square(j, i))
                if piece is not None:
                    piece_symbol = piece.symbol()
                    color_idx = 0 if piece.color else 6
                    piece_type = abs(self.piece_mapping[piece_symbol]) - 1
                    encoded[piece_type + color_idx][i][j] = 1
        
        # Add turn indicator channel (1 for white, 0 for black)
        encoded[12].fill(1.0 if board.turn else 0.0)
        
        return torch.FloatTensor(encoded)
    
class ChessDataset(Dataset):
    def __init__(self, games):
        self.encoder = ChessboardEncoder()
        self.positions = []
        self.moves = []
        self.turns = []
        
        for game in games:
            board = game.board()
            for move in game.mainline_moves():
                # Store position and whose turn it was
                self.positions.append(board.copy())
                self.turns.append(board.turn)
                
                # Encode move based on the current perspective
                from_square = move.from_square
                to_square = move.to_square
                if not board.turn:  # If it's black's turn, flip the move encoding
                    from_square = chess.square_mirror(from_square)
                    to_square = chess.square_mirror(to_square)
                move_idx = from_square * 64 + to_square
                
                self.moves.append(move_idx)
                board.push(move)
    
    def __len__(self):
        return len(self.positions)
    
    def __getitem__(self, idx):
        position = self.encoder.encode_board(self.positions[idx])
        move = torch.LongTensor([self.moves[idx]])
        return position, move
    
class ChessCNN(nn.Module):
    def __init__(self):
        super(ChessCNN, self).__init__()
        # Modified to accept 13 input channels (12 piece channels + 1 turn channel)
        self.conv1 = nn.Conv2d(13, 64, 3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, 3, padding=1)
        self.fc1 = nn.Linear(256 * 8 * 8, 1024)
        self.fc2 = nn.Linear(1024, 4096)  # 4096 = 64 * 64 possible moves
        self.relu = nn.ReLU()
        self.batch_norm1 = nn.BatchNorm2d(64)
        self.batch_norm2 = nn.BatchNorm2d(128)
        self.batch_norm3 = nn.BatchNorm2d(256)
        self.dropout = nn.Dropout(0.3)
        
    def forward(self, x):
        x = self.batch_norm1(self.relu(self.conv1(x)))
        x = self.batch_norm2(self.relu(self.conv2(x)))
        x = self.batch_norm3(self.relu(self.conv3(x)))
        x = x.view(-1, 256 * 8 * 8)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x
    
def get_best_move(model, board, encoder):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    state = encoder.encode_board(board).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(state)
        move_probs = torch.softmax(output, dim=1)
        
        # Get top 10 moves
        top_moves = torch.topk(move_probs, 10, dim=1)
        
        for move_prob, move_idx in zip(top_moves.values[0], top_moves.indices[0]):
            from_square = move_idx.item() // 64
            to_square = move_idx.item() % 64
            
            # If playing as black, mirror the moves back
            if not board.turn:
                from_square = chess.square_mirror(from_square)
                to_square = chess.square_mirror(to_square)
            
            move = chess.Move(from_square, to_square)
            if move in board.legal_moves:
                return move
        
        # If no legal moves found in top 10, return first legal move
        return list(board.legal_moves)[0]
    
def load_chess_data(pgn_file, max_games=100):
    games = []
    with open(pgn_file, encoding='utf-8') as f:
        for _ in range(max_games):
            game = chess.pgn.read_game(f)
            if game is None:
                break
            games.append(game)
    return games

def train_model(model, train_loader, num_epochs=5):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=2)
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        
        for batch_idx, (positions, moves) in enumerate(train_loader):
            positions = positions.to(device)
            moves = moves.to(device).squeeze()
            
            optimizer.zero_grad()
            output = model(positions)
            loss = criterion(output, moves)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            if batch_idx % 10 == 0:
                print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
        
        avg_loss = total_loss / len(train_loader)
        scheduler.step(avg_loss)
        print(f'Epoch {epoch} complete - Average Loss: {avg_loss:.4f}')
        
        # Save model checkpoint
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': avg_loss,
        }, f'chess_model_checkpoint_{epoch}.pt')
    
    return model

def main():
    # Load data
    games = load_chess_data("Andreikin.pgn", max_games=1000)
    dataset = ChessDataset(games)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Create and train model
    model = ChessCNN()
    trained_model = train_model(model, train_loader, num_epochs=10)
    
    # Save final model
    torch.save(trained_model.state_dict(), 'chess_model_final.pt')


def load_model(model_path):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ChessCNN().to(device)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    return model

def test_model():
    model = load_model('./chess_model_final.pt')
    encoder = ChessboardEncoder()
    board = chess.Board()
    
    for move_num in range(10):  # Play 10 moves (5 for each side)
        if board.is_game_over():
            break
            
        move = get_best_move(model, board, encoder)
        print(f"Move {move_num + 1}")
        print(f"{'White' if board.turn else 'Black'} to move")
        print(f"Position: {board.fen()}")
        print(f"Model's move: {move}")
        board.push(move)
        print(board)
        print("\n")

def Model_makeMove(board,difficulty):
    if difficulty == 0:
        model = load_model('Model/chess_model_easy.pt')
    if difficulty == 1:
        model = load_model('Model/chess_model_mid.pt')
    if difficulty == 2:
        model = load_model('Model/chess_model_hard.pt')
    encoder = ChessboardEncoder()
    board= chess.Board(board)
    print(board)
    move = get_best_move(model, board, encoder)
    return move

if __name__ == "__main__":
    #test_model()
    board = chess.Board()
    print(board.fen())