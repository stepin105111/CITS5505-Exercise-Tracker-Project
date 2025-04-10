// Fetch users from localStorage
let users = JSON.parse(localStorage.getItem('users')) || [];

// Function to check if email exists
function email_check(email) {
  return users.some((user) => user.email === email);
}

// Function to validate password
function pass_check(email, password) {
  const user = users.find((user) => user.email === email);
  return user && user.password === password;
}

// Handle login form submission
document.getElementById('loginForm').addEventListener('submit', (event) => {
  event.preventDefault(); // Prevent form submission

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value.trim();

  // Check if the user exists
  if (email_check(email)) {
    // Validate password
    if (pass_check(email, password)) {
      // Update login status in localStorage
      localStorage.setItem('login_status', JSON.stringify(true));
      alert('Successfully Logged In!');
      window.location.href = './dashboard.html'; // Redirect to dashboard
    } else {
      alert('Incorrect password. Please try again.');
    }
  } else {
    alert('No account found with this email. Please register.');
  }
});