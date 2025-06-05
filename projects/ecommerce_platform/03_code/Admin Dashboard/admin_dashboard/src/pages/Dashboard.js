import React from 'react';
import { Typography, Container } from '@mui/material';

function Dashboard() {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Admin Dashboard
      </Typography>
      <Typography variant="body1">
        Welcome to the admin dashboard. You can manage products, orders, and users here.
      </Typography>
    </Container>
  );
}

export default Dashboard;