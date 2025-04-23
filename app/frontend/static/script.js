const canvas = document.getElementById("chessboard");
const ctx = canvas.getContext("2d");
const tileSize = 60;
const pieceImages = {};
let selectedPiece = null;
let boardState = { board: [], turn: "w" };
let possibleMoves = [];
let myColor = null;
let myName = "";
let playersInfo = { w: null, b: null };
let helpEnabled = true;
let contreIA = false; // ❗ Variable pour le mode contre IA
let pendingPromotion = null; // ❗ Variable pour la promotion de pion

// === Fonctions d'information à l'écran ===
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
    return piece1.slice(-1) === piece2.slice(-1);
}

function highlightPossibleMoves() {
    if (!helpEnabled) return; // ❗ Ne rien afficher si l'aide est désactivée

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
                    boardRow.push(null);
                }
            } else {
                boardRow.push(fenToImage[char]);
            }
        }
        board.push(boardRow);
    }
    return { board, turn };
}

function drawBoard(board) {
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
    highlightPossibleMoves();
}

const socket = io();

document.addEventListener('DOMContentLoaded', () => {
    socket.on('connect', () => {
        // ❗ Affiche bien le prompt à la connexion
        const mode = prompt("Mode de jeu ? (ecrire 'ia' pour jouer contre l’IA, sinon entrer pour multijoueur)").toLowerCase();
        if (mode === "ia") {
            contreIA = true;
        }

        myName = prompt("Entrez votre nom :") || "Anonyme";

        socket.emit('register_player', {
            nom: myName,
            mode: contreIA ? "ia" : "multi"
        });
        console.log("Connexion socket établie ✅");
    });

    socket.on('player_accepted', data => {
        myColor = data.couleur;
        //document.getElementById("restartButton").style.display = "none";
        socket.emit('get_board');
    });

    socket.on('spectator', data => {
        myColor = null;
        myName = "Spectateur";
        socket.emit('get_board');
    });

    socket.on('players_info', data => {
        playersInfo = data;
        updateGameInfo();
    });

    socket.on('update_board', fen => {
        boardState = parseFEN(fen);
        updateGameInfo();
        drawBoard(boardState.board);
    });

    socket.on('board_update', fen => {
        boardState = parseFEN(fen);
        updateGameInfo();
        drawBoard(boardState.board);
    });

    socket.on('illegal_move', data => {
        alert(data.message);
    });

    socket.on('game_over', data => {
        alert("La partie est terminée : " + data.reason);
        //document.getElementById('restartButton').style.display = 'inline-block';
    });

    socket.on('legal_moves', moves => {
        possibleMoves = moves;
        drawBoard(boardState.board);
    });

    document.getElementById('restartButton').addEventListener('click', () => {
        if (confirm("Voulez-vous vraiment recommencer la partie ?")) {
            socket.emit('restart_game');
        }
    });  
    
    document.getElementById('toggleHelpSlider').addEventListener('change', (e) => {
        helpEnabled = e.target.checked;
    
        const label = document.getElementById('toggleHelpLabel');
        label.textContent = helpEnabled ? "Aide activée" : "Aide désactivée";
    
        drawBoard(boardState.board); // rafraîchir
    });

    document.getElementById('sendChatBtn').addEventListener('click', () => {
        const message = document.getElementById('chatInput').value.trim();
        if (message) {
            socket.emit('chat_message', { nom: myName, text: message });
            document.getElementById('chatInput').value = '';
        }
    });
    
    socket.on('chat_message', data => {
        const chatBox = document.getElementById('chatMessages');
        const msg = document.createElement('div');
        msg.innerHTML = `<strong>${data.nom} :</strong> ${data.text}`;
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight; // scroll auto
    });    

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
                // Vérifier si promotion possible (pion qui atteint dernière rangée)
                const pieceType = boardState.board[selectedPiece.row][selectedPiece.col];
                const isPawn = pieceType && pieceType.startsWith('pawn');
                const isLastRow = (myColor === "w" && row === 0) || (myColor === "b" && row === 7);

                if (isPawn && isLastRow) {
                    // Ouvrir le menu de promotion
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

    // Gestion de la promotion de pion
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

    preloadPieceImages();
});
