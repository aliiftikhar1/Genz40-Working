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
  
  function checkUserLoggedIn() {
    return "{{request.user.id}}" !== "None";
  }
  
  let userLoggedIn = checkUserLoggedIn();
  
  function setupPasswordToggle() {
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
  
  function handlePasswordChange() {
    const passwordInput = document.getElementById('signup-password');
    const passwordInput1 = document.getElementById('password1');
    const passwordInput2 = document.getElementById('password2');
  
    passwordInput.addEventListener('input', () => {
      const passwordValue = passwordInput.value;
      passwordInput1.value = passwordValue;
      passwordInput2.value = passwordValue;
    });
  }
  
  async function handleSignUpSubmit(e) {
    e.preventDefault();
    
    const formData = {
      first_name: document.getElementById('first_name').value,
      last_name: document.getElementById('last_name').value,
      email: document.getElementById('signup-email').value,
      phone_number: document.getElementById('phone_number').value,
      password: document.getElementById('signup-password').value
    };
  
    var data = new FormData($('#signup-form').get(0));
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
                const closebutton = document.getElementById('close-signup');
                closebutton.click();
                const reserveButton = document.getElementById('reserve_button');
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
  
  function showLoginForm() {
    const loginSignupSection = document.getElementById('LOGIN_SIGNUP_SECTION');
    if (!loginSignupSection) return;
  
    loginSignupSection.innerHTML = '';
  
    const formContainer = document.createElement('div');
    formContainer.className = 'max-w-md mx-auto p-6 bg-white rounded-lg shadow-md';
  
    formContainer.innerHTML = `
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">Log In</h2>
        <button id="close-login" class="text-gray-500 hover:text-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <form id="login-form" class="space-y-4">
        {% csrf_token %}
        <div>
          <label for="login-email" class="block text-sm font-medium text-gray-700">Email</label>
          <input type="email" id="login-email" name="email" required 
                 class="mt-1 block w-full border border-gray-300 text-gray-700 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        
        <div>
          <label for="login-password" class="block text-sm font-medium text-gray-700">Password</label>
          <div class="relative mt-1">
            <input type="password" id="login-password" name="password" required 
                   class="block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm py-2 px-3 pr-10 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
            <button type="button" id="toggle-login-password" class="absolute inset-y-0 right-0 px-3 flex items-center" tabindex="-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" id="login-eye-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 hidden" id="login-eye-off-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
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
            <a href="#" id="show-signup-form" class="font-medium text-indigo-600 hover:text-indigo-500">Sign up</a>
          </p>
        </div>
      </form>
    `;
  
    loginSignupSection.appendChild(formContainer);
  
    document.getElementById('close-login').addEventListener('click', () => {
      loginSignupSection.innerHTML = '';
    });
  
    document.getElementById('show-signup-form').addEventListener('click', (e) => {
      e.preventDefault();
      showSignUpForm();
    });
  
    setupLoginPasswordToggle();
    document.getElementById('login-form').addEventListener('submit', handleLoginSubmit);
  }
  
  function setupLoginPasswordToggle() {
    const toggleBtn = document.getElementById('toggle-login-password');
    const passwordInput = document.getElementById('login-password');
    const eyeIcon = document.getElementById('login-eye-icon');
    const eyeOffIcon = document.getElementById('login-eye-off-icon');
  
    toggleBtn.addEventListener('click', () => {
      const isPassword = passwordInput.type === 'password';
      passwordInput.type = isPassword ? 'text' : 'password';
      eyeIcon.classList.toggle('hidden', !isPassword);
      eyeOffIcon.classList.toggle('hidden', isPassword);
    });
  }
  
  function handleLoginSubmit(e) {
    e.preventDefault();
    
    const formData = {
      username: document.getElementById('login-email').value,
      password: document.getElementById('login-password').value,
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
          document.getElementById('close-login').click();
          const reserveButton = document.getElementById('reserve_button');
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
  
  function showSignUpForm() {
    const loginSignupSection = document.getElementById('LOGIN_SIGNUP_SECTION');
    if (!loginSignupSection) return;
  
    loginSignupSection.innerHTML = '';
  
    const formContainer = document.createElement('div');
    formContainer.className = 'max-w-md mx-auto p-6 bg-white rounded-lg shadow-md';
  
    formContainer.innerHTML = `
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">Sign Up</h2>
        <button id="close-signup" class="text-gray-500 hover:text-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <form id="signup-form" class="space-y-4">
        {% csrf_token %}
        <input type="text" name="role" value="customer" hidden/>
        <input type="text" id="password1" name="password1" value="" hidden/>
        <input type="text" id="password2" name="password2" value="" hidden/>
        <div>
          <label for="first_name" class="block text-sm font-medium text-gray-700">First Name</label>
          <input type="text" id="first_name" name="first_name" required 
                 class="mt-1 block w-full border text-gray-700 border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        
        <div>
          <label for="last_name" class="block text-sm font-medium text-gray-700">Last Name</label>
          <input type="text" id="last_name" name="last_name" required 
                 class="mt-1 block w-full border border-gray-300 text-gray-700 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        
        <div>
          <label for="signup-email" class="block text-sm font-medium text-gray-700">Email</label>
          <input type="email" id="signup-email" name="email" required 
                 class="mt-1 block w-full border border-gray-300 text-gray-700 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        
        <div>
          <label for="phone_number" class="block text-sm font-medium text-gray-700">Phone Number</label>
          <input type="tel" id="phone_number" name="phone_number" required 
                 class="mt-1 block w-full border border-gray-300 text-gray-700 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        
        <div>
          <label for="signup-password" class="block text-sm font-medium text-gray-700">Password</label>
          <div class="relative mt-1">
            <input type="password" id="signup-password" name="password" required 
                   class="block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm py-2 px-3 pr-10 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
            <button type="button" id="toggle-password" class="absolute inset-y-0 right-0 px-3 flex items-center" tabindex="-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" id="eye-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 hidden" id="eye-off-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </button>
          </div>
        </div>
        
        <div>
          <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Sign Up
          </button>
        </div>
        
        <div class="text-center text-sm">
          <p class="text-gray-600">Already have an account? 
            <a href="#" id="show-login-form" class="font-medium text-indigo-600 hover:text-indigo-500">Log in</a>
          </p>
        </div>
      </form>
    `;
  
    loginSignupSection.appendChild(formContainer);
  
    document.getElementById('close-signup').addEventListener('click', () => {
      loginSignupSection.innerHTML = '';
    });
  
    setupPasswordToggle();
    document.getElementById('signup-form').addEventListener('submit', handleSignUpSubmit);
    handlePasswordChange();
    
    document.getElementById('show-login-form').addEventListener('click', (e) => {
      e.preventDefault();
      showLoginForm();
    });
  }
  
  function initRollerPriceCalculator() {
    const basePrice = 24999.00;
    const totalPriceEl = document.getElementById('rollertotalPrice');
    const mobilePriceEl = document.getElementById('rollermobiletotalPrice');
  
    function updatePrice() {
      let total = basePrice;
      document.querySelectorAll('.roller-feature-checkbox').forEach(cb => {
        if (cb.checked && !cb.disabled) {
          total += parseFloat(cb.dataset.price || 0);
        }
      });
      const formatted = '$' + total.toFixed(2);
      if (totalPriceEl) totalPriceEl.textContent = formatted;
      if (mobilePriceEl) mobilePriceEl.textContent = formatted;
    }
  
    document.addEventListener('change', e => {
      if (e.target.classList.contains('roller-feature-checkbox')) {
        updatePrice();
      }
    });
  
    updatePrice();
  }
  
  function submitRollerForm(event) {
    event.preventDefault();
    
    if (!userLoggedIn) {
      showSignUpForm();
      return;
    }
  
    const checked = document.querySelectorAll('#rollerForm input[type="checkbox"]:checked:not([disabled])');
    const features = Array.from(checked).map(cb => cb.name).filter(Boolean);
  
    const selectedNostril = document.querySelector('#rollerForm input[name="nostril"]:checked');
    if (selectedNostril) {
      features.push(`${selectedNostril.value.charAt(0).toUpperCase() + selectedNostril.value.slice(1)}Nostril`);
    }
  
    const totalPriceEl = document.getElementById("rollertotalPrice") || document.getElementById("rollermobiletotalPrice");
    const price = totalPriceEl ? totalPriceEl.textContent.replace("$", "").replace(/,/g, "") : "100";
    const carModel = "{{ items.id }}";
    const userId = localStorage.getItem("userId") || sessionStorage.getItem("userId") || "fb292fed-9283-441f-82f9-da5fb505606b";
  
    const formData = new FormData();
    formData.append("title", "Roller");
    formData.append("extra_features", features.length ? features.join(', ') : "None");
    formData.append("price", price);
    formData.append("status", "pending");
    formData.append("car_model", carModel);
    formData.append("user", userId);
  
    fetch("{% url 'save-booked-package' %}", {
      method: "POST",
      body: formData,
      credentials: "include",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then(res => {
        if (res.status === 403) {
          window.location.href = "{% url 'customer_login' %}";
        }
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.json();
      })
      .then(data => {
        toastr.success("Package Booked successfully!");
        var newdata = new FormData();
        console.log("Package id is : ", data)
        newdata.append("package_id", data.id);
        window.location.href = "{% url 'reservation_checkout' '0' %}".replace('0', data.id);
      })
      .catch(err => {
        console.error(err);
        showToast("Failed to save configuration.", "error");
      });
  }
  
  function updateSelectedFeatures() {
    const selectedFeatures = [];
    
    const checkedCheckboxes = document.querySelectorAll('#rollerForm input[type="checkbox"]:checked:not([disabled])');
    const checkedRadios = document.querySelectorAll('#rollerForm input[type="radio"]:checked:not([disabled])');
  
    checkedCheckboxes.forEach(cb => selectedFeatures.push(cb.name));
    checkedRadios.forEach(rb => selectedFeatures.push(rb.name));
  
    const formattedFeatures = selectedFeatures.map(feature => feature.charAt(0).toUpperCase() + feature.slice(1)).join(', ');
  
    const selectedFeatureElement = document.getElementById('roller_selected_features');
    if (selectedFeatureElement) {
      if (formattedFeatures.length > 0) {
        selectedFeatureElement.innerHTML = `<strong>Selected Extra Features:</strong><br>${formattedFeatures}`;
      } else {
        selectedFeatureElement.textContent = 'No features selected yet';
      }
    }
  }
  
  document.addEventListener('DOMContentLoaded', function () {
    initRollerPriceCalculator();
    
    document.querySelectorAll('#rollerForm input[type="checkbox"], #rollerForm input[type="radio"]').forEach(input => {
      input.addEventListener('change', updateSelectedFeatures);
    });
    
    updateSelectedFeatures();
  });