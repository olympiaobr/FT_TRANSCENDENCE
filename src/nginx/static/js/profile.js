import { getCSRFToken, logout} from './auth.js';

document.addEventListener('DOMContentLoaded', function() {
    fetchProfileData();
    document.getElementById('logout-button').addEventListener('click', logout);
    document.getElementById('settings-button').addEventListener('click', function() {
        window.location.href = 'update-profile.html';
    });
    document.getElementById('home-button').addEventListener('click', function() {
        window.location.href = 'index.html';
    });
    document.getElementById('change-avatar-btn').addEventListener('click', function() {
        document.getElementById('avatar-upload').click();
    });
    document.getElementById('avatar-upload').addEventListener('change', uploadAvatar);
    document.getElementById('add-friend-btn').addEventListener('click', addFriend);
});

function fetchProfileData() {
    fetch('/user-api/profile/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'include',
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch profile data');
        }
    })
    .then(data => {
        document.getElementById('username').textContent = data.user.username;
        document.getElementById('display-name').textContent = data.display_name;
        document.getElementById('wins').textContent = data.stats.wins;
        document.getElementById('losses').textContent = data.stats.losses;
        if (data.avatar) {
            document.getElementById('avatar').src = data.avatar;
        }
        updateFriendsList(data.friends);
        updateMatchHistory(data.match_history);
    })
    .catch(error => {
        console.error('Error fetching profile data:', error);
        alert('Error loading profile information.');
    });
}

function updateFriendsList(friends) {
    const friendsList = document.getElementById('friends');
    friendsList.innerHTML = '';
    friends.forEach(friend => {
        const li = document.createElement('li');
        li.textContent = `${friend.username} (${friend.online ? 'Online' : 'Offline'})`;
        friendsList.appendChild(li);
    });
}

function updateMatchHistory(matches) {
    const matchHistoryBody = document.getElementById('match-history-body');
    matchHistoryBody.innerHTML = '';
    matches.forEach(match => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(match.date).toLocaleDateString()}</td>
            <td>${match.opponent}</td>
            <td>${match.result}</td>
            <td>${match.score}</td>
        `;
        matchHistoryBody.appendChild(row);
    });
}

function uploadAvatar(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('avatar', file);

        fetch('/user-api/upload-avatar/', {
            method: 'POST',
            body: formData,
            credentials: 'include',
        })
        .then(response => response.json())
        .then(data => {
            if(data.message) {
                document.getElementById('avatar').src = window.URL.createObjectURL(file);
                alert('Avatar uploaded successfully!');
            } else {
                throw new Error(data.error || 'Failed to upload avatar');
            }
        })
        .catch(error => {
            console.error('Error uploading avatar:', error);
            alert(error.message);
        });
    }
}


function addFriend() {
    const friendUsername = document.getElementById('friend-username').value;
    if (friendUsername) {
        fetch('/user-api/add-friend/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ friend_username: friendUsername }),
            credentials: 'include',
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to add friend');
            }
        })
        .then(data => {
            alert('Friend added successfully!');
            fetchProfileData();
        })
        .catch(error => {
            console.error('Error adding friend:', error);
            alert('Failed to add friend.');
        });
    }
}
