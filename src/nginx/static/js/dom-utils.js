import { login, signup } from './auth.js';

export async function loadProfile() {
    try {
        const response = await fetch('/user-api/profile/', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
        });

        if (response.ok) {
            window.location.href = '/profile.html';
        } else if (response.status === 401) {
            alert('Unauthorized. Please log in.');
            showLoginForm();
        } else {
            console.error('Unexpected error:', response.status);
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

export function showLoginForm() {
    const mainContent = document.querySelector('body');
    mainContent.innerHTML = `
        <h1>Login</h1>
        <form id="login-form">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Log In</button>
        </form>
        <p>Don't have an account? <button id="signup-link">Sign Up</button></p>
    `;

    document.getElementById('signup-link').addEventListener('click', showSignupForm);
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', login);
}

export function showSignupForm() {
    const mainContent = document.querySelector('body');
    mainContent.innerHTML = `
        <h1>Sign Up</h1>
        <form id="signup-form">
            <input type="text" name="username" placeholder="Username" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign Up</button>
        </form>
        <p>Already have an account? <button id="login-link">Log In</button></p>
    `;

    document.getElementById('login-link').addEventListener('click', showLoginForm);
    const signupForm = document.getElementById('signup-form');
    signupForm.addEventListener('submit', signup);
}

export function resetNavigation() {
    document.getElementById('login-button').style.display = 'inline-block';
    document.getElementById('signup-button').style.display = 'inline-block';
    document.getElementById('logout-button').style.display = 'none';
    document.getElementById('profile-button').style.display = 'none';
}

