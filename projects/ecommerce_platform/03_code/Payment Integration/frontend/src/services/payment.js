import axios from 'axios';

const API_URL = 'http://localhost:3000/payment'; // Replace with your backend API URL

export const createPaymentVNPay = async (paymentData) => {
  try {
    const response = await axios.post(`${API_URL}/vnpay/create_payment`, paymentData);
    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const createPaymentMomo = async (paymentData) => {
  try {
    const response = await axios.post(`${API_URL}/momo/create_payment`, paymentData);
    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
