import { showLoginForm } from './dom-utils.js';

export function getCSRFToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        if (cookie.trim().startsWith('csrftoken=')) {
            csrfToken = cookie.trim().substring('csrftoken='.length);
        }
    }
    return csrfToken;
}

function saveTokens(tokens) {
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);
    console.log('Tokens saved:', tokens);
}


export function postAPI(url, data, saveTokensCallback = null) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(data),
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error(`Error: ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (saveTokensCallback && data.tokens) {
            saveTokensCallback(data.tokens);
        }
        return data;
    })
    .catch(error => {
        console.error(`Network error: ${error.message}`);
        throw error;
    });
}


export async function verify2FA(event, username) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const otp = formData.get('otp');

    try {
        const response = await postAPI('/user-api/verify/', { otp }, saveTokens);
        if (response.tokens) {
            alert('2FA verification successful!');
            window.location.href = '/';
        } else {
            alert(response.error || '2FA verification failed');
        }
    } catch (error) {
        console.error('2FA verification error:', error);
        alert('2FA verification failed: ' + error.message);
    }
}




export function show2FAForm(username) {
    const mainContent = document.querySelector('body');
    mainContent.innerHTML = `
        <h1>Verify OTP</h1>
        <form id="2fa-form">
            <input type="text" name="otp" placeholder="Enter OTP" required>
            <button type="submit">Verify</button>
        </form>
        <button id="resend-otp">Resend OTP</button>
    `;

    const twoFAForm = document.getElementById('2fa-form');
    twoFAForm.addEventListener('submit', (event) => verify2FA(event, username));

    document.getElementById('resend-otp').addEventListener('click', resendOTP);
}


export async function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await postAPI('/user-api/login/', data, saveTokens);

        if (response.message && response.twoFA_required) {
            alert('2FA required. Check your email for the OTP.');
            show2FAForm(response.username);
        } else if (response.message) {
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

