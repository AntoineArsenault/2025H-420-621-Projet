# Importation des modules nécessaires
from flask_socketio import emit            # Pour envoyer des messages via WebSocket
from game.game import Game                 # On importe la classe Game (logique du jeu)
import chess                               # Librairie pour gérer les règles d’échecs
import chess.engine                        # Permet d’utiliser un moteur d’échecs comme Stockfish
from flask import request                  # Pour accéder à l'identité du joueur connecté
import random                              # (optionnel ici)
import eventlet                            # Nécessaire pour permettre les pauses et la gestion asynchrone

# Démarrer Stockfish (moteur d’échecs)
engine = chess.engine.SimpleEngine.popen_uci("../engine/stockfish.exe")  # ← à adapter selon ton projet

# Création d'une instance de jeu (plateau, état du jeu, etc.)
game = Game()

# Dictionnaire pour stocker les joueurs connectés et l'ordre de connexion
players = {}  # Clé = session ID, valeur = dict avec nom, couleur, etc.
order = []    # Liste pour garder l’ordre d’arrivée des joueurs

# 💡 Fonction IA : demande à Stockfish un coup selon le niveau choisi
def make_ai_move(board, niveau="moyen"):
    """Utilise Stockfish pour faire un coup selon la difficulté."""
    if niveau == "facile":
        limit = chess.engine.Limit(depth=4)  # réflexion très rapide
    elif niveau == "difficile":
        limit = chess.engine.Limit(depth=15)  # niveau fort
    else:
        limit = chess.engine.Limit(depth=8)  # par défaut, moyen

    result = engine.play(board, limit)  # Stockfish joue un coup selon l’état du plateau
    return result.move

# 💻 Fait jouer automatiquement l'IA si c’est son tour
def jouer_coup_ia(socketio):
    if game.board.turn == chess.BLACK:  # IA joue toujours avec les pièces noires
        # Récupérer les infos du joueur humain
        humain = next((p for sid, p in players.items() if p.get("contre_ia")), None)
        niveau = humain.get("niveau_ia", "moyen") if humain else "moyen"

        # Demander un coup à Stockfish
        move = make_ai_move(game.board, niveau)
        if move:
            game.board.push(move)  # Appliquer le coup
            socketio.emit('board_update', game.get_fen())  # Mise à jour du plateau côté client
            if game.is_game_over():  # Si la partie est terminée
                socketio.emit('game_over', {'reason': game.is_game_over()})

# 🔁 Envoie les noms des joueurs actuels à tous les clients
def send_players_info():
    emit('players_info', {
        'w': next((p['nom'] for p in players.values() if p['couleur'] == 'w'), None),
        'b': next((p['nom'] for p in players.values() if p['couleur'] == 'b'), None)
    }, broadcast=True)

# 🔌 Enregistre tous les événements WebSocket gérés par le serveur
def register_websocket_events(socketio):

    @socketio.on('get_board')
    def handle_get_board():
        """Envoie l'état actuel du plateau au client."""
        print("Envoi du plateau...")
        emit('update_board', game.get_fen())

    @socketio.on('move_piece')
    def handle_move_piece(data):
        """Gère le déplacement d’une pièce envoyé par un joueur."""
        # Transformation des coordonnées du client vers format interne (0 à 63)
        from_row = data['from']['row']
        from_col = data['from']['col']
        to_row = data['to']['row']
        to_col = data['to']['col']
        from_square = chess.square(from_col, 7 - from_row)
        to_square = chess.square(to_col, 7 - to_row)

        # Vérifie si le joueur demande une promotion (ex: pion en dame)
        promotion_code = data.get('promotion')
        promotion_piece = None
        if promotion_code:
            mapping = {
                'q': chess.QUEEN,
                'r': chess.ROOK,
                'b': chess.BISHOP,
                'n': chess.KNIGHT
            }
            promotion_piece = mapping.get(promotion_code)

        # Création du mouvement avec (ou sans) promotion
        move = chess.Move(from_square, to_square, promotion=promotion_piece)

        # Vérifie qui est ce joueur (via session WebSocket)
        joueur = players.get(request.sid)

        # ❌ Vérifie que c’est bien son tour (en mode multijoueur uniquement)
        if joueur and not joueur.get("contre_ia"):
            if (joueur["couleur"] == "w" and not game.board.turn) or (joueur["couleur"] == "b" and game.board.turn):
                emit('illegal_move', {'message': 'Ce n’est pas votre tour !'})
                return

        # ✅ Appliquer le coup s’il est valide
        if move in game.board.legal_moves:
            game.board.push(move)
            socketio.emit('board_update', game.get_fen())
            if game.is_game_over():
                socketio.emit('game_over', {'reason': game.is_game_over()})
        else:
            emit('illegal_move', {'message': 'Mouvement illégal!'})

        # Si on joue contre l’IA, c’est à elle de jouer ensuite
        if joueur and joueur.get("contre_ia"):
            jouer_coup_ia(socketio)

    @socketio.on('restart_game')
    def handle_restart_game():
        """Redémarre une nouvelle partie pour tous les joueurs."""
        game.start_game()
        emit('update_board', game.get_fen(), broadcast=True)

    @socketio.on('get_legal_moves')
    def handle_get_legal_moves(data):
        """Envoie tous les coups légaux possibles pour une pièce cliquée."""
        row = data['row']
        col = data['col']
        legal_moves = game.get_legal_moves(row, col)
        emit('legal_moves', legal_moves)

    @socketio.on('register_player')
    def handle_register(data):
        """Enregistre un joueur qui rejoint la partie (IA ou multi)."""
        nom = data['nom']
        mode = data.get('mode', 'multi')
        sid = request.sid
        niveau = data.get('niveau', 'moyen')

        if mode == "ia":
            # Le joueur joue contre l’ordinateur
            players[sid] = {"nom": nom, "couleur": "w", "contre_ia": True, "niveau_ia": niveau}
            order.append(sid)
            players["ia"] = {"nom": "IA", "couleur": "b"}
            emit('player_accepted', {'nom': nom, 'couleur': 'w'}, room=sid)
            send_players_info()
            print(f"{nom} joue contre l'IA.")

        elif len([sid for sid in order if sid in players]) < 2:
            # Deux joueurs maximum : on donne blanc ou noir selon disponibilité
            used_colors = [p["couleur"] for p in players.values() if not p.get("contre_ia")]
            couleur = 'w' if 'w' not in used_colors else 'b'
            players[sid] = {"nom": nom, "couleur": couleur, "contre_ia": False}
            order.append(sid)
            emit('player_accepted', {'nom': nom, 'couleur': couleur}, room=sid)
            print(f"{nom} a rejoint comme joueur {couleur}")
        else:
            # Les autres sont spectateurs
            emit('spectator', {'message': "Vous êtes spectateur."}, room=sid)
            print(f"{nom} a rejoint comme spectateur.")

        send_players_info()

    @socketio.on('disconnect')
    def handle_disconnect():
        """Déconnecte un joueur (fermeture du navigateur, perte réseau, etc.)."""
        sid = request.sid
        if sid in players:
            nom = players[sid]['nom']
            order.remove(sid)
            del players[sid]
            print(f"{nom} s'est déconnecté")
        if "ia" in players:
            del players["ia"]
        send_players_info()

    @socketio.on('leave_game')
    def handle_leave_game():
        """Quand un joueur quitte volontairement la partie."""
        sid = request.sid
        if sid in players:
            nom = players[sid]['nom']
            print(f"{nom} a quitté la partie volontairement.")
            order.remove(sid)
            del players[sid]
        if "ia" in players:
            del players["ia"]
        send_players_info()

    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Réception et diffusion d’un message de chat à tous les joueurs."""
        emit('chat_message', data, broadcast=True)
