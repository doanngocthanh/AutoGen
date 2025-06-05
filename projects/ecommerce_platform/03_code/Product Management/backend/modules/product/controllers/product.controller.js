const Product = require('../models/product.model');

// Create a new product
exports.create = async (req, res) => {
  try {
    const product = new Product(req.body);
    const savedProduct = await product.save();
    res.status(201).send(savedProduct);
  } catch (error) {
    res.status(500).send({ message: error.message || 'Some error occurred while creating the Product.' });
  }
};

// Retrieve all products
exports.findAll = async (req, res) => {
  try {
    const products = await Product.find();
    res.send(products);
  } catch (error) {
    res.status(500).send({ message: error.message || 'Some error occurred while retrieving products.' });
  }
};

// Find a single product with an id
exports.findOne = async (req, res) => {
  try {
    const product = await Product.findById(req.params.id);
    if (!product) {
      return res.status(404).send({ message: 'Product not found with id ' + req.params.id });
    }
    res.send(product);
  } catch (error) {
    if (error.kind === 'ObjectId') {
      return res.status(404).send({ message: 'Product not found with id ' + req.params.id });
    }
    res.status(500).send({ message: 'Error retrieving product with id ' + req.params.id });
  }
};

// Update a product identified by the id in the request
exports.update = async (req, res) => {
  try {
    const product = await Product.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!product) {
      return res.status(404).send({ message: 'Product not found with id ' + req.params.id });
    }
    res.send(product);
  } catch (error) {
    if (error.kind === 'ObjectId') {
      return res.status(404).send({ message: 'Product not found with id ' + req.params.id });
    }
    res.status(500).send({ message: 'Error updating product with id ' + req.params.id });
  }
};

// Delete a product with the specified id in the request
exports.delete = async (req, res) => {
  try {
    const product = await Product.findByIdAndRemove(req.params.id);
    if (!product) {
      return res.status(404).send({ message: 'Product not found with id ' + req.params.id });
    }
    res.send({ message: 'Product deleted successfully!' });
  } catch (error) {
    if (error.kind === 'ObjectId' || error.name === 'NotFound') {
      return res.status(404).send({ message: 'Product not found with id ' + req.params.id });
    }
    res.status(500).send({ message: 'Could not delete product with id ' + req.params.id });
  }
};