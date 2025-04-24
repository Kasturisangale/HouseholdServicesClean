<template>
    <div>
      <h1>API Data</h1>
      <div v-if="responseData">
        <pre>{{ responseData }}</pre> 
      </div>
      <div v-else>
        <p>Loading data...</p> 
      </div>
    </div>
  </template>
  
  <script>
  import apiClient from '@/services/apiClient';  
  
  export default {
    data() {
      return {
        responseData: null,  
      };
    },
    created() {
      this.fetchData(); 
    },
    methods: {
      async fetchData() {
        try {
          const response = await apiClient.get('/some-endpoint'); 
          this.responseData = response.data;  
        } catch (error) {
          console.error('API call failed:', error);  
        }
      },
    },
  };
  </script>
 
  