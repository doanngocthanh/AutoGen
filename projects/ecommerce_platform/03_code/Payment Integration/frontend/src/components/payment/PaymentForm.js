import React, { useState } from 'react';
import { createPaymentVNPay, createPaymentMomo } from '../../services/payment';

const PaymentForm = () => {
  const [amount, setAmount] = useState('');
  const [orderId, setOrderId] = useState('');
  const [paymentUrl, setPaymentUrl] = useState('');

  const handleVNPayPayment = async () => {
    try {
      const data = await createPaymentVNPay({ amount: parseFloat(amount), orderId: orderId });
      setPaymentUrl(data.url);
      window.location.href = data.url;
    } catch (error) {
      console.error(error);
      alert('Failed to create VNPay payment');
    }
  };

  const handleMomoPayment = async () => {
    try {
      const data = await createPaymentMomo({ amount: parseFloat(amount), orderId: orderId });
      if (data.payUrl) {
        setPaymentUrl(data.payUrl);
        window.location.href = data.payUrl;
      } else {
        alert('Failed to create Momo payment: ' + data.message);
      }
    } catch (error) {
      console.error(error);
      alert('Failed to create Momo payment');
    }
  };

  return (
    <div>
      <h2>Payment Integration</h2>
      <div>
        <label>Amount:</label>
        <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
      </div>
      <div>
        <label>Order ID:</label>
        <input type="text" value={orderId} onChange={(e) => setOrderId(e.target.value)} />
      </div>
      <button onClick={handleVNPayPayment}>Pay with VNPay</button>
      <button onClick={handleMomoPayment}>Pay with Momo</button>
      {paymentUrl && (
        <div>
          <a href={paymentUrl} target="_blank" rel="noopener noreferrer">
            Go to Payment
          </a>
        </div>
      )}
    </div>
  );
};

export default PaymentForm;
