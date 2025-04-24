<template>
  <div class="container">
    <div class="header">
      <div class="login-box" v-for="login in logins" :key="login.text">
        <button class="login-button" @click="navigateTo(login.route)">
          {{ login.text }}
        </button>
      </div>
    </div>

    <div class="hero">
      <div class="hero-text">
        <h1>QuickWick Household Services</h1>
        <p>Instant service at your doorstep.</p>
        <button class="cta-button" @click="navigateTo('/customerlogin')">Book Now</button>
      </div>
      <div class="hero-image">
        <img src="/img/undraw_booking_1ztt.svg" alt="Services" />
      </div>
    </div>
  </div>
</template>



<script>
export default {
    name: 'HomePage',
    data() {
        return {
            logins: [
                { text: 'Admin Login', route: '/adminlogin' },
                { text: 'Customer Login', route: '/customerlogin' },
                { text: 'Professional Login', route: '/professionallogin' },
            ],
        };
    },
    computed: {
        isLoggedIn() {
            return !!localStorage.getItem('token'); 
        },
    },
    methods: {
        navigateTo(route) {
            this.$router.push(route);
        },
        logout() {
            localStorage.removeItem('token'); 
            alert('You have been logged out.');
            this.$router.push('/');
        },
    },
};
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body, html {
  height: 100%;
  font-family: 'Poppins', sans-serif;
}

.container {
  min-height: 100vh;
  background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #fff;
  position: relative;
}

.header {
  position: absolute;
  top: 20px;
  right: 30px;
  display: flex;
  gap: 1rem;
  z-index: 10;
}

.login-box {
  background-color: rgba(255, 255, 255, 0.15);
  padding: 10px;
  border-radius: 10px;
  backdrop-filter: blur(10px);
}

.login-button {
  background: #ff9800;
  color: #fff;
  border: none;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-button:hover {
  background-color: #ff7700;
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(255, 119, 0, 0.5);
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 100px 60px 40px;
  gap: 40px;
}

.hero-text {
  flex: 1;
}

.hero-text h1 {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.hero-text p {
  font-size: 1.25rem;
  margin-bottom: 30px;
  max-width: 500px;
}

.cta-button {
  background-color: #ffffff;
  color: #333;
  border: none;
  padding: 14px 28px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cta-button:hover {
  background-color: #eeeeee;
  transform: scale(1.05);
}

.hero-image {
  flex: 1;
}

.hero-image img {
  width: 100%;
  max-width: 400px;
  filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.2));
}

.footer {
  background-color: rgba(255, 255, 255, 0.15);
  text-align: center;
  padding: 20px;
  font-size: 14px;
  color: #f1f1f1;
}

.footer a {
  color: #fff;
  text-decoration: underline;
  margin: 0 10px;
}
</style>
