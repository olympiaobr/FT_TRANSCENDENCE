import { showLoginForm, showSignupForm, resetNavigation } from './dom-utils.js';
import { login, signup, logout } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/user-api/profile/', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
        });

        if (response.ok) {
            document.getElementById('login-button').style.display = 'none';
            document.getElementById('signup-button').style.display = 'none';
            document.getElementById('logout-button').style.display = 'inline-block';
            document.getElementById('profile-button').style.display = 'inline-block';
        } else {
            resetNavigation();
        }
    } catch (error) {
        console.error('Error checking authentication:', error);
    }

    // Event listeners for navigation buttons
    document.getElementById('login-button').addEventListener('click', showLoginForm);
    document.getElementById('signup-button').addEventListener('click', showSignupForm);
    document.getElementById('logout-button').addEventListener('click', logout);
    document.getElementById('profile-button').addEventListener('click', loadProfile);

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', login);
    }

    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', signup);
    }
});
