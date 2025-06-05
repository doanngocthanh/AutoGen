import React from 'react';
import { Route, Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

function PrivateRoute({ children }) {
  const { authTokens } = useAuth();

  return authTokens ? children : <Navigate to="/login" />;
}

export default PrivateRoute;