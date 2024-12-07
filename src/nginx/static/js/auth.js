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
            window.location.href = '/';
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
            const errorData = await response.json().catch(() => null);
            if (errorData) {
                alert(errorData.error || 'Signup failed');
            } else {
                alert('Unexpected error occurred.');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Could not connect to the server. Please try again later.');
    }
}

export async function logout() {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch('/user-api/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
        });

        if (response.ok) {
            resetNavigation();
            alert('Logged out successfully!');
            window.location.href = '/';
        } else {
            alert('Error logging out.');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}


