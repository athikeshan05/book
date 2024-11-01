document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('login-form');
    const userTypeSelect = document.getElementById('user-type');
    const emailInput = document.getElementById('login-email');
    const passwordInput = document.getElementById('login-password');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const userType = userTypeSelect.value;
        const email = emailInput.value;
        const password = passwordInput.value;

        if (!email || !password) {
            alert('Please fill in all fields.');
            return;
        }

        // Disable the button to prevent multiple submissions
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';

        // Create an object to send to the server
        const loginData = {
            userType: userType,
            email: email,
            password: password
        };

        // Send AJAX request to the server
        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        })
        .then(response => {
            if (response.ok) {
                return response.json();  // Parse JSON if response is okay
            } else {
                return response.text().then(text => {
                    throw new Error('Server responded with: ' + text);  // Read and throw server response text
                });
            }
        })
        .then(data => {
            if (data.success) {
                // Redirect based on user type
                if (userType === 'doctor') {
                    window.location.href = '/doctor_dashboard';
                } else if (userType === 'patient') {
                    window.location.href = '/patient_dashboard';
                }
            } else {
                alert('Login failed. Please check your credentials.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
        
    });
});
