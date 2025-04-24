<template>
  <div class="dashboard">
    <!-- Top Navbar -->
    <header class="navbar">
      <div class="logo">Admin Panel</div>
      <div class="admin-info">
        <i class="fas fa-user-shield"></i>
        <span>{{ admin.admin_name }}</span>
        <button class="logout-btn" @click="logout">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </header>

    <div class="layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <button @click="navigateTo('/admin/customerinfo')"><i class="fas fa-users"></i> Customers</button>
        <button @click="navigateTo('/admin/professionalinfo')"><i class="fas fa-user-tie"></i> Professionals</button>
        <button @click="navigateTo('/admin/serviceinfo')"><i class="fas fa-cogs"></i> Services</button>
        <button @click="navigateTo('/admin/servicerequestinfo')"><i class="fas fa-tasks"></i> Requests</button>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <div class="card">
          <h2>Welcome, {{ admin.admin_name }}</h2>
          <p><strong>Admin ID:</strong> {{ admin.admin_id }}</p>

          <button class="update-btn" @click="showUpdatePasswordForm = !showUpdatePasswordForm">
            <i class="fas fa-key"></i> Update Password
          </button>

          <div v-if="showUpdatePasswordForm" class="password-form">
            <input v-model="newPassword" type="password" placeholder="New password" />
            <input v-model="confirmPassword" type="password" placeholder="Confirm password" />
            <div class="form-actions">
              <button @click="updatePassword">Submit</button>
              <button @click="showUpdatePasswordForm = false" class="cancel">Cancel</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      admin: { admin_name: '', admin_id: null },
      showUpdatePasswordForm: false,
      newPassword: '',
      confirmPassword: '',
    };
  },
  methods: {
    async fetchAdminInfo() {
      const token = localStorage.getItem('jwt_token');
      if (!token) {
        alert('You must be logged in.');
        this.$router.push('/adminlogin');
        return;
      }
      try {
        const res = await axios.get('http://54.242.17.17:5000/api/user-info', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.data?.user) this.admin = res.data.user;
        else alert('Failed to fetch admin data');
      } catch (err) {
        console.error(err);
        alert('Session expired or error occurred.');
        this.$router.push('/adminlogin');
      }
    },
    async updatePassword() {
      if (this.newPassword !== this.confirmPassword) {
        alert('Passwords do not match!');
        return;
      }
      const token = localStorage.getItem('jwt_token');
      try {
        const res = await axios.put(
          'http://54.242.17.17:5000/api/admins/updatepassword',
          { new_password: this.newPassword },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (res.status === 200) {
          alert('Password updated!');
          this.showUpdatePasswordForm = false;
          this.newPassword = this.confirmPassword = '';
        }
      } catch (err) {
        alert('Error updating password.');
        console.error(err);
      }
    },
    logout() {
      localStorage.removeItem('jwt_token');
      alert('Logged out successfully.');
      this.$router.push('/');
    },
    navigateTo(route) {
      this.$router.push(route);
    },
  },
  mounted() {
    this.fetchAdminInfo();
  },
};
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

* {
  box-sizing: border-box;
}

.dashboard {
  font-family: 'Montserrat', sans-serif;
  background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: #fff;
}

.navbar {
  background-color: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #fff;
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border: 3px solid black;
}

.logo {
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-info span {
  color: #fff;
}

.logout-btn {
  background: #ff9800;
  color: white;
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #ff7700;
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(255, 119, 0, 0.5);
}

.layout {
  display: flex;
  height: 100%;
}

.sidebar {
  width: 220px;
  background: white;
  padding: 20px;
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar button {
  background: #f0f4ff;
  color: black;
  padding: 12px;
  font-size: 1rem;
  border: none;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: background 0.3s;
}

.sidebar button:hover {
  background: #d6e0ff;
}

.main-content {
  flex: 1;
  padding: 40px;
}

.card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin: auto;
  color: #333;
}

.card h2 {
  font-size: 1.6rem;
  margin-bottom: 10px;
}

.update-btn {
  background: black;
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  margin-top: 20px;
  cursor: pointer;
}

.update-btn:hover {
  background: #162c6c;
}

.password-form {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.password-form input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.form-actions {
  display: flex;
  gap: 10px;
}

.form-actions button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.form-actions .cancel {
  background: #ddd;
}

.form-actions button:hover {
  opacity: 0.9;
}
</style>
