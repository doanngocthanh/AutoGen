import React from 'react';
import { Typography, Container } from '@mui/material';

function Products() {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Products
      </Typography>
      <Typography variant="body1">
        Manage your products here.
      </Typography>
    </Container>
  );
}

export default Products;