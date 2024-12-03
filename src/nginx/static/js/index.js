import { showLoginForm, showSignupForm, resetNavigation, loadProfile } from './dom-utils.js';
import { login, signup, logout } from './auth.js';

document.addEventListener('DOMContentLoaded', () => {
    resetNavigation(); // Set the initial state (Login and Signup visible)

    // Event listeners for navigation buttons
    document.getElementById('login-button').addEventListener('click', showLoginForm);
    document.getElementById('signup-button').addEventListener('click', showSignupForm);
    document.getElementById('logout-button').addEventListener('click', logout);
    document.getElementById('profile-button').addEventListener('click', loadProfile);
});
