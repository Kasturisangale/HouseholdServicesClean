<template>
  <div class="customer-info-container">
    <h1>Customer Information</h1>

    <div class="button-container">
      <button
        @click="viewActiveUsers"
        :class="{ active: activeSection === 'activeUsers' }"
        class="action-button"
      >
        View Active Users
      </button>
      <button
        @click="viewBlockedUsers"
        :class="{ active: activeSection === 'blockedUsers' }"
        class="action-button"
      >
        View Blocked Users
      </button>
      <button @click="goBackToDashboard" class="action-button">
        Go Back to Dashboard
      </button>

      <div class="search-bar">
        <input
          type="text"
          id="searchInput"
          v-model="searchQuery"
          placeholder="Search for a customer"
        />
        <button @click="search">Search</button>
      </div>
    </div>

    <div class="main-content">
      <div v-if="loading" class="loading-message">Loading customer data...</div>

      <div v-else>
        <div class="data-container">
          <div v-if="activeSection === 'activeUsers'">
            <h2 class="data-header">Active Users</h2>
            <div
              v-for="customer in activeCustomers"
              :key="customer.id"
              class="customer-info-block"
            >
              <h3>{{ customer.name }}</h3>
              <div class="customer-details">
                <div><strong>Customer ID:</strong> {{ customer.id }}</div>
                <div><strong>Phone:</strong> {{ customer.phone }}</div>
                <div><strong>Email:</strong> {{ customer.email }}</div>
                <div><strong>Rating:</strong> {{ customer.rating }}</div>

                <div v-if="customer.services_requested.length">
                  <strong>Services Requested:</strong>
                  <div>
                    [
                    <span
                      v-for="(service, index) in customer.services_requested"
                      :key="index"
                      :style="{ color: service.color }"
                    >
                      {{ service.service_name }}{{ index < customer.services_requested.length - 1 ? ', ' : '' }}
                    </span>
                    ]
                  </div>
                </div>

                <div v-if="!customer.blockingInProgress">
                  <button @click="startBlockingCustomer(customer)" class="action-button block-btn">
                    Block Customer
                  </button>
                </div>

                <div v-if="customer.blockingInProgress">
                  <textarea
                    v-model="customer.blocked_reason"
                    placeholder="Enter reason for blocking the customer"
                    rows="4"
                    cols="50"
                    class="reason-input"
                  ></textarea>
                  <div class="blocking-actions">
                    <button @click="saveBlockingReason(customer)" class="action-button">Save Reason</button>
                    <button @click="cancelBlockingCustomer(customer)" class="action-button cancel-btn">Cancel</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="activeSection === 'blockedUsers'">
            <h2 class="data-header">Blocked Users</h2>
            <div
              v-for="customer in blockedCustomers"
              :key="customer.id"
              class="customer-info-block"
            >
              <h3>{{ customer.name }}</h3>
              <div class="customer-details">
                <div><strong>Customer ID:</strong> {{ customer.id }}</div>
                <div><strong>Phone:</strong> {{ customer.phone }}</div>
                <div><strong>Email:</strong> {{ customer.email }}</div>
                <div><strong>Rating:</strong> {{ customer.rating }}</div>
                <p><strong>Blocked Reason:</strong> {{ customer.reason_for_blocking }}</p>
                <div v-if="customer.services_requested.length">
                  <strong>Services Requested:</strong>
                  <div>
                    [
                    <span
                      v-for="(service, index) in customer.services_requested"
                      :key="index"
                      :style="{ color: service.color }"
                    >
                      {{ service.service_name }}{{ index < customer.services_requested.length - 1 ? ', ' : '' }}
                    </span>
                    ]
                  </div>
                </div>
                <div v-if="!customer.unblockingInProgress">
                  <button @click="startUnblockingCustomer(customer)" class="action-button unblock-btn">
                    Unblock Customer
                  </button>
                </div>

                <div v-if="customer.unblockingInProgress">
                  <div class="unblocking-actions">
                    <button @click="saveUnblockingReason(customer)" class="action-button">Confirm Unblock</button>
                    <button @click="cancelUnblockingCustomer(customer)" class="action-button cancel-btn">
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
  name: "AdminCustomerInfo",
  data() {
    return {
      customers: [],
      loading: true,
      activeSection: "activeUsers",
      searchQuery: "",
    };
  },
  computed: {
    filteredCustomers() {
      const query = this.searchQuery.toLowerCase().trim();
      if (!query) return this.customers;

      return this.customers.filter((customer) => {
        const nameMatch = customer.name.toLowerCase().includes(query);
        const idMatch = customer.id.toString().includes(query);
        return nameMatch || idMatch;
      });
    },
    activeCustomers() {
      return this.customers.filter((customer) => !customer.blocked);
    },
    blockedCustomers() {
      return this.customers.filter((customer) => customer.blocked);
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
        const response = await axios.get(`http://54.242.17.17:5000/api/admins/customerinfo/search`, {
          params: { query: searchInput },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.data && response.data.customers) {
          this.customers = response.data.customers;
        } else {
          alert("No customers found or failed to retrieve customers.");
        }
      } catch (error) {
        console.error("Error during search:", error);
        alert("An error occurred while searching for customers.");
      } finally {
        this.loading = false;
      }
    },
    async fetchCustomerData() {
      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.get("http://54.242.17.17:5000/api/admins/customerinfo", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        this.customers = response.data.customers.map((customer) => {
          customer.services_requested = customer.services_requested.map((service) => {
            let color = "black";
            switch (service.status.toLowerCase()) {
              case "requested":
                color = "yellow";
                break;
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

          customer.blockingInProgress = false;
          customer.blocked = customer.status === "blocked";  
          customer.unblockingInProgress = false; 
          return customer;
        });
      } catch (error) {
        console.error("Error fetching customer data:", error);
        alert("Failed to fetch customer data.");
      } finally {
        this.loading = false;
      }
    },

    startBlockingCustomer(customer) {
      customer.blockingInProgress = true;
      customer.blocked_reason = "";
    },

    cancelBlockingCustomer(customer) {
      customer.blockingInProgress = false;
      customer.blocked_reason = "";
    },

    async saveBlockingReason(customer) {
      if (!customer.blocked_reason.trim()) {
        alert("Please provide a reason for blocking.");
        return;
      }

      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.post(
          `http://54.242.17.17:5000/api/admins/customerinfo/blockcustomer/${customer.id}`,
          { blocked_reason: customer.blocked_reason },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          customer.blocked = true;
          customer.blockingInProgress = false;
          alert("Customer has been successfully blocked.");
        } else {
          alert("Failed to block the customer.");
        }
      } catch (error) {
        console.error("Error blocking customer:", error);
        alert("Error blocking the customer.");
      }
    },

    startUnblockingCustomer(customer) {
      customer.unblockingInProgress = true;
    },

    cancelUnblockingCustomer(customer) {
      customer.unblockingInProgress = false;
    },

    async saveUnblockingReason(customer) {
      try {
        const token = localStorage.getItem("jwt_token");
        const response = await axios.post(
          `http://54.242.17.17:5000/api/admins/customerinfo/unblockcustomer/${customer.id}`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          customer.blocked = false;
          customer.blocked_reason = "Not Applicable";
          customer.unblockingInProgress = false;
          alert("Customer has been successfully unblocked.");
        } else {
          alert("Failed to unblock the customer.");
        }
      } catch (error) {
        console.error("Error unblocking customer:", error);
        alert("Error unblocking the customer.");
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
    this.fetchCustomerData();
  },
};
</script>

<style scoped>
/* Customer Info Container */
.customer-info-container {
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

/* Customer Info Block */
.customer-info-block {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.customer-info-block h3 {
  font-size: 1.5rem;
  color: #008080;
  margin-bottom: 10px;
}

.customer-details {
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
