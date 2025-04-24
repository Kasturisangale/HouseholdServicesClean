<template>
    <div>
      <h2>Available Services</h2>
      <ul>
        <li v-for="service in services" :key="service.id">
          <h3>{{ service.name }}</h3>
          <p>{{ service.description }}</p>
          <p>Price: ${{ service.price }}</p>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        services: []
      };
    },
    created() {
      axios.get('http://54.242.17.17:5000/api/services')
        .then(response => {
          this.services = response.data;
        })
        .catch(error => {
          console.error("There was an error fetching the services:", error);
        });
    }
  };
  </script>
  