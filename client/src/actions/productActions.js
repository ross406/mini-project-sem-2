import axios from 'axios';

import { CLEAR_ERRORS, GET_ERRORS } from './types';

// Add new Product
export const addProduct = (productData) => (dispatch) => {
  dispatch(clearErrors());
  axios
    .post('/api/sell', productData)
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      dispatch({
        type: GET_ERRORS,
        payload: err.response.data,
      });
    });
};

// Clear errors
export const clearErrors = () => {
  return {
    type: CLEAR_ERRORS,
  };
};
