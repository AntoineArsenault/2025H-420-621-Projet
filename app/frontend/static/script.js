// === Variables globales ===
const canvas = document.getElementById("chessboard");
const ctx = canvas.getContext("2d");
const tileSize = 60;
const pieceImages = {};  // Doit être déclaré globalement
let selectedPiece = null; // Pour stocker la pièce sélectionnée
let boardState = []; // Pour stocker l'état du plateau

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

// === Convertit FEN -> tableau 2D compatible drawBoard ===
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
            
            ctx.fillStyle = isWhite ? "#eee" : "#666";
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
}


// === Socket.IO ===
const socket = io.connect("http://127.0.0.1:5000");

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
        }
    } else {
        // Deuxième clic : Déplacer la pièce
        console.log("Déplacement de la pièce : ", boardState[selectedPiece.row][selectedPiece.col]);
        console.log("Vers la case : ", row, col);

        // Ici, nous allons envoyer l'information au serveur pour mettre à jour le plateau
        socket.emit('move_piece', { from: selectedPiece, to: { row, col } });

        // Réinitialiser la sélection
        selectedPiece = null;
    }
});

// === Appeler la fonction de préchargement ===
preloadPieceImages();
