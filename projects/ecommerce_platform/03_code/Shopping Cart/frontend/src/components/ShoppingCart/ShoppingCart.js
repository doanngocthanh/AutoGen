import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ShoppingCart = () => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCart = async () => {
      try {
        const token = localStorage.getItem('token'); // Assuming token is stored in localStorage
        const response = await axios.get('/api/shopping_cart', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setCart(response.data);
      } catch (err) {
        setError(err.message || 'Failed to fetch cart');
      } finally {
        setLoading(false);
      }
    };

    fetchCart();
  }, []);

  if (loading) {
    return <p>Loading cart...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  if (!cart) {
    return <p>Cart is empty.</p>;
  }

  return (
    <div>
      <h2>Shopping Cart</h2>
      <ul>
        {cart.items.map((item) => (
          <li key={item.product_id._id}>
            {item.product_id.name} - Quantity: {item.quantity} - Price: {item.price}
          </li>
        ))}
      </ul>
      <p>Total: {cart.total_amount}</p>
    </div>
  );
};

export default ShoppingCart;