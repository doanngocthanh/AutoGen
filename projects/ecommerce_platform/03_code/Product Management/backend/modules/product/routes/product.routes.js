const express = require('express');
const router = express.Router();
const products = require('../controllers/product.controller');

// Create a new Product
router.post('/', products.create);

// Retrieve all Products
router.get('/', products.findAll);

// Retrieve a single Product with productId
router.get('/:id', products.findOne);

// Update a Product with productId
router.put('/:id', products.update);

// Delete a Product with productId
router.delete('/:id', products.delete);

module.exports = router;