let roomCode;
let playerName;
let host;
let socket;

const welcomeText = document.getElementById('welcome-text');
const statusText = document.getElementById('status-text');
const answersContainer = document.getElementById('answers-container');
let answerButtons;

function initQuiz(initHost, Code, name) {
    host = initHost;
    roomCode = Code;
    playerName = name;

    socket = new WebSocket(`ws://${host}/ws/quiz/${roomCode}/`);

    answerButtons = answersContainer.getElementsByClassName('answer-btn');

    socket.onopen = () => {
        console.log("✅ Player connected!");
        socket.send(JSON.stringify({ 'type': 'join', 'name': playerName }));
    };

    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log("Player received:", data);

        if (data.type === 'new_question') {
            document.body.style.backgroundColor = 'white';
            welcomeText.style.display = 'none';
            statusText.textContent = 'Choose your answer now!';
            answersContainer.style.display = 'block';

            for (let btn of answerButtons) {
                btn.disabled = false;
            }
        }
        else if (data.type === 'round_results') {
            const myResult = data.results[playerName];
            console.log("My result:", myResult);
            if (myResult === true) {
                statusText.textContent = 'Correct!';
                document.body.style.backgroundColor = 'lightgreen';
            } else {
                statusText.textContent = 'Incorrect!';
                document.body.style.backgroundColor = 'lightcoral';
            }
        }
        else if (data.type === 'quiz_end') {
            setTimeout(() => {
                document.body.style.backgroundColor = 'white';
                statusText.textContent = 'The quiz has ended. Thank you for playing!';
                answersContainer.style.display = 'none';
            }, 3000);
        }
    };
}

function sendAnswer(answer) {
    console.log(`Sending answer: ${answer}`);
    socket.send(JSON.stringify({'type': 'answer', 'answer': answer}));

    answersContainer.style.display = 'none'; 

    statusText.textContent = 'Answer sent! Waiting for the next question...';
}