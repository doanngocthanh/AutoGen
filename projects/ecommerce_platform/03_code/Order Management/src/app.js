const express = require('express');
const cors = require('cors');
const productRoutes = require('./product_management/routes/productRoutes');
const categoryRoutes = require('./category_management/routes/categoryRoutes');
const userRoutes = require('./user_authentication/routes/userRoutes');
const orderRoutes = require('./order_management/routes/orderRoutes');

const app = express();

app.use(cors());
app.use(express.json());

app.use('/products', productRoutes);
app.use('/categories', categoryRoutes);
app.use('/users', userRoutes);
app.use('/orders', orderRoutes);

module.exports = app;