<template>
  <div class="dashboard">
    <div class="sidebar">
      <h1 >PROFESSIONAL DASHBOARD</h1>
      <button class="sidebar-btn" @click="activeSection = 'explore'">Explore Opportunities</button>
      <button class="sidebar-btn" @click="activeSection = 'previous'">View Completed Services</button>
      <button class="sidebar-btn" @click="activeSection = 'assigned'">View Assigned Services</button>
      <button class="sidebar-btn" @click="activeSection = 'cancelled'">View Cancelled Services</button>
      <button class="sidebar-btn logout" @click="logout">Logout</button>
    </div>

    <div class="main-content">
      <div v-if="loading">Loading...</div>

<div v-else-if="activeSection === 'explore'">
  <h2>Explore Opportunities</h2>
  <div v-if="service_requests.length === 0">
    <p>No services available at the moment.</p>
  </div>
  <div v-else>
    <div v-for="serviceRequest in service_requests" :key="serviceRequest.service_request_id" class="service-item">
      <div class="service-box">
        <p><strong>{{ serviceRequest.service_name }}</strong></p>
        <p>Customer: {{ serviceRequest.customer_name }}</p>
        <p>Date of Request: {{ serviceRequest.date_of_request }}</p>
        <p>Status: {{ serviceRequest.service_status }}</p>
        <button @click="bookService(serviceRequest)">ACCEPT</button>
      </div>
    </div>
  </div>
</div>


     
      <div v-else-if="activeSection === 'previous'">
        <h2>Previous Services</h2>
        <div v-if="previousServices.length === 0">
          <p>No previous services found.</p>
        </div>
        <div v-else>
          <div v-for="service in previousServices" :key="service.service_id" class="service-item">
            <div class="service-box">
              <p><strong>{{ service.service_name }}</strong></p>
              <p><b>Request ID:</b> {{ service.request_id }}</p>
              <p><b>Customer Name:</b> {{ service.customer_name }}</p>
              <p><b>Date of Request:</b> {{ service.date_of_request }}</p>
              <p><b>Date of Completion:</b> {{ service.date_of_completion }}</p>
              <p><b>Remarks given for professional:</b> {{ service.remarks_for_professional || "NA "}} </p>
              <p><b>Rating given for professional:</b> {{ service.rating_for_professional }}</p>
              <p><b>Remarks for the customer given by you:</b> {{ service.remarks_for_customer || "NA "}}</p>
              <p><b>Rating given for customer:</b> {{ service.rating_for_customer }}</p>
              <p><b>Do you want to update it? Here's your opportunity.</b></p>
              <p><b>Remarks given by you:</b></p>
              <textarea v-model="service.remarks_for_customer" placeholder="Edit your remarks" rows="3"></textarea>
              <p><b>Rating Given to Professional:</b></p>
              <select v-model="service.rating_for_customer">
                <option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }} Star</option>
              </select>
              <button @click="updateRemarksAndRating(service)">Update</button>
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
    <div v-for="service in assignedServices" :key="service.service_request_id" class="service-item">
      <div class="service-box">
        <p><strong>{{ service.service_name }}</strong></p>
        <p><b>Request ID:</b> {{ service.request_id }}</p>
        <p><b>Customer Name:</b> {{ service.customer_name }}</p>
        <p><b>Price to Pay:</b> INR {{ service.price }}</p>
        <p><b>Expected Time:</b> {{ service.time_required }}</p>
        <p><b>Date of Request:</b> {{ service.date_of_request }}</p>
        <p><b>Date of Completion:</b> {{ service.date_of_completion || 'NA' }}</p>
        <p><b>when done with the service, give us the feedback and mark it as done</b></p>
        <p><b>Give us feedback about your experience:</b></p>
        <textarea v-model="service.remarks_for_customer" placeholder="Edit your remarks" rows="3"></textarea>
        <p><b>Rating Given to Customer:</b></p>
        <select v-model="service.rating_for_customer">
          <option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }} Star</option>
        </select>
        <button @click="updateRemarksAndRating(service)">MARK DONE</button>
        <div>
          <button @click="cancelServiceRequest(service.request_id)">Cancel Service</button>
        </div>
      </div>
    </div>
  </div>
</div>

<div v-else-if="activeSection === 'cancelled'">
  <h2>Cancelled Services-</h2>
  <h3>(The services cancelled which were assigned to you)</h3>
  <div v-if="cancelledServices.length === 0">
    <p>No cancelled services found.</p>
  </div>
  <div v-else>
    <div v-for="service in cancelledServices" :key="service.service_request_id" class="service-item">
      <div class="service-box">
        <p><strong>{{ service.service_name }}</strong></p>
        <p><b>Request ID:</b> {{ service.request_id }}</p>
        <p><b>Customer Name:</b> {{ service.customer_name }}</p>
        <p><b>Service Price:</b> INR {{ service.price }}</p>
        <p><b>Expected Time:</b> {{ service.time_required }}</p>
        <p><b>Date of Request:</b> {{ service.date_of_request }}</p>
        <p><b>The service request was cancelled.</b></p>

        <div>
        </div>
      </div>
    </div>
  </div>
</div>

      <div v-else>
        <p>Welcome, <b>{{ professional.professional_name }} (ID={{ professional.professional_id }})</b>!</p>
        <p>Let's get to work!</p>
      </div>
    </div>
  </div>
</template>


<script>
import axios from "axios";

export default {
  name: "ProfessionalDashboard",
  data() {
    return {
      professional: {},
      professional_name: "",
      professional_email: "",
      professional_number: "",
      professional_password: "",
      message: "",
      messageType: "", 
      service_requests: {},
      previousServices: [],
      assignedServices: [],
      cancelledServices: [],
      activeSection: 'home',
      loading: true,
    };
  },
  methods: {
    
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
      remarks_for_customer: service.remarks_for_customer,
      rating_for_customer: service.rating_for_customer,
    };

    console.log("Payload sent to backenddddd:", updatedData);

    const response = await axios.put("http://54.242.17.17:5000/api/professional/update-service-feedback", updatedData, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200) {
      alert("Updated successfully.");
      this.fetchPreviousServices();  
    } else {
      alert("There was an issue updating.");
    }
  } catch (error) {
    console.error("Error updating :", error);
    alert("There was an error processing your update.");
  }
}
,
    async fetchProfessionalInfo() {
      try {
        this.loading = true;
        const token = localStorage.getItem("token");

        if (!token) {
          alert("You must be logged in to view this page.");
          this.$router.push("/professional/login");
          return;
        }

        const response = await axios.get("http://54.242.17.17:5000/api/professional-info", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.user) {
          this.professional = response.data.user;
        }
      } catch (error) {
        console.error("Error fetching customer info:", error);
        alert("Error fetching customer info.");
      } finally {
        this.loading = false;
      }
    },

    async fetchExploreServices() {
  try {
    const token = localStorage.getItem("token");

    if (!token) {
      alert("You must be logged in to explore services.");
      return;
    }

    const response = await axios.get("http://54.242.17.17:5000/api/professional/explore", {
      headers: { Authorization: `Bearer ${token}` },
    });

    console.log("The data received:", response.data);

    if (response.data && response.data.service_requests) {
      this.service_requests = response.data.service_requests; 
    } else {
      this.service_requests = []; 
    }
  } catch (error) {
    console.error("Error fetching services:", error);
    this.service_requests = []; 
  }
}
,

async fetchPreviousServices() {
  try {
    const token = localStorage.getItem("token");

    if (!token) {
      alert("You must be logged in to view previous services.");
      return;
    }

    const response = await axios.get("http://54.242.17.17:5000/api/professional/previous-services", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.data.services) {
      this.previousServices = response.data.services;
    }
  } catch (error) {
    console.error("Error fetching previous services:", error);
  }
}
,

    async fetchAssignedServices() {
      try {
        const token = localStorage.getItem("token");

        if (!token) {
          alert("You must be logged in to view assigned services.");
          return;
        }

        const response = await axios.get("http://54.242.17.17:5000/api/professional/assigned-services", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.services) {
          this.assignedServices = response.data.services;
        }
      } catch (error) {
        console.error("Error fetching assigned services:", error);
      }
    },

    async fetchCancelledServices() {
      try {
        const token = localStorage.getItem("token");

        if (!token) {
          alert("You must be logged in to view assigned services.");
          return;
        }

        const response = await axios.get("http://54.242.17.17:5000/api/professional/cancelled-services", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.services) {
          this.cancelledServices = response.data.services;
        }
      } catch (error) {
        console.error("Error fetching assigned services:", error);
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
        const response = await axios.put(`http://54.242.17.17:5000/api/professional/cancelservice/${requestId}`, {}, {
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

    async bookService(serviceRequest) {
  try {
    const token = localStorage.getItem("token");

    if (!token) {
      alert("You must be logged in to book a service.");
      return;
    }

    const bookingData = {
      professional_id: this.professional.professional_id,  
      service_status: 'assigned',  
    };

    const response = await axios.put(`http://54.242.17.17:5000/api/professional/assign-service/${serviceRequest.service_request_id}`, bookingData, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200) {
      alert("Service successfully assigned!");
      serviceRequest.service_status = 'assigned';  
      serviceRequest.professional_id = this.professional.professional_id; 
    } else {
      alert("There was an issue assigning the service.");
    }
  } catch (error) {
    console.error("Error assigning service:", error);
    alert("There was an error processing the assignment.");
  }
}
,
    

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
    this.fetchProfessionalInfo();
  },
  watch: {
    activeSection(newSection) {
      if (newSection === "explore") {
        this.fetchExploreServices();
      } else if (newSection === "previous") {
        this.fetchPreviousServices();
      } else if (newSection === "assigned") {
        this.fetchAssignedServices();
      } else if (newSection === "cancelled") {
        this.fetchCancelledServices();
      }
    },
  },
};
</script>


<!-- <style scoped>
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


.title {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2rem;
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
</style>

 -->
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
 