<template>
  <div class="container">
    <div class="login-box">
      <h1>Customer Login Page</h1>
      <input v-model="customerId" type="text" placeholder="Enter your ID" required />
      <input v-model="password" type="password" placeholder="Enter your password" required />
      <button @click="login">Login</button>
      <div class="register-section">
        <p>Don't have an account?</p>
        <button @click="register">Register</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      customerId: '',
      password: '',
    };
  },
  methods: {
    register() {
            this.$router.push('/customerregister');
        },
    async login() {
  if (!this.customerId || !this.password) {
    alert('Please enter both ID and password.');
    return;
  }

  try {
    const payload = {
      customer_id: this.customerId,
      customer_password: this.password,
    };

    console.log('Login Payload:', payload);

    const response = await axios.post('http://54.242.17.17:5000/api/customers/login', payload);

    console.log('Login Response:', response);

    if (response.status === 200 && response.data.token) {
      const { token } = response.data;
      localStorage.setItem('token', token);

      alert('Login successful!');
      this.$router.push('/customer/dashboard'); 
    } else {
      alert('Login successful but no token received.');
    }
  } catch (error) {
    const status = error.response?.status;
    console.error('Login Error:', error);

    if (status === 401) {
      alert('Invalid login credentials. Please try again.');
    } else if (status === 403) {
      alert(`${error.response.data.message}`);
      this.$router.push('/');
    } else {
      alert('An unexpected error occurred. Please try again.');
    }
  }
}


  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body,
html {
  height: 100%;
  font-family: 'Poppins', sans-serif;
}

.container {
  background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%);
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 40px 30px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  color: #000;
  width: 100%;
  max-width: 400px;
}

.login-box h1 {
  font-size: 28px;
  margin-bottom: 25px;
  font-weight: 600;
  color: #333;
  text-align: center;
}

.login-box input {
  width: 100%;
  padding: 12px;
  margin-bottom: 18px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  background-color: #f0f0f0;
  color: #333;
  transition: box-shadow 0.3s ease;
}

.login-box input:focus {
  outline: none;
  box-shadow: 0 0 0 2px #00c9ff;
}

.login-box button {
  width: 100%;
  padding: 12px;
  background-color: #ff9800;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-box button:hover {
  background-color: #ff7700;
  transform: scale(1.03);
  box-shadow: 0 6px 18px rgba(255, 119, 0, 0.4);
}
</style>
