import { gameplay_socket, initGameplaySocket, closeGameplaySocket } from "./sockets.js";

export function startGame(lobby_id, player, player_count, roles)
{
    let gameSettings = {
        scoreBoard : document.getElementById('score'),
        canvas : document.getElementById('game-canvas'),
        paddle_width : 0,
        paddle_height : 0,
        ball_size : 0
    }

    document.querySelectorAll('.online').forEach(content => 
        {
          content.classList.remove('active');
        }
      );
    document.getElementById('game').classList.add('active');

    initGameplaySocket(`/ws/gameplay/${player_count}/${lobby_id}/`)
      
    const encodeState = (player, direction, moving) => {
      const playerBit = (player == 'p1' ? 0 : 1);
      const directionBit = (direction == 'up' ? 1 : 0);
      const movingBit = (moving ? 1 : 0);
      return ((playerBit << 2) | (directionBit << 1) | movingBit);
    }

    const handleKeyDown = (event) => {
      if (event.key === 'w')
        gameplay_socket.send(encodeState((player ? player : 'p1'), 'up', 1));
      else if (event.key === 's')
        gameplay_socket.send(encodeState((player ? player : 'p1'), 'down', 1));
      else if (event.key === 'ArrowUp')
        gameplay_socket.send(encodeState((player ? player : 'p2'), 'up', 1));
      else if (event.key === 'ArrowDown')
        gameplay_socket.send(encodeState((player ? player : 'p2'), 'down', 1));
    };

    const handleKeyUp = (event) => {
      if (event.key === 'w')
        gameplay_socket.send(encodeState((player ? player : 'p1'), 'up', 0));
      else if (event.key === 's')
        gameplay_socket.send(encodeState((player ? player : 'p1'), 'down', 0));
      else if (event.key === 'ArrowUp')
        gameplay_socket.send(encodeState((player ? player : 'p2'), 'up', 0));
      else if (event.key === 'ArrowDown')
        gameplay_socket.send(encodeState((player ? player : 'p2'), 'down', 0));
    };

    gameplay_socket.onopen = () => {
      console.log('Gameplay WebSocket open');
      document.addEventListener('keydown', handleKeyDown);
      document.addEventListener('keyup', handleKeyUp);
    };

    gameplay_socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type == 'game_update')
        drawGame(data, gameSettings.canvas, gameSettings.paddle_width, gameSettings.paddle_height, gameSettings.ball_size, gameSettings.scoreBoard, roles);
      else if(data.type == 'game_init')
        initGameSettings(data, gameSettings);
      else if(data.type == 'player_left') {
        closeGameplaySocket();
        console.log("player disconnected");
        document.querySelectorAll('.online').forEach(content => 
          {
            content.classList.remove('active');
          }
        );
        document.getElementById('lobby').classList.add('active');
        alert("Player disconnected - returning to lobby.");
      }
    };

    gameplay_socket.onerror = console.error;

    gameplay_socket.onclose = () => {
      console.log('Gameplay WebSocket closed');
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    }
}   

function initGameSettings(data, gameSettings)
{
    const canvas_container = document.getElementById('game');
    let container_height = canvas_container.clientHeight;
    let container_width = canvas_container.clientWidth;
    let screen_height_ratio = parseFloat(data.screen_height);
    if (container_height > container_width * screen_height_ratio)
    {
        gameSettings.canvas.width = container_width;
        gameSettings.canvas.height = container_width * screen_height_ratio;
    }
    else 
    {
        gameSettings.canvas.width = container_height / screen_height_ratio;
        gameSettings.canvas.height = container_height;
    }
    gameSettings.paddle_height = gameSettings.canvas.width * parseFloat(data.paddle_heigth);
    gameSettings.paddle_width = gameSettings.canvas.width * parseFloat(data.paddle_width);
    gameSettings.ball_size = gameSettings.canvas.width * parseFloat(data.ball_size);
}

function normalize(value, max, canvasSize)
{
   return((value / max) * canvasSize);
}

function drawGame(data, canvas, paddle_width, paddle_height, ball_size, scoreBoard, roles)
{
    const context = canvas.getContext('2d');
    const maxX = 1000;
    const maxY = 500;

    // const nonce = parseInt(data.nonce);
    const paddleL = normalize(parseInt(data.paddleL), maxY, canvas.height);
    const paddleR = normalize(parseInt(data.paddleR), maxY, canvas.height);
    const ballX = normalize(parseInt(data.ball_x), maxX, canvas.width);
    const ballY = normalize(parseInt(data.ball_y), maxY, canvas.height);

    context.clearRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = 'white';

    // draw paddles
    context.fillRect(0, paddleL, paddle_width, paddle_height);
    context.fillRect(canvas.width - paddle_width, paddleR, paddle_width, paddle_height);

    // draw ball
    context.beginPath();
    context.arc(ballX, ballY, ball_size / 2, 0, Math.PI * 2);
    context.fill();

    // Update score
    scoreBoard.textContent = `P1 : ${roles.p1} : ${data.Lscore} | ${data.Rscore} : ${roles.p2} : P2`;
}