<template>
  <div class="professional-info-container">
    <h1>Professional Information</h1>

    <div class="button-container">
      <button
        @click="viewActiveUsers"
        :class="{ active: activeSection === 'activeUsers' }"
        class="action-button"
      >
        View Active Professionals
      </button>
      <button
        @click="viewBlockedUsers"
        :class="{ active: activeSection === 'blockedUsers' }"
        class="action-button"
      >
        View Blocked Professionals
      </button>
      <button @click="goBackToDashboard" class="action-button">
        Go Back to Dashboard
      </button>
      <div class="search-bar">
  <input
    type="text"
    id="searchInput"
    v-model="searchQuery"
    placeholder="Search for a professional"
  />
  <button @click="search">Search</button>
</div>
    </div>

    <div class="main-content">
      <div v-if="loading" class="loading-message">Loading professional data...</div>

      <div v-else>
        <div class="data-container">
          <div v-if="activeSection === 'activeUsers'">
            <h2 class="data-header">Active Professionals</h2>
            <div
              v-for="professional in activeProfessionals"
              :key="professional.id"
              class="professional-info-block"
            >
              <h3>{{ professional.name }}</h3>
              <div class="professional-details">
                <div><strong>Professional ID:</strong> {{ professional.id }}</div>
                <div><strong>Phone:</strong> {{ professional.phone }}</div>
                <div><strong>Service Type:</strong> {{ professional.servicetype }}</div>
                <div><strong>Experience:</strong> {{ professional.experience }}</div>
                <div><strong>Pincode:</strong> {{ professional.pincode }}</div>
                <div><strong>Date Joined:</strong> {{ professional.datejoined }}</div>
                
                <div><strong>Verified:</strong> {{ professional.verified }}</div>
                <div>
                  <button
                    @click="toggleVerification(professional)"
                    class="action-button"
                  >
                    Set Verified to {{ professional.verified ? 'False' : 'True' }}
                  </button>
                </div>

                <div><strong>Rating:</strong> {{ professional.rating }}</div>
                <div v-if="professional.services_requested.length">
                  <strong>Services done:</strong>
                  <div>
                    [
                    <span
                      v-for="(service, index) in professional.services_requested"
                      :key="index"
                      :style="{ color: service.color }"
                    >
                      {{ service.service_name }}{{ index < professional.services_requested.length - 1 ? ', ' : '' }}
                    </span>
                    ]
                  </div>
                </div>

                <div v-if="!professional.blockingInProgress">
                  <button @click="startBlockingProfessional(professional)" class="action-button block-btn">
                    Block Professional
                  </button>
                </div>

                <div v-if="professional.blockingInProgress">
                  <textarea
                    v-model="professional.blocked_reason"
                    placeholder="Enter reason for blocking the professional"
                    rows="4"
                    cols="50"
                    class="reason-input"
                  ></textarea>
                  <div class="blocking-actions">
                    <button @click="saveBlockingReason(professional)" class="action-button">Save Reason</button>
                    <button @click="cancelBlockingProfessional(professional)" class="action-button cancel-btn">Cancel</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeSection === 'blockedUsers'">
            <h2 class="data-header">Blocked Professionals</h2>
            <div
              v-for="professional in blockedProfessionals"
              :key="professional.id"
              class="professional-info-block"
            >
              <h3>{{ professional.name }}</h3>
              <div class="professional-details">
                <div><strong>Professional ID:</strong> {{ professional.id }}</div>
                <div><strong>Phone:</strong> {{ professional.phone }}</div>
                <div><strong>Service Type:</strong> {{ professional.service_type }}</div>
                <div><strong>Experience:</strong> {{ professional.experience }}</div>
                <div><strong>Pincode:</strong> {{ professional.pincode }}</div>
                <div><strong>Date Joined:</strong> {{ professional.datejoined }}</div>
                <div><strong>Verified:</strong> {{ professional.verified }}</div>
                <p><strong>Blocked Reason:</strong> {{ professional.reason_for_blocking }}</p>

                <div v-if="professional.services_requested.length">
                  <strong>Services Requested:</strong>
                  <div>
                    [
                    <span
                      v-for="(service, index) in professional.services_requested"
                      :key="index"
                      :style="{ color: service.color }"
                    >
                      {{ service.service_name }}{{ index < professional.services_requested.length - 1 ? ', ' : '' }}
                    </span>
                    ]
                  </div>
                </div>

                <div v-if="!professional.unblockingInProgress">
                  <button @click="startUnblockingProfessional(professional)" class="action-button unblock-btn">
                    Unblock Professional
                  </button>
                </div>

                <div v-if="professional.unblockingInProgress">
                  <div class="unblocking-actions">
                    <button @click="saveUnblockingReason(professional)" class="action-button">Confirm Unblock</button>
                    <button @click="cancelUnblockingProfessional(professional)" class="action-button cancel-btn">
                      Cancel
                    </button>
                  </div>
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
  name: "AdminProfessionalInfo",
  data() {
    return {
      professionals: [],
      loading: true,
      activeSection: "activeUsers",
      searchQuery: "", 
    };
  },
  computed: {
    filteredProfessionals() {
    const query = this.searchQuery.toLowerCase().trim();
    if (!query) return this.professionals; 

    return this.professionals.filter((professional) => {
      const nameMatch = professional.name.toLowerCase().includes(query);
      const idMatch = professional.id.toString().includes(query);
      return nameMatch || idMatch;
    });
  },
    activeProfessionals() {
      return this.professionals.filter((professional) => !professional.blocked);
    },
    blockedProfessionals() {
      return this.professionals.filter((professional) => professional.blocked);
    },
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
    const response = await axios.get(`http://54.242.17.17:5000/api/admins/professionalinfo/search`, {
      params: { query: searchInput },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.data && response.data.professionals) {
      this.professionals = response.data.professionals; 
    } else {
      alert("No professionals found or failed to retrieve professionals.");
    }
  } catch (error) {
    console.error("Error during search:", error);
    alert("An error occurred while searching for professionals.");
  } finally {
    this.loading = false; 
  }
}
,
    async toggleVerification(professional) {
      const newVerificationStatus = !professional.verified;
      
      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.post(
          `http://54.242.17.17:5000/api/admins/professionalinfo/updateverification/${professional.id}`,
          { verified: newVerificationStatus },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          professional.verified = newVerificationStatus; 
          alert(`Professional verification status updated to ${newVerificationStatus ? 'True' : 'False'}.`);
        } else {
          alert("Failed to update the verification status.");
        }
      } catch (error) {
        console.error("Error updating verification status:", error);
        alert("Error updating verification status.");
      }
    },

    async fetchProfessionalData() {
      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.get("http://54.242.17.17:5000/api/admins/professionalinfo", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        this.professionals = response.data.professionals.map((professional) => {
          professional.services_requested = professional.services_requested.map((service) => {
            let color = "black";
            switch (service.status.toLowerCase()) {
              case "assigned":
                color = "green";
                break;
              case "closed":
                color = "red";
                break;
              default:
                color = "black";
                break;
            }
            return { ...service, color };
          });

          professional.blockingInProgress = false;
          professional.blocked = professional.status === "blocked";  
          professional.unblockingInProgress = false; 
          return professional;
        });
      } catch (error) {
        console.error("Error fetching professional data:", error);
        alert("Failed to fetch professional data.");
      } finally {
        this.loading = false;
      }
    },

    startBlockingProfessional(professional) {
      professional.blockingInProgress = true;
      professional.blocked_reason = "";
    },

    cancelBlockingProfessional(professional) {
      professional.blockingInProgress = false;
      professional.blocked_reason = "";
    },

    async saveBlockingReason(professional) {
      if (!professional.blocked_reason.trim()) {
        alert("Please provide a reason for blocking.");
        return;
      }

      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.post(
          `http://54.242.17.17:5000/api/admins/professionalinfo/blockprofessional/${professional.id}`,
          { blocked_reason: professional.blocked_reason },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          professional.blocked = true;
          professional.blockingInProgress = false;
          alert("Professional has been successfully blocked.");
        } else {
          alert("Failed to block the professional.");
        }
      } catch (error) {
        console.error("Error blocking professional:", error);
        alert("Error blocking the professional.");
      }
    },

    startUnblockingProfessional(professional) {
      professional.unblockingInProgress = true;
    },

    cancelUnblockingProfessional(professional) {
      professional.unblockingInProgress = false;
    },

    async saveUnblockingReason(professional) {
      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.post(
          `http://54.242.17.17:5000/api/admins/professionalinfo/unblockprofessional/${professional.id}`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          professional.blocked = false;
          professional.blocked_reason = "Not Applicable";
          professional.unblockingInProgress = false;
          alert("Professional has been successfully unblocked.");
        } else {
          alert("Failed to unblock the professional.");
        }
      } catch (error) {
        console.error("Error unblocking professional:", error);
        alert("Error unblocking the professional.");
      }
    },

    viewActiveUsers() {
      this.activeSection = "activeUsers";
    },

    viewBlockedUsers() {
      this.activeSection = "blockedUsers";
    },

    goBackToDashboard() {
      this.$router.push("/admin/dashboard"); 
    },
  },
  mounted() {
    this.fetchProfessionalData(); 
  },
};
</script>

  
<style scoped>
/* professional Info Container */
.professional-info-container {
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

/* professional Info Block */
.professional-info-block {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.professional-info-block h3 {
  font-size: 1.5rem;
  color: #008080;
  margin-bottom: 10px;
}

.professional-details {
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
