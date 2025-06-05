import React from 'react';
import { Typography, Container } from '@mui/material';

function Orders() {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Orders
      </Typography>
      <Typography variant="body1">
        Manage your orders here.
      </Typography>
    </Container>
  );
}

export default Orders;