import { loadProfile, resetNavigation, showLoginForm } from './dom-utils.js';

export async function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/user-api/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            alert('Login successful!');
            document.getElementById('login-button').style.display = 'none';
            document.getElementById('signup-button').style.display = 'none';
            document.getElementById('logout-button').style.display = 'inline-block';
            document.getElementById('profile-button').style.display = 'inline-block';
            loadProfile(); // Load profile data dynamically
        } else {
            const errorData = await response.json();
            alert(errorData.error || 'Login failed');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

export async function signup(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/user-api/signup/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            alert('Signup successful! Please log in.');
            showLoginForm();
        } else {
            const errorData = await response.json();
            alert(errorData.error || 'Signup failed');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

export async function logout() {
    try {
        const response = await fetch('/user-api/logout/', {
            method: 'POST',
            credentials: 'include',
        });

        if (response.ok) {
            alert('Logged out successfully!');
            resetNavigation(); // Reset to initial state
        } else {
            alert('Error logging out.');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

