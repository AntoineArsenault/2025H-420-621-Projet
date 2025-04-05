from .board import Board 

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'w'  # Par exemple, 'w' pour blanc, 'b' pour noir

    def start_game(self):
        # Logique pour démarrer une nouvelle partie
        pass
    
    def get_board(self):
        return self.board.board  # Retourne l'état actuel du plateau
