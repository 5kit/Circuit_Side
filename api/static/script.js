function toggleForm(formType) {
    if (formType === 'login') {
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('signup-form').style.display = 'none';
        localStorage.setItem('currentForm', 'login');
    } else if (formType === 'signup') {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('signup-form').style.display = 'block';
        localStorage.setItem('currentForm', 'signup');
    }
}

// Retrieve and set the form state on page load
document.addEventListener('DOMContentLoaded', function() {
    var currentForm = localStorage.getItem('currentForm');
    if (currentForm === 'signup') {
        toggleForm('signup');
    } else {
        toggleForm('login');
    }
});
