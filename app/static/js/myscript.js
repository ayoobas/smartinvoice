const togglePassword = document.querySelector('#togglePassword');
const password = document.querySelector('#password');
togglePassword.addEventListener('click', (e) => {
    const type = password.getAttribute('type') === 'password' ? 'text': 'password';
    password.setAttribute('type', type);
    e.target.classList.toggle('bi-eye');
})

const ctogglePassword = document.querySelector('#ctogglePassword');
const cpassword = document.querySelector('#cpassword');
ctogglePassword.addEventListener('click', (e) => {
    const type = cpassword.getAttribute('type') === 'password' ? 'text': 'password';
    cpassword.setAttribute('type', type);
    e.target.classList.toggle('bi-eye');
})

