// === Variables globales ===
const canvas = document.getElementById("chessboard");   // Récupère le canvas HTML pour l'échiquier
const ctx = canvas.getContext("2d");                    // Contexte de dessin 2D pour le canvas
const tileSize = 60;                                    // Taille d'une case en pixels
const pieceImages = {};                                 // Dictionnaire pour stocker les images des pièces
let selectedPiece = null;                               // Pièce sélectionnée par le joueur (ligne/colonne)
let boardState = { board: [], turn: "w" };              // État actuel du plateau et tour du joueur
let possibleMoves = [];                                 // Liste des mouvements possibles à afficher
let myColor = null;                                     // Couleur du joueur ("w" ou "b")
let myName = "";                                        // Nom du joueur
let playersInfo = { w: null, b: null };                 // Informations sur les joueurs blancs et noirs
let helpEnabled = true;                                 // Aide visuelle activée (cercles jaunes)
let contreIA = false;                                   // Indique si le joueur affronte l'IA
let pendingPromotion = null;                            // Promotion en attente (quand un pion atteint la fin)

const socket = io();                                    // Connexion WebSocket au serveur

// === Code qui s'exécute une fois le document HTML chargé ===
document.addEventListener('DOMContentLoaded', () => {

    // === Écran d'accueil ===
    document.getElementById("playIA").addEventListener("click", () => {
        myName = document.getElementById("inputName").value.trim() || "Anonyme";
        contreIA = true;
        const niveau = document.getElementById("selectLevel").value;
        lancerConnexion(niveau); // Connexion en mode IA
    });

    document.getElementById("playMulti").addEventListener("click", () => {
        myName = document.getElementById("inputName").value.trim() || "Anonyme";
        contreIA = false;
        lancerConnexion(); // Connexion multijoueur
    });

    function lancerConnexion(niveau = "moyen") {
        document.getElementById("welcomeScreen").style.display = "none"; // Cache l'écran d'accueil
        socket.emit("register_player", {
            nom: myName,
            mode: contreIA ? "ia" : "multi",
            niveau: contreIA ? niveau : undefined
        });
    }

    // === Réception des événements WebSocket du serveur ===
    socket.on('player_accepted', data => {
        myColor = data.couleur;
        socket.emit('get_board'); // Demande l’état du plateau
    });

    socket.on('spectator', data => {
        myColor = null;
        myName = "Spectateur";
        socket.emit('get_board');
    });

    socket.on('players_info', data => {
        playersInfo = data;
        updateGameInfo(); // Met à jour les infos des joueurs
    });

    socket.on('update_board', fen => {
        boardState = parseFEN(fen);          // Met à jour l'état du jeu (FEN → matrice)
        updateGameInfo();                    // Met à jour les infos d'affichage
        drawBoard(boardState.board);        // Redessine l’échiquier
    });

    socket.on('board_update', fen => {
        boardState = parseFEN(fen);
        updateGameInfo();
        drawBoard(boardState.board);
    });

    socket.on('illegal_move', data => {
        alert(data.message); // Message d'erreur en cas de coup illégal
    });

    socket.on('game_over', data => {
        alert("La partie est terminée : " + data.reason); // Message de fin de partie
    });

    socket.on('legal_moves', moves => {
        possibleMoves = moves;
        drawBoard(boardState.board); // Affiche les coups légaux
    });

    socket.on('chat_message', data => {
        const chatBox = document.getElementById('chatMessages');
        const msg = document.createElement('div');
        msg.innerHTML = `<strong>${data.nom} :</strong> ${data.text}`;
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    // === Contrôles boutons ===
    document.getElementById('restartButton').addEventListener('click', () => {
        if (confirm("Voulez-vous vraiment recommencer la partie ?")) {
            socket.emit('restart_game');
        }
    });

    document.getElementById("returnMenuButton").addEventListener("click", () => {
        if (confirm("Voulez-vous vraiment quitter la partie et revenir au menu ?")) {
            socket.emit('leave_game');

            // Réinitialise les données de jeu
            selectedPiece = null;
            boardState = { board: [], turn: "w" };
            myColor = null;
            myName = "";
            playersInfo = { w: null, b: null };

            document.getElementById("welcomeScreen").style.display = "flex";
        }
    });

    document.getElementById('toggleHelpSlider').addEventListener('change', (e) => {
        helpEnabled = e.target.checked;
        const label = document.getElementById('toggleHelpLabel');
        label.textContent = helpEnabled ? "Aide activée" : "Aide désactivée";
        drawBoard(boardState.board);
    });

    document.getElementById('sendChatBtn').addEventListener('click', () => {
        const message = document.getElementById('chatInput').value.trim();
        if (message) {
            socket.emit('chat_message', { nom: myName, text: message });
            document.getElementById('chatInput').value = '';
        }
    });

    // === Clic sur l’échiquier ===
    canvas.addEventListener('click', function(event) {
        const x = event.clientX - canvas.getBoundingClientRect().left;
        const y = event.clientY - canvas.getBoundingClientRect().top;
        const col = Math.floor(x / tileSize);
        const row = Math.floor(y / tileSize);
        const clickedPiece = boardState.board[row][col];

        if (!selectedPiece) {
            if (clickedPiece) {
                selectedPiece = { row, col };
                socket.emit('get_legal_moves', selectedPiece);
            }
        } else {
            const selectedPieceType = boardState.board[selectedPiece.row][selectedPiece.col];
            if (clickedPiece && isSameColor(clickedPiece, selectedPieceType)) {
                selectedPiece = { row, col };
                socket.emit('get_legal_moves', selectedPiece);
            } else {
                if (myColor !== boardState.turn) {
                    alert("Ce n’est pas votre tour !");
                    return;
                }

                const pieceType = boardState.board[selectedPiece.row][selectedPiece.col];
                const isPawn = pieceType && pieceType.startsWith('pawn');
                const isLastRow = (myColor === "w" && row === 0) || (myColor === "b" && row === 7);

                if (isPawn && isLastRow) {
                    pendingPromotion = { from: selectedPiece, to: { row, col } };
                    document.getElementById("promotionModal").style.display = "flex";
                } else {
                    socket.emit('move_piece', { from: selectedPiece, to: { row, col } });
                }

                selectedPiece = null;
                possibleMoves = [];
            }
        }
    });

    // === Choix de la pièce pour promotion ===
    document.querySelectorAll(".promotion-options button").forEach(button => {
        button.addEventListener("click", () => {
            const promotion = button.getAttribute("data-piece");
            if (pendingPromotion) {
                socket.emit("move_piece", {
                    from: pendingPromotion.from,
                    to: pendingPromotion.to,
                    promotion: promotion
                });
                pendingPromotion = null;
                document.getElementById("promotionModal").style.display = "none";   
            }
        });
    });

    preloadPieceImages(); // Charge les images des pièces à l’avance
});

// === Fonctions utilitaires ===

function updateGameInfo() {
    const playerNameDisplay = document.getElementById("playerName");
    const playerColorDisplay = document.getElementById("playerColor");
    const opponentNameDisplay = document.getElementById("opponentName");
    const currentTurnDisplay = document.getElementById("currentTurn");

    if (!myColor) {
        playerNameDisplay.textContent = "Mode spectateur";
        playerColorDisplay.textContent = "";
        opponentNameDisplay.textContent = "";
    } else {
        playerNameDisplay.textContent = "Nom : " + myName;
        playerColorDisplay.textContent = "Couleur : " + (myColor === "w" ? "Blanc" : "Noir");
        const opponentColor = myColor === "w" ? "b" : "w";
        const opponent = playersInfo[opponentColor];
        opponentNameDisplay.textContent = "Adversaire : " + (opponent || "En attente...");
    }

    currentTurnDisplay.textContent = "Tour : " + (boardState.turn === "w" ? "Blanc" : "Noir");
}

function isSameColor(piece1, piece2) {
    if (!piece1 || !piece2) return false;
    return piece1.slice(-1) === piece2.slice(-1); // Compare les suffixes "w" ou "b"
}

function highlightPossibleMoves() {
    if (!helpEnabled) return;
    possibleMoves.forEach(move => {
        const x = move.col * tileSize;
        const y = move.row * tileSize;
        ctx.fillStyle = "rgba(255, 255, 0, 0.5)";
        ctx.beginPath();
        ctx.arc(x + tileSize / 2, y + tileSize / 2, tileSize / 6, 0, 2 * Math.PI);
        ctx.fill();
    });
}

function preloadPieceImages() {
    const pieces = ['king-b', 'queen-b', 'rook-b', 'knight-b', 'bishop-b', 'pawn-b',
                    'king-w', 'queen-w', 'rook-w', 'knight-w', 'bishop-w', 'pawn-w'];
    pieces.forEach(piece => {
        const img = new Image();
        img.src = `static/assets/${piece}.svg`;
        pieceImages[piece] = img;
    });
}

function parseFEN(fen) {
    const [placement, turn] = fen.split(" ");
    const rows = placement.split("/");
    const board = [];
    const fenToImage = {
        p: "pawn-b", r: "rook-b", n: "knight-b", b: "bishop-b", q: "queen-b", k: "king-b",
        P: "pawn-w", R: "rook-w", N: "knight-w", B: "bishop-w", Q: "queen-w", K: "king-w"
    };
    for (let row of rows) {
        const boardRow = [];
        for (let char of row) {
            if (!isNaN(char)) {
                for (let i = 0; i < parseInt(char); i++) {
                    boardRow.push(null); // case vide
                }
            } else {
                boardRow.push(fenToImage[char]); // case avec une pièce
            }
        }
        board.push(boardRow);
    }
    return { board, turn };
}

function drawBoard(board) {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Nettoie le plateau

    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const x = col * tileSize;
            const y = row * tileSize;
            const isWhite = (row + col) % 2 === 0;
            ctx.fillStyle = isWhite ? "#dcdcdc" : "#568496";
            ctx.fillRect(x, y, tileSize, tileSize);

            const piece = board[row][col];
            if (piece && pieceImages[piece]) {
                ctx.drawImage(pieceImages[piece], x, y, tileSize, tileSize);
            }
        }
    }

    highlightPossibleMoves(); // Affiche les coups légaux (cercles jaunes)

    // Lettres A-H en haut
    ctx.fillStyle = "#333";
    ctx.font = "bold 14px Arial";
    const letters = "ABCDEFGH";
    for (let col = 0; col < 8; col++) {
        const letter = letters[col];
        ctx.fillText(letter, col * tileSize + tileSize / 2 - 5, 15);
    }

    // Chiffres 1-8 à gauche
    for (let row = 0; row < 8; row++) {
        const number = 8 - row;
        ctx.fillText(number, 5, row * tileSize + tileSize / 2 + 5);
    }
}
