document.addEventListener('DOMContentLoaded', function() {
    loadCurrentUserData();

    const form = document.getElementById('update-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        updateUserData();
    });
});

function loadCurrentUserData() {
    fetch('/user-api/profile/', {
        method: 'GET',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('display-name').value = data.display_name || '';
        if (data.avatar) {
            document.getElementById('avatar-img').src = data.avatar;
        } else {
            document.getElementById('avatar-img').src = '/static/images/default_avatar.jpeg'; // Update to JPEG
        }
    })
    .catch(error => {
        console.error('Failed to load user data:', error);
    });
}


function updateUserData() {
    const formData = new FormData(document.getElementById('update-form'));
    fetch('/user-api/update-profile/', {
        method: 'POST',
        body: formData,
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to update profile');
        alert('Profile updated successfully!');
        window.location.href = 'profile.html';
    })
    .catch(error => {
        console.error('Error updating profile:', error);
        alert('Failed to update profile.');
    });
}
