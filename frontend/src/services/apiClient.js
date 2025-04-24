import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://54.242.17.17:5000',  
  headers: {
    'Content-Type': 'application/json'
  }
});

export default apiClient;
