import { showLoginForm } from './dom-utils.js';

function getCSRFToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        if (cookie.trim().startsWith('csrftoken=')) {
            csrfToken = cookie.trim().substring('csrftoken='.length);
        }
    }
    return csrfToken;
}

function postAPI(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(data),
        credentials: 'include'
    }).then(response => {
        if (!response.ok) throw new Error('Response not OK');
        return response.json();
    });
}

export async function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await postAPI('/user-api/login/', data);
        if (response.message) {
            window.location.href = '/';
        } else {
            alert(response.error || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed: ' + error.message);
    }
}

export async function signup(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await postAPI('/user-api/signup/', data);
        if (response.message === 'User created successfully') {
            alert('Signup successful! Please log in.');
            showLoginForm();
        } else {
            alert(response.error || 'Signup failed');
        }
    } catch (error) {
        console.error('Signup error:', error);
        alert('Signup failed: ' + error.message);
    }
}

export async function logout(event) {
    try {
        const response = await postAPI('/user-api/logout/', {});
        if (response.message) {
            window.location.href = '/';
        } else {
            alert('Failed to log out.');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('Logout failed: ' + error.message);
    }
}

