import { showLoginForm, showSignupForm, resetNavigation, loadProfile } from './dom-utils.js';
import { logout } from './auth.js';

document.addEventListener('DOMContentLoaded', () => {
    resetNavigation();
    checkAuthentication();

    document.getElementById('login-button').addEventListener('click', showLoginForm);
    document.getElementById('signup-button').addEventListener('click', showSignupForm);
    document.getElementById('logout-button').addEventListener('click', logout);
    document.getElementById('profile-button').addEventListener('click', loadProfile);
});

async function checkAuthentication() {
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
            document.getElementById('login-button').style.display = 'inline-block';
            document.getElementById('signup-button').style.display = 'inline-block';
            document.getElementById('logout-button').style.display = 'none';
            document.getElementById('profile-button').style.display = 'none';
        }
    } catch (error) {
        console.error('Authentication check failed:', error);
    }
}
