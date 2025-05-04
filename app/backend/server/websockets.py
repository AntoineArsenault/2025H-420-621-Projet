from flask_socketio import emit
from game.game import Game
import chess
import chess.engine
from flask import request
import random
import eventlet

# Démarrer Stockfish
engine = chess.engine.SimpleEngine.popen_uci("../engine/stockfish.exe")  # ← adapte le chemin selon où tu as mis Stockfish

game = Game()

players = {}
order = []

def make_ai_move(board, niveau="moyen"):
    """Utilise Stockfish pour faire un coup selon la difficulté."""
    if niveau == "facile":
        limit = chess.engine.Limit(depth=4)  # rapide et peu profond
    elif niveau == "difficile":
        limit = chess.engine.Limit(depth=15)  # réflexion plus poussée
    else:
        limit = chess.engine.Limit(depth=8)  # niveau moyen par défaut

    result = engine.play(board, limit)
    return result.move

def jouer_coup_ia(socketio):
    if game.board.turn == chess.BLACK:
        eventlet.sleep(0.5)
        # 🧠 Récupérer le joueur humain
        humain = next((p for sid, p in players.items() if p.get("contre_ia")), None)
        niveau = humain.get("niveau_ia", "moyen") if humain else "moyen"

        move = make_ai_move(game.board, niveau)
        if move:
            game.board.push(move)
            socketio.emit('board_update', game.get_fen())
            if game.is_game_over():
                socketio.emit('game_over', {'reason': game.is_game_over()})

def send_players_info():
    emit('players_info', {
        'w': next((p['nom'] for p in players.values() if p['couleur'] == 'w'), None),
        'b': next((p['nom'] for p in players.values() if p['couleur'] == 'b'), None)
    }, broadcast=True)

def register_websocket_events(socketio):
    @socketio.on('get_board')
    def handle_get_board():
        print("Envoi du plateau...")
        emit('update_board', game.get_fen())

    @socketio.on('move_piece')
    @socketio.on('move_piece')
    def handle_move_piece(data):
        from_row = data['from']['row']
        from_col = data['from']['col']
        to_row = data['to']['row']
        to_col = data['to']['col']
        from_square = chess.square(from_col, 7 - from_row)
        to_square = chess.square(to_col, 7 - to_row)

        # Vérifier s’il y a une promotion demandée depuis le client
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

        # Construire le coup (avec ou sans promotion)
        move = chess.Move(from_square, to_square, promotion=promotion_piece)

        # Obtenir l'identité du joueur
        joueur = players.get(request.sid)

        # 🔒 Empêcher de jouer si ce n’est pas son tour (en multijoueur)
        if joueur and not joueur.get("contre_ia"):  # Seulement si on n’est PAS en mode IA
            if (joueur["couleur"] == "w" and not game.board.turn) or (joueur["couleur"] == "b" and game.board.turn):
                emit('illegal_move', {'message': 'Ce n’est pas votre tour !'})
                return

        if move in game.board.legal_moves:
            game.board.push(move)
            socketio.emit('board_update', game.get_fen())

            if game.is_game_over():
                socketio.emit('game_over', {'reason': game.is_game_over()})
        else:
            emit('illegal_move', {'message': 'Mouvement illégal!'})

        # Si on est en mode IA, faire jouer l'IA après le coup du joueur
        if joueur and joueur.get("contre_ia"):
            jouer_coup_ia(socketio)



    @socketio.on('restart_game')
    def handle_restart_game():
        game.start_game()
        emit('update_board', game.get_fen(), broadcast=True)

    @socketio.on('get_legal_moves')
    def handle_get_legal_moves(data):
        row = data['row']
        col = data['col']
        legal_moves = game.get_legal_moves(row, col)
        emit('legal_moves', legal_moves)

    @socketio.on('register_player')
    def handle_register(data):
        nom = data['nom']
        mode = data.get('mode', 'multi')
        sid = request.sid
        niveau = data.get('niveau', 'moyen')

        if mode == "ia":
            # Mode IA : le joueur est blanc, l’IA est noire
            players[sid] = {"nom": nom, "couleur": "w", "contre_ia": True, "niveau_ia": niveau}
            order.append(sid)
            players["ia"] = {"nom": "IA", "couleur": "b"}
            emit('player_accepted', {'nom': nom, 'couleur': 'w'}, room=sid)
            send_players_info()
            print(f"{nom} joue contre l'IA.")

        elif len([sid for sid in order if sid in players]) < 2:
            used_colors = [p["couleur"] for p in players.values() if not p.get("contre_ia")]
            couleur = 'w' if 'w' not in used_colors else 'b'
            players[sid] = {"nom": nom, "couleur": couleur, "contre_ia": False}
            order.append(sid)
            emit('player_accepted', {'nom': nom, 'couleur': couleur}, room=sid)
            print(f"{nom} a rejoint comme joueur {couleur}")
        else:
            emit('spectator', {'message': "Vous êtes spectateur."}, room=sid)
            print(f"{nom} a rejoint comme spectateur.")

        send_players_info()

    @socketio.on('disconnect')
    def handle_disconnect():
        sid = request.sid
        if sid in players:
            nom = players[sid]['nom']
            order.remove(sid)
            del players[sid]
            print(f"{nom} s'est déconnecté")
        if "ia" in players:
            del players["ia"]
        send_players_info()  # mise à jour des noms

    @socketio.on('leave_game')
    def handle_leave_game():
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
        emit('chat_message', data, broadcast=True)
