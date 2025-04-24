<template>
    <div class="container">
      <div class="login-box">
        <h1>Customer Registration</h1>
        <form @submit.prevent="registerCustomer">
          <input 
            v-model="customerName" 
            type="text" 
            placeholder="Enter your name" 
            required 
          />
          <input 
            v-model="customerPassword" 
            type="password" 
            placeholder="Enter your password" 
            required 
          />
          <input 
            v-model="contactNumber" 
            type="text" 
            placeholder="Enter your contact number" 
            required 
          />
          <input 
            v-model="customerEmail" 
            type="text" 
            placeholder="Enter your Email" 
            required 
          />
          <button type="submit">Register</button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'; 
  
  export default {
    data() {
      return {
        customerName: '', 
        customerPassword: '',
        contactNumber: '',
        customerEmail: '' 
      };
    },
    methods: {
      async registerCustomer() {
        try {
          const payload = {
  customer_name: this.customerName,
  customer_password: this.customerPassword,
  customer_number: this.contactNumber ,
  customer_email: this.customerEmail
};

  
          const response = await axios.post('http://54.242.17.17:5000/api/customers/register', payload);
  
          if (response.status === 201) {
            const customerId = response.data.customer_id;
            alert(`Registration successful for Customer!\nYour ID is: ${ customerId }`);
            this.$router.push('/customerlogin'); 
          }
        } catch (error) {
          console.error('Error registering customer:', error);
          alert('Registration failed. Please try again.');
        }
      }
    }
  };
  </script>
  
  <style>
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
  