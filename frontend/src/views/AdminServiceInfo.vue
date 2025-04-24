<template>
  <div class="service-info-container">
    <h1>Service Information</h1>

    <div class="button-container">
      <button
        @click="viewServices"
        :class="{ active: activeSection === 'viewServices' }"
        class="action-button"
      >
        View All Services
      </button>
      <button
        @click="addNewService"
        :class="{ active: activeSection === 'addService' }"
        class="action-button"
      >
        Add New Service
      </button>
      <button @click="goBackToDashboard" class="action-button">
        Go Back to Dashboard
      </button>
      <div class="search-bar">
  <input
    type="text"
    id="searchInput"
    v-model="searchQuery"
    placeholder="Search for a service"
  />
  <button @click="search">Search</button>
</div>
    </div>

    <div class="main-content">
      <div v-if="loading" class="loading-message">Loading service data...</div>

      <div v-else>
        <div class="data-container">
          <div v-if="activeSection === 'viewServices'">
            <h2 class="data-header">All Services</h2>
            <div
              v-for="service in services"
              :key="service.id"
              class="service-info-block"
            >
              <h3>{{ service.service_name }}</h3>
              <div class="service-details">
                <div><strong>Service ID:</strong> {{ service.id }}</div>
                <div><strong>Price:</strong> ₹{{ service.price }}</div>
                <div><strong>Time Required:</strong> {{ service.time_required }}</div>
                <div><strong>Description:</strong> {{ service.description }}</div>

                <div class="button-group">
                  <button
                    @click="editService(service)"
                    class="action-button edit-btn"
                  >
                    Edit Service
                  </button>
                  <button
                    @click="deleteService(service.id)"
                    class="action-button delete-btn"
                  >
                    Delete Service
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeSection === 'addService'">
            <h2 class="data-header">Add a New Service</h2>
            <form @submit.prevent="saveNewService" class="add-service-form">
              <div class="form-group">
                <label for="serviceName">Service Name:</label>
                <input
                  type="text"
                  v-model="newService.service_name"
                  id="serviceName"
                  required
                />
              </div>

              <div class="form-group">
                <label for="price">Price (₹):</label>
                <input
                  type="number"
                  v-model="newService.price"
                  id="price"
                  required
                />
              </div>

              <div class="form-group">
                <label for="timeRequired">Time Required:</label>
                <input
                  type="text"
                  v-model="newService.time_required"
                  id="timeRequired"
                />
              </div>

              <div class="form-group">
                <label for="description">Description:</label>
                <textarea
                  v-model="newService.description"
                  id="description"
                  rows="4"
                ></textarea>
              </div>

              <button type="submit" class="action-button save-btn">
                Save Service
              </button>
            </form>
          </div>
          
          
          <div v-if="activeSection === 'editService'">
            <h2 class="data-header">Edit Service</h2>
            <form @submit.prevent="updateService" class="add-service-form">
              <div class="form-group">
                <label for="serviceName">Service Name:</label>
                <input
                  type="text"
                  v-model="currentService.service_name"
                  id="serviceName"
                  required
                />
              </div>

              <div class="form-group">
                <label for="price">Price (₹):</label>
                <input
                  type="number"
                  v-model="currentService.price"
                  id="price"
                  required
                />
              </div>

              <div class="form-group">
                <label for="timeRequired">Time Required:</label>
                <input
                  type="text"
                  v-model="currentService.time_required"
                  id="timeRequired"
                />
              </div>

              <div class="form-group">
                <label for="description">Description:</label>
                <textarea
                  v-model="currentService.description"
                  id="description"
                  rows="4"
                ></textarea>
              </div>

              <button type="submit" class="action-button save-btn">
                Update Service
              </button>
              <button
                type="button"
                @click="cancelEdit"
                class="action-button cancel-btn"
              >
                Cancel
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AdminServiceInfo",
  data() {
    return {
      services: [],
      newService: {
        service_name: "",
        price: null,
        time_required: "",
        description: "",
      },
      currentService: {
        id: null,
        service_name: "",
        price: null,
        time_required: "",
        description: "",
      },
      loading: true,
      searchQuery: "", 
      activeSection: "viewServices", 
    };
  },
  computed: {
    
  filteredServices() {
    const query = this.searchQuery.toLowerCase().trim();
    if (!query) return this.services; 

    return this.services.filter((service) => {
      const nameMatch = service.service_name.toLowerCase().includes(query); 
      const idMatch = service.id.toString().includes(query);
      return nameMatch || idMatch;
    });
  }
},

  methods: {
    async search() {
  try {
    const searchInput = this.searchQuery.trim();

    if (!searchInput) {
      alert("Please enter a search query.");
      return;
    }

    this.loading = true; 

    const token = localStorage.getItem("jwt_token");
    const response = await axios.get(`http://54.242.17.17:5000/api/admins/serviceinfo/search`, {
      params: { query: searchInput },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.data && response.data.services) {
      this.services = response.data.services; 
    } else {
      alert("No services found or failed to retrieve services.");
    }
  } catch (error) {
    console.error("Error during search:", error);
    alert("An error occurred while searching for services.");
  } finally {
    this.loading = false; 
  }
}
,
    async fetchServices() {
      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.get("http://54.242.17.17:5000/api/admins/serviceinfo", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        this.services = response.data.services;
      } catch (error) {
        console.error("Error fetching services:", error);
        alert("Failed to fetch services.");
      } finally {
        this.loading = false;
      }
    },

    async deleteService(serviceId) {
      if (confirm("Are you sure you want to delete this service?")) {
        try {
          const token = localStorage.getItem("jwt_token");
          const response = await axios.delete(
            `http://54.242.17.17:5000/api/admins/service/${serviceId}`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (response.data.success) {
            this.services = this.services.filter(
              (service) => service.id !== serviceId
            );
            alert("Service deleted successfully.");
          } else {
            alert("Failed to delete the service.");
          }
        } catch (error) {
          console.error("Error deleting service:", error);
          alert("Error deleting the service.");
        }
      }
    },

    async saveNewService() {
      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.post(
          "http://54.242.17.17:5000/api/admins/addservice",
          this.newService,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          this.services.push(response.data.service);
          alert("New service added successfully.");
          this.resetNewServiceForm();
          this.activeSection = "viewServices";
        } else {
          alert("Failed to add the new service.");
        }
      } catch (error) {
        console.error("Error adding new service:", error);
        alert("Error adding the new service.");
      }
    },

    editService(service) {
      this.currentService = { ...service };
      this.activeSection = "editService";
    },

    async updateService() {
      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.put(
          `http://54.242.17.17:5000/api/admins/service/${this.currentService.id}`,
          this.currentService,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          const index = this.services.findIndex(
            (service) => service.id === this.currentService.id
          );
          this.services[index] = response.data.service;
          alert("Service updated successfully.");
          this.activeSection = "viewServices";
        } else {
          alert("Failed to update the service.");
        }
      } catch (error) {
        console.error("Error updating service:", error);
        alert("Error updating the service.");
      }
    },

    cancelEdit() {
      this.activeSection = "viewServices";
    },

    resetNewServiceForm() {
      this.newService = {
        service_name: "",
        price: null,
        time_required: "",
        description: "",
      };
    },

    viewServices() {
      this.activeSection = "viewServices";
    },

    addNewService() {
      this.activeSection = "addService";
    },

    goBackToDashboard() {
      this.$router.push("/admin/dashboard");
    },
  },
  mounted() {
    this.fetchServices(); 
  },
};
</script>

<!-- <style scoped>
.action-button {
  background-color: #ddd;
  color: black;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.action-button.active {
  background-color: blue;
  color: white;
  font-weight: bold;
}

.action-button:hover {
  background-color: darkgray;
}

.service-info-container {
  background-color: #00b7be;
  padding: 20px;
  color: white;
  font-family: Arial, sans-serif;
  border-radius: 8px;
}

.button-container {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.data-container {
  background-color: white;
  color: black;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.data-header {
  margin-bottom: 20px;
  font-size: 1.5rem;
  font-weight: bold;
}

.service-info-block {
  background-color: #f9f9f9;
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.service-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.button-group {
  display: flex;
  gap: 10px;
}

.edit-btn {
  background-color: #ffa500;
  color: white;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.add-service-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

input,
textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.save-btn {
  background-color: #4caf50;
  color: white;
}

.loading-message {
  text-align: center;
  font-size: 1rem;
  font-weight: bold;
  color: yellow;
}
</style> -->
<style scoped>
/* service Info Container */
.service-info-container {
  background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%);
  color: black;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

/* Button Container */
.button-container {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  justify-content: center;
}

.action-button {
  background-color: #00b7be;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
}

.action-button:hover {
  background-color: #009f9b;
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Hover effect */
}

.action-button.active {
  background-color: #008080;
  font-weight: 700;
}

/* Search Bar */
.search-bar input {
  padding: 10px;
  margin-right: 15px;
  border-radius: 8px;
  border: 1px solid #ccc;
  width: 220px;
  outline: none;
}

.search-bar button {
  background-color: #008080;
  color: white;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.search-bar button:hover {
  background-color: #00b7be;
}

/* Main Content */
.main-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Data Container */
.data-container {
  background-color: white;
  color: black;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 1000px;
  margin: 0 auto;
}

/* Data Header */
.data-header {
  font-size: 2rem;
  font-weight: 700;
  color: #00b7be;
  margin-bottom: 20px;
  text-align: center;
}

/* service Info Block */
.service-info-block {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.service-info-block h3 {
  font-size: 1.5rem;
  color: #008080;
  margin-bottom: 10px;
}

.service-details {
  font-size: 1rem;
  line-height: 1.5;
  color: #333;
}

/* Button in Data Block */
.block-btn,
.unblock-btn {
  background-color: #ff4444;
  color: white;
}

.cancel-btn {
  background-color: #999;
}

/* Hover Effects for Block & Unblock Buttons */
.block-btn:hover {
  background-color: #ff2222;
}

.unblock-btn:hover {
  background-color: #44b5ff;
}

.cancel-btn:hover {
  background-color: #777;
}

/* Blocking/Unblocking Textarea */
.reason-input {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
  resize: vertical;
  font-size: 1rem;
}

/* Blocking Actions */
.blocking-actions,
.unblocking-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 20px;
}

.loading-message {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
  text-align: center;
}

.edit-btn {
  background-color: #ffa500;
  color: white;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.add-service-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

input,
textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.save-btn {
  background-color: #4caf50;
  color: white;
}

.loading-message {
  text-align: center;
  font-size: 1rem;
  font-weight: bold;
  color: yellow;
}
</style>
