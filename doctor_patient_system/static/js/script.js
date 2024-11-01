// script.js

document.addEventListener('DOMContentLoaded', function () {
    const userTypeSelect = document.getElementById('signup-user-type');
    const form = document.querySelector('form');
    const submitButton = document.querySelector('button[type="submit"]');
    
    // Update button text based on selected user type
    userTypeSelect.addEventListener('change', function () {
        const userType = userTypeSelect.value;
        if (userType === 'doctor') {
            submitButton.textContent = 'Sign Up as Doctor';
        } else if (userType === 'patient') {
            submitButton.textContent = 'Sign Up as Patient';
        }
    });

    // Handle form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const userType = userTypeSelect.value;
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        if (!name || !email || !password) {
            alert('All fields are required!');
            return;
        }

        fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userType: userType,
                name: name,
                email: email,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to respective form (health history or doctor details) based on user type
                if (userType === 'doctor') {
                    window.location.href = '/doctor_details';  // Route to doctor details form
                } else if (userType === 'patient') {
                    window.location.href = '/health_history';  // Route to health history form
                }
            } else {
                alert(data.message);  // Show the error message returned from the server
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
        
    });

});
