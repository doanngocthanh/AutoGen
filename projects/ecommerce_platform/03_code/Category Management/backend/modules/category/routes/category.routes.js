const express = require('express');
const router = express.Router();
const categoryController = require('../controllers/category.controller');

// Create a new category
router.post('/', categoryController.create);

// Get all categories
router.get('/', categoryController.findAll);

// Get a category by ID
router.get('/:id', categoryController.findOne);

// Update a category by ID
router.put('/:id', categoryController.update);

// Delete a category by ID
router.delete('/:id', categoryController.delete);

module.exports = router;