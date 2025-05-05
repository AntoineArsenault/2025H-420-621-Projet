import chess  # Importe la bibliothèque python-chess, qui gère toute la logique des règles d’échecs

# Définition de la classe Game, qui représente une partie d’échecs
class Game:
    def __init__(self):
        # Initialise un nouvel objet Board, qui contient le plateau et les règles
        self.board = chess.Board()
        # Variable pour suivre à qui est le tour ('w' = blanc, 'b' = noir)
        self.current_turn = 'w'

    def start_game(self):
        # Redémarre une partie avec un nouveau plateau vide
        self.board = chess.Board()
        # Remet le tour au joueur blanc
        self.current_turn = 'w'

    def get_board(self):
        # Retourne le plateau actuel (objet chess.Board)
        return self.board

    def get_fen(self):
        # Retourne une chaîne de caractères (format FEN) représentant l'état du jeu
        return self.board.fen()

    def make_move(self, from_square, to_square):
        """Tente de faire un mouvement du point A au point B."""
        # Crée un objet "coup" (move) à partir des deux positions
        move = chess.Move(from_square, to_square)
        # Vérifie si ce coup est légal (selon les règles du jeu)
        if move in self.board.legal_moves:
            # Si oui, on applique le coup sur le plateau
            self.board.push(move)
            return True  # Le coup a été joué avec succès
        return False  # Le coup n'était pas autorisé

    def is_game_over(self):
        # Vérifie si la partie est terminée et renvoie la raison
        if self.board.is_checkmate():
            return "Échec et mat"  # Un roi est capturé
        elif self.board.is_stalemate():
            return "Pat"  # Aucun coup légal possible, mais pas d'échec
        elif self.board.is_insufficient_material():
            return "Matériel insuffisant"  # Pas assez de pièces pour mater
        elif self.board.is_seventyfive_moves():
            return "75 coups sans prise ni mouvement de pion"  # Règle des 75 coups
        elif self.board.is_fivefold_repetition():
            return "Répetition quintuple"  # Même position répétée 5 fois
        elif self.board.is_variant_draw():
            return "Partie nulle (variant)"  # Autres règles spécifiques
        else:
            return None  # La partie continue

    def get_legal_moves(self, row, col):
        # Convertit les coordonnées ligne-colonne du frontend en case unique du plateau
        square = chess.square(col, 7 - row)  # L’indexation est inversée entre Python (ligne 0 en haut) et l’affichage
        moves = []  # Liste des mouvements valides
        for move in self.board.legal_moves:
            if move.from_square == square:
                # Convertit la destination du coup en coordonnées ligne-colonne
                to_row = 7 - chess.square_rank(move.to_square)
                to_col = chess.square_file(move.to_square)
                # Ajoute ce coup à la liste
                moves.append({"row": to_row, "col": to_col})
        return moves  # Retourne tous les coups possibles à partir de la case choisie
