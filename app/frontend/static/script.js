// === Variables globales ===
const canvas = document.getElementById("chessboard");
const ctx = canvas.getContext("2d");
const tileSize = 60;
const pieceImages = {};  // Doit être déclaré globalement
let selectedPiece = null; // Pour stocker la pièce sélectionnée
let boardState = []; // Pour stocker l'état du plateau
let possibleMoves = []; // Pour stocker les mouvements possibles

// === Ajuster la taille du canvas ===
function highlightPossibleMoves() {
    possibleMoves.forEach(move => {
        const x = move.col * tileSize;
        const y = move.row * tileSize;
        ctx.fillStyle = "rgba(255, 255, 0, 0.5)";  // Jaune semi-transparent
        ctx.beginPath();
        ctx.arc(x + tileSize / 2, y + tileSize / 2, tileSize / 6, 0, 2 * Math.PI);
        ctx.fill();
    });
}

// === Précharger les images des pièces ===
function preloadPieceImages() {
    const pieces = ['king-b', 'queen-b', 'rook-b', 'knight-b', 'bishop-b', 'pawn-b',
                    'king-w', 'queen-w', 'rook-w', 'knight-w', 'bishop-w', 'pawn-w'];

    pieces.forEach(piece => {
        const img = new Image();
        img.src = `static/assets/${piece}.svg`;
        pieceImages[piece] = img;
    });
}

// === Convertir FEN -> tableau 2D compatible drawBoard ===
function parseFEN(fen) {
    const rows = fen.split(" ")[0].split("/");
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
                    boardRow.push(null);
                }
            } else {
                boardRow.push(fenToImage[char]);
            }
        }
        board.push(boardRow);
    }

    return board;
}

// === Dessiner le plateau et les pièces ===
function drawBoard(board) {
    boardState = board; // Mettre à jour l'état du plateau

    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const x = col * tileSize;
            const y = row * tileSize;
            const isWhite = (row + col) % 2 === 0;
            
            ctx.fillStyle = isWhite ? "#dcdcdc" : "#568496";
            ctx.fillRect(x, y, tileSize, tileSize);

            // Vérification si une pièce existe à cette position
            const piece = boardState[row] && boardState[row][col];
            if (piece) {
                const image = pieceImages[piece];
                if (image) {
                    ctx.drawImage(image, x, y, tileSize, tileSize);
                }
            }
        }
    }
    // Surligner les coups possibles après avoir dessiné
    highlightPossibleMoves();
}

// === Socket.IO ===
const socket = io.connect("http://127.0.0.1:5000");

// Lorsque le DOM est complètement chargé
document.addEventListener('DOMContentLoaded', () => {
    // Écouter l'événement de fin de partie
    socket.on('game_over', (data) => {
        alert("La partie est terminée : " + data.reason);  // Afficher la raison de la fin de la partie
        document.getElementById('restartButton').style.display = 'inline-block';  // Afficher le bouton de redémarrage
    });

    // Ajouter un gestionnaire d'événements pour recommencer la partie
    const restartButton = document.getElementById('restartButton');
    if (restartButton) {
        restartButton.addEventListener('click', () => {
            socket.emit('restart_game');  // Envoyer un événement au backend pour recommencer la partie
            restartButton.style.display = 'none';  // Masquer le bouton de redémarrage
        });
    }

    // === Autres codes de Socket.IO ===
    socket.on('connect', () => {
        socket.emit('get_board');
    });

    socket.on('update_board', (fen) => {
        const board = parseFEN(fen);
        drawBoard(board);
    });

    // === Gestion des clics ===
    canvas.addEventListener('click', function(event) {
        const x = event.clientX - canvas.getBoundingClientRect().left;
        const y = event.clientY - canvas.getBoundingClientRect().top;
        const col = Math.floor(x / tileSize);
        const row = Math.floor(y / tileSize);

        if (!selectedPiece) {
            // Premier clic : Sélectionner une pièce
            const piece = boardState[row][col];
            if (piece) {
                selectedPiece = { row, col };  // Enregistrer la case de la pièce sélectionnée
                console.log("Pièce sélectionnée : ", piece, " à la position : ", row, col);
                socket.emit('get_legal_moves', selectedPiece);  // Demande au backend
            }
        } else {
            // Deuxième clic : Déplacer la pièce
            console.log("Déplacement de la pièce : ", boardState[selectedPiece.row][selectedPiece.col]);
            console.log("Vers la case : ", row, col);

            // Ici, nous allons envoyer l'information au serveur pour mettre à jour le plateau
            socket.emit('move_piece', { from: selectedPiece, to: { row, col } });

            // Réinitialiser la sélection
            selectedPiece = null;
            possibleMoves = [];  // Réinitialiser les mouvements possibles
        }
    });

    // === Réception des réponses du serveur ===
    socket.on('illegal_move', (data) => {
        // Afficher un message d'erreur si le mouvement est invalide
        alert(data.message);
    });

    socket.on('legal_moves', (moves) => {
        possibleMoves = moves;
        drawBoard(boardState);  // Redessine pour afficher les highlights
    });

    socket.on('board_update', (fen) => {
        // Mettre à jour le plateau si le mouvement est valide
        const board = parseFEN(fen);
        drawBoard(board);
    });

    // === Appeler la fonction de préchargement ===
    preloadPieceImages();
});