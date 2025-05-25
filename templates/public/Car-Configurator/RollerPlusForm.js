function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function showToast(message, type = "info") {
  toastr[type](message);
}

if (!document.getElementById("toast-styles")) {
  const style = document.createElement("style");
  style.id = "toast-styles";
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeOut {
      from { opacity: 1; transform: translateY(0); }
      to { opacity: 0; transform: translateY(-20px); }
    }
  `;
  document.head.appendChild(style);
}

function setupRollerPlusPasswordToggle() {
  const toggleBtn = document.getElementById('toggle-password');
  const passwordInput = document.getElementById('signup-password');
  const eyeIcon = document.getElementById('eye-icon');
  const eyeOffIcon = document.getElementById('eye-off-icon');

  toggleBtn.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    eyeIcon.classList.toggle('hidden', !isPassword);
    eyeOffIcon.classList.toggle('hidden', isPassword);
  });
}

function handleRollerPlusPasswordChange() {
  const passwordInput = document.getElementById('signup-password');
  const passwordInput1 = document.getElementById('password1');
  const passwordInput2 = document.getElementById('password2');

  passwordInput.addEventListener('input', () => {
    const passwordValue = passwordInput.value;
    passwordInput1.value = passwordValue;
    passwordInput2.value = passwordValue;
  });
}

async function handleRollerPlusSignUpSubmit(e) {
  e.preventDefault();
  e.preventDefault();
  const form = e.target;
  const emailInput = form.elements.email;
  const passwordInput = form.elements.password;

  if (!emailInput || !passwordInput) {
    console.error('Form is missing email or password fields');
    return; // Exit the function if fields are missing
  }

  const email = emailInput.value;
  const password = passwordInput.value;
  const formData = {
    first_name: document.getElementById('first_name').value,
    last_name: document.getElementById('last_name').value,
    email: document.getElementById('signup-email').value,
    phone_number: document.getElementById('phone_number').value,
    password: document.getElementById('signup-password').value
  };

  var data = new FormData($('#show').get(0));
  $('#pro').show();
  
  $.ajax({
    type: 'POST',
    url: "{% url 'customer_register' %}",
    data: data,
    cache: false,
    processData: false,
    contentType: false,
    crossDomain: true,
    success: function (response) {
      if (response.is_success) {
        toastr.success(response['message']);
        
        const csrftoken = getCookie('csrftoken');
        
        const loginData = {
          csrfmiddlewaretoken: csrftoken,
          username: formData.email,
          password: formData.password,
        };

        $.ajax({
          type: 'POST',
          url: "{% url 'customer_login' %}",
          data: loginData,
          success: function(loginResponse) {
            if (loginResponse.is_success) {
              toastr.success("User logged in successfully!");
              userLoggedIn = true;
              const closebutton = document.getElementById('close-roller-plus-signup');
              closebutton.click();
              const reserveButton = document.getElementById('roller_plus_reserve_button');
              reserveButton.click();
            } else {
              toastr.error(loginResponse['message']);
            }
          },
          error: function(loginError) {
            toastr.error("Auto-login failed. Please login manually.");
            setTimeout(function() {
              location.href = "{% url 'customer_login' %}";
            }, 3000);
          }
        });
        
      } else {
        toastr.error(response['message']);
      }
      $('#pro').hide();
    },
    error: function (response) {
      if (!response.is_success) {
        toastr.error(response['message'] || "Registration failed");
      }
      $('#pro').hide();
    }
  });
}

function showRollerPlusLoginForm() {
  const loginSignupSection = document.getElementById('ROLLER_PLUS_LOGIN_SIGNUP_SECTION');
  if (!loginSignupSection) return;

  loginSignupSection.innerHTML = '';

  const formContainer = document.createElement('div');
  formContainer.className = 'max-w-md mx-auto p-6 bg-white rounded-lg shadow-md';

  formContainer.innerHTML = `
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Log In</h2>
      <button id="close-roller-plus-login" class="text-gray-500 hover:text-gray-700">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <form id="roller-plus-login-form" class="space-y-4">
      {% csrf_token %}
      <div>
        <label for="roller-plus-login-email" class="block text-sm font-medium text-gray-700">Email</label>
        <input type="email" id="roller-plus-login-email" name="email" required 
               class="mt-1 block w-full border border-gray-300 text-gray-700 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
      </div>
      
      <div>
        <label for="roller-plus-login-password" class="block text-sm font-medium text-gray-700">Password</label>
        <div class="relative mt-1">
          <input type="password" id="roller-plus-login-password" name="password" required 
                 class="block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm py-2 px-3 pr-10 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          <button type="button" id="toggle-roller-plus-login-password" class="absolute inset-y-0 right-0 px-3 flex items-center" tabindex="-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" id="roller-plus-login-eye-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 hidden" id="roller-plus-login-eye-off-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>
        </div>
      </div>
      
      <div>
        <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Log In
        </button>
      </div>
      
      <div class="text-center text-sm">
        <p class="text-gray-600">Don't have an account? 
          <a href="#" id="show-roller-plus-signup" class="font-medium text-indigo-600 hover:text-indigo-500">Sign up</a>
        </p>
      </div>
    </form>
  `;

  loginSignupSection.appendChild(formContainer);

  // Event listeners remain unchanged
  document.getElementById('close-roller-plus-login').addEventListener('click', () => {
    loginSignupSection.innerHTML = '';
  });

  document.getElementById('show-roller-plus-signup').addEventListener('click', (e) => {
    e.preventDefault();
    showRollerPlusSignUpForm();
  });

  setupRollerPlusLoginPasswordToggle();
  document.getElementById('roller-plus-login-form').addEventListener('submit', handleRollerPlusLoginSubmit);
}

function setupRollerPlusLoginPasswordToggle() {
  const toggleBtn = document.getElementById('toggle-roller-plus-login-password');
  const passwordInput = document.getElementById('roller-plus-login-password');
  const eyeIcon = document.getElementById('roller-plus-login-eye-icon');
  const eyeOffIcon = document.getElementById('roller-plus-login-eye-off-icon');

  toggleBtn.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    eyeIcon.classList.toggle('hidden', !isPassword);
    eyeOffIcon.classList.toggle('hidden', isPassword);
  });
}

function handleRollerPlusLoginSubmit(e) {
  e.preventDefault();
  
  const formData = {
    username: document.getElementById('roller-plus-login-email').value,
    password: document.getElementById('roller-plus-login-password').value,
    csrfmiddlewaretoken: getCookie('csrftoken')
  };

  $.ajax({
    type: 'POST',
    url: "{% url 'customer_login' %}",
    data: formData,
    success: function(response) {
      if (response.is_success) {
        toastr.success("Logged in successfully!");
        userLoggedIn = true;
        document.getElementById('close-roller-plus-login').click();
        const reserveButton = document.getElementById('roller_plus_reserve_button');
        reserveButton.click();
      } else {
        toastr.error(response.message || "Login failed");
      }
    },
    error: function(response) {
      toastr.error(response.responseJSON?.message || "Login failed");
    }
  });
}

function showRollerPlusSignUpForm() {
  const loginSignupSection = document.getElementById('ROLLER_PLUS_LOGIN_SIGNUP_SECTION');
  if (!loginSignupSection) return;

  loginSignupSection.innerHTML = '';

  const formContainer = document.createElement('div');
  formContainer.className = 'max-w-md mx-auto p-6 bg-white rounded-lg shadow-md';

  formContainer.innerHTML = `
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-white">Sign Up</h2>
          <button id="close-roller-plus-signup" class="text-gray-300 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form id="roller-plus-signup-form" class="grid grid-cols-2 gap-4">
          {% csrf_token %}
          <input type="text" name="role" value="customer" hidden/>
          <input type="text" id="password1" name="password1" value="" hidden/>
          <input type="text" id="password2" name="password2" value="" hidden/>
          <div>
            <label for="signup-first-name" class="block text-sm font-medium text-white">First Name</label>
            <input type="text" id="signup-first-name" name="first_name" required 
                   class="mt-1 block w-full border border-gray-500 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          </div>
          
          <div>
            <label for="signup-last-name" class="block text-sm font-medium text-white">Last Name</label>
            <input type="text" id="signup-last-name" name="last_name" required 
                   class="mt-1 block w-full border border-gray-500 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          </div>
          
          <div>
            <label for="signup-email" class="block text-sm font-medium text-white">Email</label>
            <input type="email" id="signup-email" name="email" required 
                   class="mt-1 block w-full border border-gray-500 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          </div>
          
          <div>
            <label for="signup-phone-number" class="block text-sm font-medium text-white">Phone Number</label>
            <input type="tel" id="signup-phone-number" name="phone_number" required 
                   class="mt-1 block w-full border border-gray-500 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          </div>
          
          <div class="col-span-2">
            <label for="signup-password" class="block text-sm font-medium text-white">Password</label>
            <div class="relative mt-1">
              <input type="password" id="signup-password" name="password" required 
                     class="block w-full border border-gray-500 rounded-md shadow-sm py-2 px-3 pr-10 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
              <button type="button" id="toggle-password" class="absolute inset-y-0 right-0 px-3 flex items-center" tabindex="-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-300" id="eye-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-300 hidden" id="eye-off-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="col-span-2">
            <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              Sign Up
            </button>
          </div>
          
          <div class="col-span-2 text-center text-sm">
            <p class="text-white">Already have an account? 
              <a href="#" id="show-roller-plus-login-form" class="font-medium text-indigo-300 hover:text-indigo-400">Log in</a>
            </p>
          </div>
        </form>
      `;

      loginSignupSection.appendChild(formContainer);

      document.getElementById('close-roller-plus-signup').addEventListener('click', () => {
        loginSignupSection.innerHTML = '';
      });

      document.getElementById('roller-plus-signup-form').addEventListener('submit', handleRollerPlusSignUpSubmit);
      handleRollerPlusPasswordChange();

      document.getElementById('show-roller-plus-login-form').addEventListener('click', (e) => {
        e.preventDefault();
        showRollerPlusLoginForm();
    
  });
}
