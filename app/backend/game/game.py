import chess

class Game:
    def __init__(self):
        self.board = chess.Board()
        self.current_turn = 'w'  # Par exemple, 'w' pour blanc, 'b' pour noir

    def start_game(self):
        # Logique pour démarrer une nouvelle partie
        self.board = chess.Board()
        self.current_turn = 'w'  # Réinitialiser le tour à 'w' (blanc)
    
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
    
    def is_game_over(self):
        # Vérifie si la partie est terminée et retourne la raison de la fin de la partie
        if self.board.is_checkmate():
            return "Échec et mat"
        elif self.board.is_stalemate():
            return "Pat"
        elif self.board.is_insufficient_material():
            return "Matériel insuffisant"
        elif self.board.is_seventyfive_moves():
            return "75 coups sans prise ni mouvement de pion"
        elif self.board.is_fivefold_repetition():
            return "Répetition quintuple"
        elif self.board.is_variant_draw():
            return "Partie nulle (variant)"
        else:
            return None  # La partie n'est pas encore terminée
        
    def get_legal_moves(self, row, col):
        square = chess.square(col, 7 - row)  # Inverser ligne pour correspondre au frontend
        moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                to_row = 7 - chess.square_rank(move.to_square)
                to_col = chess.square_file(move.to_square)
                moves.append({"row": to_row, "col": to_col})
        return moves