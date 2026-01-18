document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const alertMessage = document.getElementById('alertMessage');

    function showAlert(message, type = 'danger') {
        alertMessage.textContent = message;
        alertMessage.className = `alert alert-${type} mt-3`;
        alertMessage.classList.remove('d-none');
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/v1/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('jwt_token', data.jwt_token);
                    localStorage.setItem('user_info', JSON.stringify(data.user));
                    window.location.href = '/dashboard';
                } else {
                    showAlert(data.error || 'Login failed');
                }
            } catch (error) {
                showAlert('An error occurred. Please try again.');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const organization = document.getElementById('organization').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/v1/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, organization, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    // Auto login or redirect to login
                    showAlert('Registration successful! Redirecting to login...', 'success');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 1500);
                } else {
                    showAlert(data.error || 'Registration failed');
                }
            } catch (error) {
                showAlert('An error occurred. Please try again.');
            }
        });
    }
});
