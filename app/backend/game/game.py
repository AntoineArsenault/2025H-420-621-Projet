import chess

class Game:
    def __init__(self):
        self.board = chess.Board()
        self.current_turn = 'w'  # Par exemple, 'w' pour blanc, 'b' pour noir

    def start_game(self):
        # Logique pour démarrer une nouvelle partie
        pass
    
    def get_board(self):
        return self.board  # Retourne l'état actuel du plateau
    
    def get_fen(self):
        return self.board.fen()
    
    def make_move(self, from_square, to_square):
        """Tente de faire un mouvement."""
        move = chess.Move(from_square, to_square)
        if move in self.board.legal_moves:
            self.board.push(move)  # Appliquer le mouvement
            return True
        return False