let hostSocket;
let roomCode;
let hostEnv;

const lobbyContainer = document.getElementById('lobby-container');
const questionContainer = document.getElementById('question-container');
const playersList = document.getElementById('players-list');
const playerCount = document.getElementById('player-count');
const questionText = document.getElementById('question-text');
const startButton = document.getElementById('start-quiz-btn');

const hostAnswerA = document.getElementById('host-answer-a');
const hostAnswerB = document.getElementById('host-answer-b');
const hostAnswerC = document.getElementById('host-answer-c');
const hostAnswerD = document.getElementById('host-answer-d');

function initHostQuiz(initialHostEnv, initialRoomCode) {
    hostEnv = initialHostEnv;
    roomCode = initialRoomCode;
    
    hostSocket = new WebSocket(`ws://${hostEnv}/ws/quiz/${roomCode}/`);

    hostSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.type === 'players_update') {
            playersList.innerHTML = ''; 
            data.players.forEach(name => {
                const li = document.createElement('li');
                li.textContent = name;
                playersList.appendChild(li);
            });
            playerCount.textContent = data.players.length;
        }
        else if (data.type === 'new_question') {
            lobbyContainer.style.display = 'none';
            
            questionText.textContent = data.question;
            hostAnswerA.textContent = `${data.answers.A}`;
            hostAnswerB.textContent = `${data.answers.B}`;
            hostAnswerC.textContent = `${data.answers.C}`;
            hostAnswerD.textContent = `${data.answers.D}`;
            
            questionContainer.style.display = 'block';
            document.getElementById('host-answers-container').style.display = 'block';
        }
        else if (data.type === 'round_results') {
            questionText.textContent = 'Get ready for the next question...';
            document.getElementById('host-answers-container').style.display = 'none';
        }
        else if (data.type === 'quiz_end') {
            questionText.textContent = 'Quiz Over! Thanks for playing.';
            document.getElementById('host-answers-container').style.display = 'none';
        }
    };

    startButton.addEventListener('click', () => {
        if (hostSocket && hostSocket.readyState === WebSocket.OPEN) {
            hostSocket.send(JSON.stringify({'type': 'start_quiz'}));
            startButton.style.display = 'none';
        }
    });
}