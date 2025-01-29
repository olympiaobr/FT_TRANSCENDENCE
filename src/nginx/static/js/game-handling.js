import { getCSRFToken } from "./auth.js";
import { gameplay_socket, initGameplaySocket, closeGameplaySocket } from "./globals.js";

export function startGame(lobby_id, player, player_count, roles, max_score)
{
    let gameSettings = {
        scoreBoard : document.getElementById('score'),
        canvas : document.getElementById('game-canvas'),
        contextType : '2d',
        paddle_width : 0,
        paddle_height : 0,
        ball_size : 0,
        player : player,
        screen_height_ratio : 0
    };

    let movementVariables = {
      left_top: false,
      left_down: false,
      right_top: false,
      right_down: false,
      mid_top: false,
      mid_down: false,
      mid_left: false,
      mid_right: false
    };

    document.querySelectorAll('.online').forEach(content => 
        {
          content.classList.remove('active');
        }
      );
    document.getElementById('game').classList.add('active');

    const twoD = document.getElementById('2d');
    const threeD = document.getElementById('3d');

    twoD.addEventListener('click', 
      () => {
      gameSettings.contextType = '2d';
      threeD.classList.remove('active');
      twoD.classList.add('active');
      console.log('2d selected');
      console.log(gameSettings);
    });

    threeD.addEventListener('click', 
      () => {
      gameSettings.contextType = '3d';
      twoD.classList.remove('active');
      threeD.classList.add('active');
      console.log('3d selected');
      console.log(gameSettings);
    });

    const csrfToken = getCSRFToken();

    if (player_count == 1)
      initGameplaySocket(`/ws/gameplay/local/${max_score}/${lobby_id}/`);
    else
    initGameplaySocket(`/ws/gameplay/${max_score}/${lobby_id}/`);

    const encodeState = (player, direction, moving) => {
      const playerBit = (player == 'p1' ? 0 : 1);
      const directionBit = (direction == 'up' ? 1 : 0);
      const movingBit = (moving ? 1 : 0);
      console.log(((playerBit << 2) | (directionBit << 1) | movingBit));
      return ((playerBit << 2) | (directionBit << 1) | movingBit);
    };

    const handleKeyDown = (event) => {
      let keycode = event.code;
        if (keycode === 'KeyW' && (((!player || player == 'p1') && !movementVariables.left_top) || (player == 'p2' && !movementVariables.right_top)))
          gameplay_socket.send(encodeState((player ? player : 'p1'), 'up', 1));
        else if (keycode === 'KeyS' && (((!player || player == 'p1') && !movementVariables.left_down) || (player == 'p2' && !movementVariables.right_down)))
          gameplay_socket.send(encodeState((player ? player : 'p1'), 'down', 1));
        else if (keycode === 'ArrowUp'  && (((!player || player == 'p2') && !movementVariables.right_top) || (player == 'p1' && !movementVariables.left_top)))
        {
          event.preventDefault();
          gameplay_socket.send(encodeState((player ? player : 'p2'), 'up', 1));
        }
        else if (keycode === 'ArrowDown'  && (((!player || player == 'p2') && !movementVariables.right_down) || (player == 'p1' && !movementVariables.left_down)))
        {
          event.preventDefault();
          gameplay_socket.send(encodeState((player ? player : 'p2'), 'down', 1));
        }
    };

    const handleKeyUp = (event) => {
      let keycode = event.code;
        if (keycode === 'KeyW')
          gameplay_socket.send(encodeState((player ? player : 'p1'), 'up', 0));
        if (keycode === 'KeyS')
          gameplay_socket.send(encodeState((player ? player : 'p1'), 'down', 0));
        if (keycode === 'ArrowUp')
          gameplay_socket.send(encodeState((player ? player : 'p2'), 'up', 0));
        if (keycode === 'ArrowDown')
          gameplay_socket.send(encodeState((player ? player : 'p2'), 'down', 0));
    };

    gameplay_socket.onopen = () => {
      console.log('Gameplay WebSocket open');
      document.addEventListener('keydown', handleKeyDown);
      document.addEventListener('keyup', handleKeyUp);
      gameplay_socket.send(JSON.stringify({
        type: 'player_joined',
      }))
    };

    gameplay_socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data.type);
      if (movementVariables.hasOwnProperty(data.type))
        movementVariables[data.type] = data.status === 'true';
      else if (data.type == 'game_update')
        drawGame(data, gameSettings, roles, '2d');
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
      else if(data.type == 'game_end') {
        console.log("game ending...");
        closeGameplaySocket();
        document.querySelectorAll('.online').forEach(content => 
          {
            content.classList.remove('active');
          }
        );
        alert(data.message);
        document.getElementById('lobby').classList.add('active');
      }
    };

    gameplay_socket.onerror = console.error;

    gameplay_socket.onclose = () => {
      console.log('Gameplay WebSocket closed');
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };

    window.addEventListener('resize', () => {
      updateGameCanvas(gameSettings);
  });
}   

function updateGameCanvas(gameSettings) {
  const canvas_container = document.getElementById('game');
  let container_height = canvas_container.clientHeight;
  let container_width = canvas_container.clientWidth;
  if (container_height > container_width * gameSettings.screen_height_ratio)
    {
        gameSettings.canvas.width = container_width;
        gameSettings.canvas.height = container_width * gameSettings.screen_height_ratio;
    }
    else 
    {
        gameSettings.canvas.width = container_height / gameSettings.screen_height_ratio;
        gameSettings.canvas.height = container_height;
    }
}

function initGameSettings(data, gameSettings)
{
    const canvas_container = document.getElementById('game');
    let container_height = canvas_container.clientHeight;
    let container_width = canvas_container.clientWidth;
    gameSettings.screen_height_ratio = parseFloat(data.screen_height);
    if (container_height > container_width * gameSettings.screen_height_ratio)
    {
        gameSettings.canvas.width = container_width;
        gameSettings.canvas.height = container_width * gameSettings.screen_height_ratio;
    }
    else 
    {
        gameSettings.canvas.width = container_height / gameSettings.screen_height_ratio;
        gameSettings.canvas.height = container_height;
    }
    gameSettings.paddle_height = gameSettings.canvas.width * parseFloat(data.paddle_height);
    gameSettings.paddle_width = gameSettings.canvas.width * parseFloat(data.paddle_width);
    gameSettings.ball_size = gameSettings.canvas.width * parseFloat(data.ball_size);
}

function normalize(value, max, canvasSize)
{
   return((value / max) * canvasSize);
}

function drawGame(data, gameSettings, roles)
{
  const maxX = 1000;
  const maxY = 500;

  // const nonce = parseInt(data.nonce);
  const paddleL = normalize(parseInt(data.paddleL), maxY, gameSettings.canvas.height);
  const paddleR = normalize(parseInt(data.paddleR), maxY, gameSettings.canvas.height);
  const ballX = normalize(parseInt(data.ball_x), maxX, gameSettings.canvas.width);
  const ballY = normalize(parseInt(data.ball_y), maxY, gameSettings.canvas.height);

// right now i was thinking to toggle the drawing mode from 2d to 3d
// but if you use three.js, we could also just switch the camera position and have it one.

//and dont wonder, i set both (if else) to drawGame2d right now, since drawGame3d is not implemented yet.
  if (gameSettings.contextType == '2d')
    drawGame2d(gameSettings, paddleL, paddleR, ballX, ballY);
  else 
    drawGame3d(gameSettings, paddleL, paddleR, ballX, ballY);

  // Update score
  if (roles)
    gameSettings.scoreBoard.textContent = `P1 : ${roles.p1} : ${data.Lscore} | ${data.Rscore} : ${roles.p2} : P2`;
  else
    gameSettings.scoreBoard.textContent = `P1 : ${data.Lscore} | ${data.Rscore} : P2`;
}

function drawGame2d(gameSettings, paddleL, paddleR, ballX, ballY)
{
  const context = gameSettings.canvas.getContext(gameSettings.contextType);
  context.clearRect(0, 0, gameSettings.canvas.width, gameSettings.canvas.height);
  context.fillStyle = 'white';

  // draw paddles
  context.fillRect(0, paddleL, gameSettings.paddle_width, gameSettings.paddle_height);
  context.fillRect(gameSettings.canvas.width - gameSettings.paddle_width, paddleR, gameSettings.paddle_width, gameSettings.paddle_height);

  // draw ball
  context.beginPath();
  context.arc(ballX, ballY, gameSettings.ball_size / 2, 0, Math.PI * 2);
  context.fill();

}


function drawGame3d(gameSettings, paddleL, paddleR, ballX, ballY)
{

/* gameSettings.scoreBoard <-- gets updated in drawGame already
gameSettings.canvas <-- canvas element 
gameSettings.contextType <-- updates when the player clicks on 3d or 2d to toggle mode 
gameSettings.paddle_width 
gameSettings.paddle_height
gameSettings.ball_size
gameSettings.player <- says if the player is 'p1' or 'p2' we can adjust the camera depending on it.  

paddleL <- y position of paddleL (x is as left as possible) aka 0 
paddleR <- y position of paddleR (x is as right as possible) aka gameSettings.canvas.width - gameSettings.paddle_width
ballX
ballY
*/
}