import React from 'react';
import { Typography, Container } from '@mui/material';

function Users() {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Users
      </Typography>
      <Typography variant="body1">
        Manage your users here.
      </Typography>
    </Container>
  );
}

export default Users;