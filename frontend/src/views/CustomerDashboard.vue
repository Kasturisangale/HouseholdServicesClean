<template>
  <div class="dashboard">
    <div class="sidebar">
      <h1 >CUSTOMER DASHBOARD</h1>
      <button class="sidebar-btn" @click="activeSection = 'explore'">Explore Services</button>
      <button class="sidebar-btn" @click="activeSection = 'previous'">View Completed Services</button>
      <button class="sidebar-btn" @click="activeSection = 'assigned'">View Assigned Services</button>
      <button class="sidebar-btn" @click="activeSection = 'requested'">View Requested Services</button>
      <button class="sidebar-btn" @click="activeSection = 'cancelled'">View Cancelled Services</button>
      <button class="sidebar-btn" @click="activeSection = 'professionalwise services'">View ProfessionalWise Services</button>

      <button class="sidebar-btn logout" @click="logout">Logout</button>
    </div>
    <div class="main-content">
      <div v-if="loading">Loading...</div>

      <div v-else>
        <div v-if="activeSection === 'explore'">
          <h2>Explore Services</h2>
        <div class="search-bar">
  <input
    type="text"
    id="searchInput"
    v-model="searchQuery"
    placeholder="Search for a service"
  />
  <button @click="search">Search</button>
</div>
          <div v-if="services.length === 0">
            <p>No services available at the moment.</p>
          </div>
          <div v-else>
            <div v-for="service in services" :key="service.service_id" class="service-item">
              <div class="service-box">
                <p><strong>{{ service.service_name }}</strong></p>
              <p>{{ service.description }}</p>
              <p>Price: INR {{ service.price }}</p>
              <p>Time: {{ service.time_required }}</p>
              <button @click="bookService(service)">Book Now</button>
              </div>
              
            </div>
          </div>
        </div>



      <div v-else-if="activeSection === 'professionalwise services'">
          <h2>ProfessionalWise Services</h2>
          <div class="search-bar">
            <input
              type="text"
              v-model="searchQueryp"
              placeholder="type ID/pincode/name"
            />
            <button @click="searchForProfessionals">Search Professionals</button>          </div>
          <div v-if="professionals.length === 0">
            <p>No professionals available at the moment.</p>
          </div>
          <div v-else>
            <div v-for="professional in filteredProfessionals" :key="professional.professional_id" class="service-item">
              <div class="service-box">
                <p><strong>{{ professional.name }} (ID={{ professional.id }})</strong></p>
                <p><b>Service Type:</b> {{ professional.servicetype }}</p>
                <p><b>Experience:</b> {{ professional.experience }} years</p>
                <p><b>Rating:</b> {{ professional.rating }} Stars</p>
                <p><b>Location:</b> {{ professional.pincode }}</p>
                <p><b>Email:</b> {{ professional.email }}</p>
                <p><b>Phone:</b> {{ professional.phone }}</p>
                <p><b>Verification:</b> {{ professional.verified }}</p>
                <div v-if="professional.services && professional.services.length">
                  <ul>
                    <li v-for="service in professional.services" :key="service.service_id">{{ service.service_name }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>


<div v-else-if="activeSection === 'previous'">
  <h2>Completed Services</h2>
  <div v-if="previousServices.length === 0">
    <p>No previous services found.</p>
  </div>
  <div v-else>
    <div v-for="service in previousServices" :key="service.service_id" class="service-item">
      <div class="service-box">
        <p><strong>{{ service.service_name }}</strong></p>
        <p><b>Request ID:</b> {{ service.request_id }}</p>
        <p><b>Professional Name:</b> {{ service.professional_name }}</p>
        <p><b>Price:</b> INR {{ service.price }}</p>
        <p><b>Time:</b> {{ service.time_required }}</p>
        <p><b>Date of Request:</b> {{ service.date_of_request }}</p>
        <p><b>Date of Completion:</b> {{ service.date_of_completion }}</p>
        <p><b>Remarks given for professional:</b> {{ service.remarks_for_profesional}}</p>
        <p><b>Rating given for professional:</b> {{ service.rating_for_professional }}</p>
        <p><b>GIVE FEEDBACK/UPDATE FEEDBACK-</b></p>
        <p><b>Remarks given by you:</b></p>
        <textarea v-model="service.remarks_for_professional" placeholder="Edit your remarks" rows="3"></textarea>
        <p><b>Rating Given to Professional:</b></p>
        <select v-model="service.rating_for_professional">
          <option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }} Star</option>
        </select>
        <button @click="updateRemarksAndRating(service)">Update</button>
      </div>
    </div>
  </div>
</div>
<div v-else-if="activeSection === 'cancelled'">
  <h2>Cancelled Services</h2>
  <div v-if="cancelledServices.length === 0">
    <p>No cancelled services found.</p>
  </div>
  <div v-else>
    <div v-for="service in cancelledServices" :key="service.service_id" class="service-item">
      <div class="service-box">
        <p><strong>{{ service.service_name }}</strong></p>
        <p><b>Request ID:</b> {{ service.request_id }}</p>
        <p><b>Professional Name:</b> {{ service.professional_name }}</p>
        <p><b>Price:</b> INR {{ service.price }}</p>
        <p><b>Time:</b> {{ service.time_required }}</p>
        <p><b>Date of Request:</b> {{ service.date_of_request }}</p>
        <p><b>The Request was cancelled.</b></p>
      </div>
    </div>
  </div>
</div>

        <div v-else-if="activeSection === 'assigned'">
          <h2>Assigned Services</h2>
          <div v-if="assignedServices.length === 0">
            <p>No assigned services found.</p>
          </div>
          <div v-else>
            <div v-for="service in assignedServices" :key="service.request_id" class="service-item">
              <div class="service-box">
                <p><strong>{{ service.service_name }}</strong></p>
                <p><b>Request ID:</b> {{ service.request_id }}</p>
                <p><b>Professional Name:</b> {{ service.professional_name }}</p>
                <p><b>Price to Pay:</b> INR {{ service.price }}</p>
                <p><b>Expected Time:</b> {{ service.time_required }}</p>
                <p><b>Date of Request:</b> {{ service.date_of_request }}</p>
                <div><button @click="cancelServiceRequest(service.request_id)">Cancel Service</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="activeSection === 'requested'">
          <h2>Requested Services</h2>
          <div v-if="requestedServices.length === 0">
            <p>No requested services found.</p>
          </div>
          <div v-else>
            <div v-for="service in requestedServices" :key="service.request_id" class="service-item">
              <div class="service-box">
                <p><strong>{{ service.service_name }}</strong></p>
                <p><b>Request ID:</b> {{ service.request_id }}</p>
                <p><b>Price you would need to Pay:</b> INR {{ service.price }}</p>
                <p><b>Expected Time:</b> {{ service.time_required }}</p>
                <p><b>Date of Request:</b> {{ service.date_of_request }}</p>
                <p><b>Date of Completion:</b> NA</p>
                <p><b>We ll process your request soon</b></p>
                <button @click="cancelServiceRequest(service.request_id)">Cancel Service</button>
              </div>
            </div>
          </div>
        </div>

        <div v-else>
          

          <p>Welcome, <b>{{ customer.customer_name }}  (ID={{customer.customer_id}})</b>!</p>
          <p>What would you like us to do today?</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "CustomerDashboard",
  data() {
    return {
      customer: {},
      customer_name: "",
      customer_email: "",
      contact_number: "",
      customer_password: "", 
      message: "",
      messageType: "", 
      services: [],
      previousServices: [],
      cancelledServices: [],
      assignedServices: [],
      requestedServices: [],
      activeSection: 'home',
      loading: true,
      searchQuery: "", 
      searchQueryp:"",
      professionals: [], 
    sortedProfessionals: [] 
    };
  },
  computed: {
    filteredProfessionals() {
    const query = this.searchQueryp.toLowerCase().trim();
    if (!query) return this.professionals; 

    return this.professionals.filter((professional) => {
      const nameMatch = professional.name.toLowerCase().includes(query);
      const idMatch = professional.id.toString().includes(query);
      const pincode=professional.pincode.toString().includes(query);
      return nameMatch || idMatch || pincode;
    });
  },
    
  filteredServices() {
   const query = this.searchQuery.toLowerCase().trim();
   if (!query) return this.services; 

   return this.services.filter((service) => {
     const nameMatch = service.service_name.toLowerCase().includes(query);  
     const idMatch = service.service_id.toString().includes(query); 
     return nameMatch || idMatch;
   });
 }

  },
  methods: {
    async searchForProfessionals() {
   const query = this.searchQueryp.trim().toLowerCase();
   if (!query) return;
   this.loading = true;

   const token = localStorage.getItem("token");
   try {
     const response = await axios.get("http://54.242.17.17:5000/api/customers/professionalinfo/search", {
       params: { query },
       headers: {
         Authorization: `Bearer ${token}`,
       },
     });

     if (response.data && response.data.professionals) {
       this.professionals = response.data.professionals;
     } else {
       alert("No professionals found.");
     }
   } catch (error) {
     console.error("Error during search:", error);
     alert("An error occurred while searching for professionals.");
   } finally {
     this.loading = false;
   }
 }
,
    async fetchProfessionalWiseServices() {
    try {
      console.log("FETCHING PRO LSIT")
      const token = localStorage.getItem("token");

      if (!token) {
        alert("You must be logged in to view professional services.");
        return;
      }
      console.log("WE R THERE")
      const response = await axios.get("http://54.242.17.17:5000/api/customer/professionalwise-services", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.data && response.data.professionals) {
        this.professionals = response.data.professionals;
        this.sortProfessionalsByRating();  
      }
    } catch (error) {
      console.error("Error fetching professional services:", error);
    }
  },

  sortProfessionalsByRating() {
    this.sortedProfessionals = this.professionals.sort((a, b) => {
      return parseFloat(b.professional_rating) - parseFloat(a.professional_rating);
    });
  },
    async search() {
      try {
        const searchInput = this.searchQuery.trim();
        if (!searchInput) {
          alert("Please enter a search query.");
          return;
        }
        this.loading = true;

        const token = localStorage.getItem("token");
        const response = await axios.get(`http://54.242.17.17:5000/api/customers/serviceinfo/search`, {
          params: { query: searchInput },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.data && response.data.services) {
          this.services = response.data.services;
        } else {
          alert("No services found.");
        }
      } catch (error) {
        console.error("Error during search:", error);
        alert("An error occurred while searching for services.");
      } finally {
        this.loading = false;
      }
    }
,

    async fetchProfessionals() {
      try {
        const response = await axios.get('http://54.242.17.17:5000/api/professionals');
        this.professionals = response.data;
        this.filteredProfessionals = [...this.professionals];  
      } catch (error) {
        console.error('Error fetching professionals:', error);
      }
    },
    async updateRemarksAndRating(service) {
  if (!service?.request_id) {  
    console.error("Service ID is missing. Cannot proceed.", service);
    alert("Invalid service data. Please try again.");
    return;
  }

  try {
    const token = localStorage.getItem("token");

    if (!token) {
      alert("You must be logged in to update your remarks and rating.");
      return;
    }
    console.log("Serivce id", service.request_id)
    const updatedData = {
      service_id: service.request_id,
      remarks_for_professional: service.remarks_for_professional,
      rating_for_professional: service.rating_for_professional,
    };

    console.log("Payload sent to backend:", updatedData);

    const response = await axios.put("http://54.242.17.17:5000/api/customer/update-service-feedback", updatedData, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200) {
      alert("Remarks and Rating updated successfully.");
      this.fetchPreviousServices();  
    } else {
      alert("There was an issue updating the remarks and rating.");
    }
  } catch (error) {
    console.error("Error updating remarks and rating:", error);
    alert("There was an error processing your update.");
  }
}
,
async fetchCustomerInfo() {
  try {
    console.log("Fetching customer info...");

    this.loading = true;
    const token = localStorage.getItem("token");

    if (!token) {
      alert("You must be logged in to view this page.");
      this.$router.push("/customer/login");
      return;
    }

    console.log("Stored token before request:", token);

    const response = await axios.get("http://54.242.17.17:5000/api/customer-info", {
      headers: { Authorization: `Bearer ${token}` },
    });

    console.log("Response data:", response.data);

    if (response.data.user) {
      this.customer = response.data.user;
    } else {
      alert("No customer data found.");
    }
  } catch (error) {
    console.error("Error fetching customer info:", error);

    const status = error.response?.status;
    if (status === 401) {
      alert("Session expired. Please log in again.");
      this.$router.push("/customer/login");
    } else if (status === 404) {
      alert("Customer not found.");
    } else {
      alert("An unexpected error occurred. Please try again.");
    }
  } finally {
    this.loading = false;
  }
}
,
    async fetchExploreServices() {
      try {
        const token = localStorage.getItem("token");

        if (!token) {
          alert("You must be logged in to explore services.");
          return;
        }

        const response = await axios.get("http://54.242.17.17:5000/api/customer/explore", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data) {
          this.services = response.data.services;
        }
      } catch (error) {
        console.error("Error fetching services:", error);
      }
    },

    async fetchPreviousServices() {
      try {
        const token = localStorage.getItem("token");

        if (!token) {
          alert("You must be logged in to view previous services.");
          return;
        }

        const response = await axios.get("http://54.242.17.17:5000/api/customer/previous-services", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.services) {
          this.previousServices = response.data.services;
        }
      } catch (error) {
        console.error("Error fetching previous services:", error);
      }
    },
    async fetchCancelledServices() {
      try {
        const token = localStorage.getItem("token");

        if (!token) {
          alert("You must be logged in to view assigned services.");
          return;
        }

        const response = await axios.get("http://54.242.17.17:5000/api/customer/cancelled-services", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.services) {
          this.cancelledServices = response.data.services;
        }
      } catch (error) {
        console.error("Error fetching assigned services:", error);
      }
    },
    
    async fetchAssignedServices() {
      try {
        const token = localStorage.getItem("token");

        if (!token) {
          alert("You must be logged in to view assigned services.");
          return;
        }

        const response = await axios.get("http://54.242.17.17:5000/api/customer/assigned-services", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.services) {
          this.assignedServices = response.data.services;
        }
      } catch (error) {
        console.error("Error fetching assigned services:", error);
      }
    },
    

    async fetchRequestedServices() {
      try {
        const token = localStorage.getItem("token");
        console.log("Starting")

        if (!token) {
          alert("You must be logged in to view requested services.");
          return;
        }
        console.log("Almost there")
        const response = await axios.get("http://54.242.17.17:5000/api/customer/requested-services", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.services) {
          this.requestedServices = response.data.services;
        }
      } catch (error) {
        console.error("Error fetching requested services:", error);
      }
    },

    async cancelServiceRequest(requestId) {
      try {
        const token = localStorage.getItem("token");
        console.log("starting")
        if (!token) {
          alert("You must be logged in to cancel a service.");
          return;
        }
        console.log("Almost there")
        console.log("service id:",requestId)
        const response = await axios.put(`http://54.242.17.17:5000/api/customer/cancelservice/${requestId}`, {}, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.status === 200) {
          alert("Service request has been cancelled successfully.");
          this.fetchAssignedServices(); 
        } else {
          alert("There was an issue cancelling the service.");
        }
      } catch (error) {
        console.error("Error cancelling service request:", error);
        alert("There was an error processing your cancellation.");
      }
    },

    async bookService(service) {
      try {
        const token = localStorage.getItem("token");

        if (!token) {
          alert("You must be logged in to book a service.");
          return;
        }

        const bookingData = {
          customer_id: this.customer.customer_id,
          service_id: service.service_id,
          booking_time: new Date().toISOString(),
          
        };
        const response = await axios.post("http://54.242.17.17:5000/api/customer/book-service", bookingData, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.status === 200) {
          alert("Booking successful! We will confirm your request shortly.");
        } else {
          alert("There was an issue with the booking.");
        }
      } catch (error) {
        console.error("Error booking service:", error);
        alert("There was an error processing your booking.");
      }
    },
    

    navigateTo(route) {
      this.$router.push(route);
    },

    logout() {
      localStorage.removeItem("token");
      alert("You have been logged out.");
      this.$router.push("/"); 
    },
  },
  mounted() {
    this.fetchCustomerInfo();
  },
  watch: {
    activeSection(newSection) {
      if (newSection === "explore") {
        this.fetchExploreServices();
      } else if (newSection === "previous") {
        this.fetchPreviousServices();
      } else if (newSection === "cancelled") {
        this.fetchCancelledServices();
      }else if (newSection === "assigned") {
        this.fetchAssignedServices();
      }else if (newSection === "requested") {
        this.fetchRequestedServices();
      }else if (newSection === "professionalwise services"){
        this.fetchProfessionalWiseServices();
      }
    },
  },
};
</script>

<!-- 
<style scoped>
.service-box {
  border: 2px solid #ddd;
  padding: 15px;
  margin: 15px 0;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.service-box p {
  font-size: 1rem;
}

.service-box b {
  color: #4caf50;
}

.dashboard {
  display: flex;
  height: 100vh;
  background-color: #f0f8ff;
  color: #333;
  font-family: Arial, sans-serif;
}

.title {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2rem;
}

.sidebar {
  width: 25%;
  background-color: #00b7be;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.sidebar-btn {
  width: 80%;
  padding: 10px;
  font-size: 1rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.sidebar-btn:hover {
  background-color: #45a049;
}

.logout {
  background-color: #f44336;
}

.logout:hover {
  background-color: #d32f2f;
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
  color: black;
}

.main-content p {
  font-size: 1.2rem;
  margin-bottom: 10px;
}

.service-item {
  margin-bottom: 20px;
}

.service-item p {
  font-size: 1rem;
}

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  background-color: #4caf50;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
.update-profile-section {
  background-color: #ffffff; 
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  max-width: 600px; 
  margin: 20px auto; 
  font-family: 'Arial', sans-serif;
}

.update-profile-section h2 {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  text-align: center;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

.update-profile-section .form-group {
  margin-bottom: 20px;
}

.update-profile-section .form-group label {
  font-size: 16px;
  font-weight: 500;
  color: #555; 
  margin-bottom: 8px;
  display: block;
}

.update-profile-section .form-control {
  width: 100%;
  padding: 12px 15px;
  font-size: 15px;
  border: 1px solid #ccc;
  border-radius: 8px; 
  background-color: #f9f9f9;
  transition: border 0.3s ease, box-shadow 0.3s ease;
}

.update-profile-section .form-control:focus {
  border-color: #007bff; 
  box-shadow: 0 0 8px rgba(0, 123, 255, 0.2);
  outline: none;
  background-color: #fff; 
}

.update-profile-section .btn-primary {
  background-color: #007bff; 
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  width: 100%;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.update-profile-section .btn-primary:hover {
  background-color: #0056b3;
  transform: scale(1.02); 
}

.update-profile-section .btn-primary:active {
  background-color: #004085;
  transform: scale(0.98);
}

.update-profile-section .alert {
  margin-top: 15px;
  padding: 10px 15px;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 500;
}

.update-profile-section .alert.success {
  background-color: #d4edda; 
  color: #155724; 
  border: 1px solid #c3e6cb;
}

.update-profile-section .alert.error {
  background-color: #f8d7da; 
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.professional-box {
  border: 2px solid #ddd;
  padding: 15px;
  margin: 20px 0;
  border-radius: 8px;
  background-color: #fafafa; 
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
}

.professional-box p {
  font-size: 1rem;
  margin-bottom: 10px; 
}

.professional-box b {
  color: #4caf50; 
}

.professional-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.professional-box ul {
  padding-left: 20px;
}

.professional-box ul li {
  margin-bottom: 5px;
  font-size: 1rem;
}

.professional-box .professional-name {
  font-size: 1.2rem;
  font-weight: bold;
}



.dashboard {
  display: flex;
  height: 100vh;
  background-color: #f0f8ff;
  color: #333;
  font-family: Arial, sans-serif;
}

.sidebar {
  width: 25%;
  background-color: #00b7be;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  height: 100%; 
  overflow-y: auto; 
}

.sidebar-btn {
  width: 80%;
  padding: 10px;
  font-size: 1rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.sidebar-btn:hover {
  background-color: #45a049;
}

.logout {
  background-color: #f44336;
}

.logout:hover {
  background-color: #d32f2f;
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding: 20px;
  color: black;
  overflow-y: auto; 
}

.main-content p {
  font-size: 1.2rem;
  margin-bottom: 10px;
}

.service-box {
  border: 2px solid #ddd;
  padding: 15px;
  margin: 15px 0;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.service-item {
  margin-bottom: 20px;
}

.service-item p {
  font-size: 1rem;
}

.service-box b {
  color: #4caf50;
}

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  background-color: #4caf50;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.service-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.service-item .service-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.main-content > div {
  margin-top: 20px;
  max-height: 80vh; 
  overflow-y: auto;
}

.assigned-services {
  display: flex;
  flex-direction: column;
}

.assigned-services .service-item {
  display: block;
}

.dashboard {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

@media screen and (max-width: 768px) {
  .dashboard {
    flex-direction: column;
    height: auto;
  }

  .sidebar {
    width: 100%;
    height: auto;
  }

  .main-content {
    width: 100%;
    height: auto;
  }

  .sidebar-btn {
    width: 100%;
    font-size: 1.1rem;
  }
}

</style> -->
<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Montserrat', sans-serif;
}

.dashboard {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%);
  padding: 20px;
  color: #333;
}

.sidebar {
  width: 260px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar h1 {
  font-size: 1.4rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 10px;
  color: #333;
}

.sidebar-btn {
  padding: 12px 18px;
  background: #f5f7fa;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  color: #333;
  cursor: pointer;
  text-align: left;
  transition: all 0.3s ease;
}

.sidebar-btn:hover {
  background: #dfe8ff;
}

.logout {
  margin-top: auto;
  background: #ff4d4f;
  color: #fff;
}

.logout:hover {
  background: #e60023;
}

.main-content {
  flex: 1;
  background: #ffffff;
  border-radius: 20px;
  padding: 30px;
  margin-left: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 20px;
  font-weight: 600;
  color: #222;
}

.service-item {
  margin-bottom: 24px;
}

.service-box {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
}

.service-box p {
  margin: 6px 0;
}

.service-box textarea {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #ccc;
  margin-bottom: 10px;
  resize: vertical;
}

.service-box select {
  padding: 8px;
  border-radius: 10px;
  border: 1px solid #ccc;
  margin-bottom: 10px;
}

.service-box button {
  padding: 10px 16px;
  background-color: #4caf50;
  border: none;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.service-box button:hover {
  background-color: #388e3c;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.search-bar input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #ccc;
}

.search-bar button {
  background-color: #4caf50;
  color: white;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-bar button:hover {
  background-color: #388e3c;
}

@media (max-width: 768px) {
  .dashboard {
    flex-direction: column;
    padding: 10px;
  }

  .sidebar {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 20px;
  }

}
</style>
