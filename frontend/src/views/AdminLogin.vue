<template>
  <div class="container">
    <div class="login-box">
      <h1>Welcome Back, Admin</h1>
      <form @submit.prevent="login">
        <input v-model="adminId" type="text" placeholder="Admin ID" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      adminId: '',
      password: '',
    };
  },
  methods: {
    async login() {
      if (this.adminId && this.password) {
        try {
          const response = await axios.post('http://54.242.17.17:5000/api/admins/login', {
            admin_id: this.adminId,
            admin_password: this.password,
          });

          if (response.status === 200 && response.data.token) {
            localStorage.setItem('jwt_token', response.data.token);
            alert('Login successful!');
            this.$router.push('/admin/dashboard');
          } else {
            alert('Login failed. Please try again.');
          }
        } catch (error) {
          if (error.response) {
            alert(error.response.data.message || 'Invalid credentials.');
          } else {
            alert('Something went wrong. Please try again later.');
          }
        }
      } else {
        alert('Please enter both ID and password.');
      }
    },
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
