document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('http://127.0.0.1:8000/user-api/profile/', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
        });

        if (response.ok) {
            const profileData = await response.json();
            document.getElementById('username').textContent = profileData.user.username;
            document.getElementById('profile-username').textContent = profileData.user.username;
            document.getElementById('profile-display-name').textContent = profileData.display_name;
        } else {
            alert('Unauthorized. Please log in.');
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
