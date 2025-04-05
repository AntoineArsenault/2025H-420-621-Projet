// Sélectionner le canvas et son contexte
const canvas = document.getElementById("chessboard");
const ctx = canvas.getContext("2d");
const tileSize = 60;  // Taille des cases (60x60px)

// Cache pour les images des pièces afin d'éviter les rechargements répétés
const pieceImages = {};

// Fonction pour précharger les images des pièces
function preloadPieceImages() {
    const pieces = ['king-b', 'queen-b', 'rook-b', 'knight-b', 'bishop-b', 'pawn-b', 'king-w', 'queen-w', 'rook-w', 'knight-w', 'bishop-w', 'pawn-w'];
    
    pieces.forEach(piece => {
        const img = new Image();
        img.src = `static/assets/${piece}.svg`;  // Charger l'image en fonction du nom de la pièce
        pieceImages[piece] = img;  // Stocker l'image dans le cache
    });
}

// Fonction pour dessiner le plateau
function drawBoard(board) {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const x = col * tileSize;
            const y = row * tileSize;
            const isWhite = (row + col) % 2 === 0;  // Alternance des cases (blanches et noires)
            
            // Dessiner la case
            ctx.fillStyle = isWhite ? "#eee" : "#666";
            ctx.fillRect(x, y, tileSize, tileSize);
            
            // Dessiner la pièce si elle existe
            const piece = board[row][col];
            if (piece) {
                const image = pieceImages[piece];
                if (image) {
                    ctx.drawImage(image, x, y, tileSize, tileSize);  // Afficher l'image de la pièce
                }
            }
        }
    }
}

// Écouter l'événement de connexion Socket.IO
const socket = io.connect("http://127.0.0.1:5000");

// Lorsque la connexion est établie, demander l'état du plateau
socket.on('connect', () => {
    socket.emit('get_board');  // Demander l'état du plateau au backend
});

// Lorsqu'un nouvel état du plateau est reçu
socket.on('update_board', (board) => {
    drawBoard(board);  // Afficher le plateau avec les pièces
});

// Gérer les clics sur le plateau
canvas.addEventListener('click', function(event) {
    // Récupérer les coordonnées du clic dans le canvas
    const x = event.clientX - canvas.getBoundingClientRect().left;
    const y = event.clientY - canvas.getBoundingClientRect().top;

    // Calculer la ligne et la colonne en fonction du clic
    const col = Math.floor(x / tileSize);
    const row = Math.floor(y / tileSize);

    // Afficher les indices de la case cliquée dans la console
    console.log("Case cliquée : ", row, col);

    // Envoyer l'information de la case cliquée au serveur via Socket.IO
    socket.emit('piece_clicked', { row: row, col: col });
});

// Appeler la fonction pour précharger les images des pièces
preloadPieceImages();
