document.getElementById('signup-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('http://127.0.0.1:8000/api/users/signup/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            alert('Signup successful!');
            window.location.href = 'login.html';
        } else {
            const errorData = await response.json();
            alert(errorData.error || 'Signup failed');
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
