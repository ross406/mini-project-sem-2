import axios from 'axios';

const setAuthToken = (token) => {
  if (token) {
    // Apply to every request
    console.log("token>>>>",token)
    axios.defaults.headers.common['Authorization'] = token;
  } else {
    // Delete Auth Header
    delete axios.defaults.headers.common['Authorization'];
  }
};

export default setAuthToken;
