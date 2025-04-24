<template>
    <div class="blocked-page">
      <h1>Your Account is Blocked</h1>
      <p>You cannot access your dashboard because: <b>{{ reason }}</b></p>
      <button @click="goToLogin">Go to Login</button>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        reason: '',
      };
    },
    created() {
      this.reason = this.$route.query.reason || "No reason provided";
    },
    methods: {
      goToLogin() {
        this.$router.push('/login');
      },
    },
  };
  </script>
  
  <style scoped>
  .blocked-page {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #ffdddd;
    color: #990000;
    font-family: Arial, sans-serif;
  }
  
  .blocked-page h1 {
    font-size: 2rem;
    margin-bottom: 20px;
  }
  
  .blocked-page p {
    font-size: 1.2rem;
    margin-bottom: 30px;
    text-align: center;
  }
  
  .blocked-page button {
    padding: 10px 20px;
    font-size: 1rem;
    background-color: #990000;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .blocked-page button:hover {
    background-color: #cc0000;
  }
  </style>
  