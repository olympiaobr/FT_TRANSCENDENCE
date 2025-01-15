import { closeSockets } from "./sockets.js";

document.querySelectorAll('.game-tab').forEach(tab => 
  {
  tab.addEventListener('click', generateTab);
  }
);

// functions
function generateTab() 
{
  document.querySelectorAll('.game-tab').forEach(t => t.classList.remove('active'));
  this.classList.add('active');
  const tabName = this.id.replace('-tab', '');
  document.querySelectorAll('.game-selector').forEach(content => 
    {
      content.classList.remove('active');
    }
  );
  document.getElementById(tabName).classList.add('active');
  document.querySelectorAll('.online').forEach(content => 
    {
      content.classList.remove('active');
    }
  );
  document.getElementById('option-choose').classList.add('active');
  closeSockets();
}

