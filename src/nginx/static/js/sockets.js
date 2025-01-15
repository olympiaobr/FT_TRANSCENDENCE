
export let lobby_socket;

export let gameplay_socket;

export function initLobbySocket(url)
{
    if (!lobby_socket)
        lobby_socket = new WebSocket(url);
    else
        console.warn("Lobby socket already initialized.");
}

export function initGameplaySocket(url)
{
    if (!gameplay_socket)
        gameplay_socket = new WebSocket(url);
    else
        console.warn("Lobby socket already initialized.");
}

export function closeGameplaySocket()
{
  if (gameplay_socket && gameplay_socket.readyState === WebSocket.OPEN) {
    gameplay_socket.close();
  }
  gameplay_socket = null;
}

export function closeSockets() {
    if (lobby_socket && lobby_socket.readyState === WebSocket.OPEN) {
      lobby_socket.close();
    }
    lobby_socket = null;
    closeGameplaySocket();
  }