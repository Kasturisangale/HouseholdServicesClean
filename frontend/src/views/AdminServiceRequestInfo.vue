<template>
    <div class="service-request-info-container">
      <h1>Service Request Information</h1>
  
      <div class="button-container">
        <button
          @click="viewRequests('completed')"
          :class="{ active: activeSection === 'completed' }"
          class="action-button"
        >
          Completed Reqs
        </button>
        <button
          @click="viewRequests('assigned')"
          :class="{ active: activeSection === 'assigned' }"
          class="action-button"
        >
          Assigned Reqs
        </button>
        <button
          @click="viewRequests('requested')"
          :class="{ active: activeSection === 'requested' }"
          class="action-button"
        >
          Requested Reqs
        </button>
        <button
          @click="viewRequests('calledoff')"
          :class="{ active: activeSection === 'calledoff' }"
          class="action-button"
        >
          Cancelled Reqs
        </button>
        <button @click="goBackToDashboard" class="action-button">
          Go Back to Dashboard
        </button>
      <div class="search-bar">
  <input
    type="text"
    id="searchInput"
    v-model="searchQuery"
    placeholder="Search for a service request"
  />
  <button @click="search">Search</button>
</div>
<button @click="exportCSV" class="action-button">
  Export CSV
</button>

      </div>
  
      <div class="main-content">
        <div v-if="loading" class="loading-message">Loading service request data...</div>
  
        <div v-else>
          <div class="data-container">
            <div v-if="activeSection">
              <h2 class="data-header">{{ capitalizeFirstLetter(activeSection) }} Requests</h2>
              <div v-for="request in filteredRequests" :key="request.id" class="service-request-block">
                <h3>Service Request ID: {{ request.service_request_id }}</h3>
  
                <div class="request-details">
                  <div><strong>Service Name:</strong> {{ request.service_name }}</div>
                  <div><strong>Customer Name:</strong> {{ request.customer_name || 'N/A' }}</div>
                  <div v-if="activeSection === 'assigned' || activeSection === 'completed'"><strong>Professional Name:</strong> {{ request.professional_name || 'N/A' }}</div>
                  <div><strong>Service Status:</strong> {{ request.service_status }}</div>
                  <div v-if="activeSection === 'completed'"><strong>Rating for Professional:</strong> {{ request.rating_for_professional }}</div>
                  <div v-if="activeSection === 'completed'"><strong>Rating for Customer:</strong> {{ request.rating_for_customer }}</div>
                  <div v-if="activeSection === 'completed'"><strong>Remarks for Professional:</strong> {{ request.remarks_for_professional || 'N/A' }}</div>
                  <div v-if="activeSection === 'completed'"><strong>Remarks for Customer:</strong> {{ request.remarks_for_customer || 'N/A' }}</div>
                  <div><strong>Date of Request:</strong> {{ request.date_of_request }}</div>
                  <div v-if="activeSection === 'completed'"><strong>Date of Completion:</strong> {{ request.date_of_completion || 'N/A' }}</div>
                  <div v-if="activeSection === 'completed'"><strong>Price:</strong> ₹{{ request.price || 'N/A' }}</div>
  
                  <div class="button-group">
                    <button
                      v-if="(activeSection === 'assigned' || activeSection === 'requested') && request.service_status !== 'closed'"
                      @click="closeRequest(request)"
                      class="action-button close-btn"
                    >
                      Close Request
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  
  <script>
import axios from "axios";

export default {
  name: "AdminServiceRequestInfo",
  data() {
    return {
      searchQuery: "", 
      requests: [], 
      loading: true, 
      activeSection: "completed", 
    };
  },
  computed: {
    filteredSearchRequests() {
    const query = this.searchQuery.toLowerCase().trim();
    if (!query) return this.requests;

    return this.requests.filter((request) => {
      const nameMatch = request.name.toLowerCase().includes(query);
      const idMatch = request.id.toString().includes(query);
      return nameMatch || idMatch;
    });
  },
    filteredRequests() {
      return this.requests.filter((request) => {
        if (this.activeSection === "completed") {
          return request.service_status === "closed";
        } else if (this.activeSection === "assigned") {
          return request.service_status === "assigned";
        } else if (this.activeSection === "requested") {
          return request.service_status === "requested";
        } else if (this.activeSection === "calledoff") {
      return request.service_status === "calledoff"; 
    }
        return false;
      });
    },
  },
  methods: {
    async exportCSV() {
  try {
    const response = await fetch("http://54.242.17.17:5000/export-service-requests", {
      method: "POST"
    });

    if (!response.ok) {
      throw new Error("Failed to trigger CSV export");
    }

    const data = await response.json();
    const taskId = data.task_id;

    alert("CSV export started! Please wait, OK");

    const checkTaskStatus = async () => {
      const statusResponse = await fetch(`http://54.242.17.17:5000/check-task-status/${taskId}`);
      const statusData = await statusResponse.json();

      if (statusData.status === "SUCCESS") {
        alert("CSV export completed! Downloading...");
        window.location.href = `http://54.242.17.17:5000/download-csv/${statusData.filename}`;
      } else if (statusData.status === "failed") {
        alert("CSV export failed. Please try again.");
      } else {
        setTimeout(checkTaskStatus, 2000);  
      }
    };

    checkTaskStatus(); 

  } catch (error) {
    console.error("Error exporting CSV:", error);
    alert("Something went wrong while exporting CSV.");
  }
}
,
    async search() {
  try {
    const searchInput = this.searchQuery.trim();

    if (!searchInput) {
      alert("Please enter a search query.");
      return;
    }

    this.loading = true; 

    const token = localStorage.getItem("jwt_token");
    const response = await axios.get(`http://54.242.17.17:5000/api/admins/requestinfo/search`, {
      params: { query: searchInput },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    
    console.log(response.data, response.data.service_requests);

    if (response.data && response.data.service_requests) {
      this.requests = response.data.service_requests;
    } else {
      alert("No requests found or failed to retrieve requests.");
    }
  } catch (error) {
    console.error("Error during search:", error);
    alert("An error occurred while searching for requests.");
  } finally {
    this.loading = false;
  }
}
,
    async fetchRequests() {
      try {
        const token = localStorage.getItem("jwt_token");
        console.log("JWT Token:", token);

        const response = await axios.get("http://54.242.17.17:5000/api/admins/servicerequests", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        console.log("API Response:", response.data);
        this.requests = response.data.service_requests || [];
      } catch (error) {
        console.error("Error fetching service requests:", error);
        alert("Failed to fetch service requests.");
      } finally {
        this.loading = false;
      }
    },

    async closeRequest(request) {
      try {
        const token = localStorage.getItem("jwt_token");
        console.log("JWT Token (status update):", token);
        console.log(request,request.service_request_id,request['service_request_id']);
        const response = await axios.put(
          `http://54.242.17.17:5000/api/admins/servicerequestclose/${request.service_request_id}`,
          { status: "closed" },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          request.service_status = "closed"; 
          alert("Service request closed.");
        } else {
          alert("Failed to close the service request.");
        }
      } catch (error) {
        console.error("Error closing service request:", error);
        alert("Error closing the service request.");
      }
    },

    viewRequests(section) {
      this.activeSection = section;
    },

    goBackToDashboard() {
      this.$router.push("/admin/dashboard");
    },

    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
  },
  mounted() {
    this.fetchRequests(); 
  },
};
</script>

  
 
  <style scoped>
  /* service-request Info Container */
.service-request-info-container {
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

/* service-request Info Block */
.service-request-info-block {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.service-request-info-block h3 {
  font-size: 1.5rem;
  color: #008080;
  margin-bottom: 10px;
}

.service-request-details {
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
  </style>
  
 
  
<!-- 
  <style scoped>
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
  
  .service-request-info-container {
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
  
  .service-request-block {
    background-color: #f9f9f9;
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .request-details {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .button-group {
    display: flex;
    gap: 10px;
  }
  
  .close-btn {
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
   -->