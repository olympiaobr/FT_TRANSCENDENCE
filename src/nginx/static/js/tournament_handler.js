import { lobby_socket, name, initLobbySocket } from "./globals.js";
import { lobbyFull } from "./lobby-creation.js";


export function joinLocalTournament(lobby_id, lobby_name, max_score)
{
    alert("no join tournament yet ");
}

export function joinTournament(lobby_id, lobby_name, max_score)
{
    lobbyFull(lobby_id).then(is_full => {
        if (is_full) {
          alert('Lobby is full. Cannot join.');
          return;
        }
    })

    initLobbySocket(`/ws/lobby/tournament/${lobby_id}/${name}/`)

    const playerContainer = document.getElementById('player-container');
    const tournamentContainer = document.getElementById('tournament-container');
    const playersHeader = document.getElementById('players-header');
    const tournamentHeader = document.getElementById('tournament-header');
    const tournamentDiv = document.getElementById('tournament');
    const tournamentPrep = document.getElementById('tournament-prep');


    lobby_socket.onopen = () => {
        console.log("Tournament lobby connected");
        tournamentHeader.textContent = `Tournament: ${lobby_name}`;
        lobby_socket.send(JSON.stringify({
            action: 'player_joined',
          })
        );
        document.querySelectorAll('.online').forEach(content => 
          {
            content.classList.remove('active');
          }
        );
        tournamentDiv.classList.add('active')
    }

    lobby_socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log(data);
        if (data.type == 'player_joined')
        {
          Object.keys(data.player_names).forEach((name) => {
              const button = document.createElement('button');
              button.classList.add('player_button');
              button.textContent = name;
              playerContainer.appendChild(button);
          });
        }
        else if (data.type === 'enable_start_button')
        {
            enableStartButton();
        }
        else if (data.type === 'disable_start_button')
        {
            disableStartButton();
        }
        else if (data.type == 'start_tournament')
        {
          playersHeader.classList.add('disable');
          playerContainer.classList.add('disable');
          tournamentContainer.classList.remove('disable');
          tournamentPrep.classList.add('disable');
        }
    }
} 

function enableStartButton() {
  console.log("enabling start tournament");
  const start_button = document.getElementById('start_tournament');
  if (start_button) {
    start_button.replaceWith(start_button.cloneNode(true));
    const new_start_button = document.getElementById('start_tournament');
    new_start_button.classList.add('start_enabled');
    new_start_button.addEventListener('click', () => sendStartGame())
  }
}

function disableStartButton() {
  const start_button = document.getElementById('start_tournament');
  start_button.classList.remove('start_enabled');
  start_button.onclick = null;
}
function sendStartGame()
{
  const message = {
    action: `start_tournament`
    };
    lobby_socket.send(JSON.stringify(message));
}
