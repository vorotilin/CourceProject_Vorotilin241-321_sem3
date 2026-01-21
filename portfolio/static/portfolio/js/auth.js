function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const logoutBtn = document.getElementById('logoutBtn');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

function openModal(modal) {
    modal.classList.add('active');
}

function closeModal(modal) {
    modal.classList.remove('active');
}

if (loginBtn) {
    loginBtn.addEventListener('click', () => openModal(loginModal));
}

if (registerBtn) {
    registerBtn.addEventListener('click', () => openModal(registerModal));
}

document.querySelectorAll('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        closeModal(this.closest('.modal'));
    });
});

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target);
    }
});

function showErrors(errorsDiv, errors) {
    errorsDiv.innerHTML = '';

    if (errors.general) {
        errors.general.forEach(error => {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-item';
            errorDiv.textContent = error;
            errorsDiv.appendChild(errorDiv);
        });
    }

    for (const [field, fieldErrors] of Object.entries(errors)) {
        if (field !== 'general') {
            fieldErrors.forEach(error => {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-item';
                errorDiv.textContent = `${field}: ${error}`;
                errorsDiv.appendChild(errorDiv);
            });
        }
    }
}

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            username: document.getElementById('loginUsername').value,
            password: document.getElementById('loginPassword').value,
        };

        try {
            const response = await fetch('/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                window.location.reload();
            } else {
                showErrors(document.getElementById('loginErrors'), data.errors);
            }
        } catch (error) {
            showErrors(document.getElementById('loginErrors'), {
                general: ['Произошла ошибка при входе']
            });
        }
    });
}

if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            username: document.getElementById('regUsername').value,
            first_name: document.getElementById('regFirstName').value,
            last_name: document.getElementById('regLastName').value,
            email: document.getElementById('regEmail').value,
            role: document.getElementById('regRole').value,
            password1: document.getElementById('regPassword1').value,
            password2: document.getElementById('regPassword2').value,
        };

        try {
            const response = await fetch('/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                window.location.reload();
            } else {
                showErrors(document.getElementById('registerErrors'), data.errors);
            }
        } catch (error) {
            showErrors(document.getElementById('registerErrors'), {
                general: ['Произошла ошибка при регистрации']
            });
        }
    });
}

if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/auth/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                window.location.reload();
            }
        } catch (error) {
            console.error('Logout error:', error);
        }
    });
}
