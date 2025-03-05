import { drawGame2d, drawGame3d } from "./drawPongGame.js";
import { resize3d, toggle3dButton } from "./game-buttons.js";
import { gameplay_socket, lobby_socket, initGameplaySocketTournament, closeGameplaySocket, customAlert } from "./globals.js";


export function startTournamentGame(lobby_id, game_id, player, roles, max_score, p1, p2, p3, p4, lobby_name)
{
  
  initGameplaySocketTournament(`/ws/gameplay/${max_score}/${lobby_id}/`, p1, p2, p3, p4, lobby_name);
    let gameSettings = {
        scoreBoard : document.getElementById('score'),
        canvas : document.getElementById('game-canvas'),
        contextType : '3d',
        paddle_width : 0,
        paddle_height : 0,
        ball_size : 0,
        player : player,
        screen_height_ratio : 0,
        max_score: max_score,
    };

    window.gameSettings = gameSettings;

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
    
    // Initialize 3D mode
    toggle3dButton();

    const encodeState = (player, direction, moving) => {
      const playerBit = (player == 'p1' ? 0 : 1);
      const directionBit = (direction == 'up' ? 1 : 0);
      const movingBit = (moving ? 1 : 0);
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
      document.addEventListener('keydown', handleKeyDown);
      document.addEventListener('keyup', handleKeyUp);
      document.querySelectorAll('.online').forEach(content => 
        {
          content.classList.remove('active');
        }
      );
      document.getElementById('game').classList.add('active');
      gameplay_socket.send(JSON.stringify({ type: 'player_joined' }));
    };

    gameplay_socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (movementVariables.hasOwnProperty(data.type))
        movementVariables[data.type] = data.status === 'true';
      else if (data.type == 'game_update')
        drawGame(data, gameSettings, roles, '2d');
      else if(data.type == 'game_init')
        initGameSettings(data, gameSettings);
      else if(data.type == 'player_left') {
        closeGameplaySocket();
        document.querySelectorAll('.online').forEach(content => 
          {
            content.classList.remove('active');
          }
        );
        document.getElementById('tournament').classList.add('active');
      }
      else if(data.type == 'game_end') {
        closeGameplaySocket();
        customAlert(data.message);
        document.querySelectorAll('.online').forEach(content => 
          {
            content.classList.remove('active');
          }
        );
        document.getElementById('tournament').classList.add('active');
        const message = {
        	action : 'game_end',
			    game: game_id,
			    winner : data.winner,
          };
        lobby_socket.send(JSON.stringify(message));
      }
    };

    // gameplay_socket.onerror = console.error;

    gameplay_socket.onclose = () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
      window.removeEventListener('resize', updateGameCanvas);
      window.removeEventListener('resize', resize3d);
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

  const paddleL = normalize(parseInt(data.paddleL), maxY, gameSettings.canvas.height);
  const paddleR = normalize(parseInt(data.paddleR), maxY, gameSettings.canvas.height);
  const ballX = normalize(parseInt(data.ball_x), maxX, gameSettings.canvas.width);
  const ballY = normalize(parseInt(data.ball_y), maxY, gameSettings.canvas.height);

  if (gameSettings.contextType == '2d')
    drawGame2d(gameSettings, paddleL, paddleR, ballX, ballY);
  else 
    drawGame3d(gameSettings, paddleL, paddleR, ballX, ballY, gameSettings.max_score);

  if (roles)
    gameSettings.scoreBoard.textContent = `P1 : ${roles.p1} : ${data.Lscore} | ${data.Rscore} : ${roles.p2} : P2`;
  else
    gameSettings.scoreBoard.textContent = `P1 : ${data.Lscore} | ${data.Rscore} : P2`;
}

