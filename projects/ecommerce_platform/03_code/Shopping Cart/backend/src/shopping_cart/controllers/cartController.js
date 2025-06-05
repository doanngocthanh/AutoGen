const Cart = require('../models/cart');
const Product = require('../../product/models/product');

exports.getCart = async (req, res) => {
  try {
    const userId = req.user.id; // Assuming user ID is available in req.user
    const cart = await Cart.findOne({ user_id: userId }).populate('items.product_id');

    if (!cart) {
      return res.status(404).json({ message: 'Cart not found' });
    }

    res.status(200).json(cart);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.addItemToCart = async (req, res) => {
  try {
    const userId = req.user.id;
    const { product_id, quantity } = req.body;

    const product = await Product.findById(product_id);
    if (!product) {
      return res.status(404).json({ message: 'Product not found' });
    }

    let cart = await Cart.findOne({ user_id: userId });

    if (!cart) {
      cart = new Cart({ user_id: userId, items: [], total_amount: 0 });
    }

    const existingItemIndex = cart.items.findIndex(item => item.product_id.toString() === product_id);

    if (existingItemIndex > -1) {
      cart.items[existingItemIndex].quantity += quantity;
    } else {
      cart.items.push({ product_id: product_id, quantity: quantity, price: product.price });
    }

    cart.total_amount = cart.items.reduce((total, item) => total + (item.quantity * item.price), 0);

    await cart.save();

    res.status(201).json(cart);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.updateCartItem = async (req, res) => {
    try {
        const userId = req.user.id;
        const { product_id, quantity } = req.body;

        const cart = await Cart.findOne({ user_id: userId });

        if (!cart) {
            return res.status(404).json({ message: 'Cart not found' });
        }

        const itemIndex = cart.items.findIndex(item => item.product_id.toString() === product_id);

        if (itemIndex === -1) {
            return res.status(404).json({ message: 'Item not found in cart' });
        }

        cart.items[itemIndex].quantity = quantity;
        cart.total_amount = cart.items.reduce((total, item) => total + (item.quantity * item.price), 0);

        await cart.save();

        res.status(200).json(cart);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error', error: error.message });
    }
};

exports.removeItemFromCart = async (req, res) => {
  try {
    const userId = req.user.id;
    const { product_id } = req.params;

    const cart = await Cart.findOne({ user_id: userId });

    if (!cart) {
      return res.status(404).json({ message: 'Cart not found' });
    }

    cart.items = cart.items.filter(item => item.product_id.toString() !== product_id);
    cart.total_amount = cart.items.reduce((total, item) => total + (item.quantity * item.price), 0);

    await cart.save();

    res.status(200).json({ message: 'Item removed from cart', cart });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.clearCart = async (req, res) => {
  try {
    const userId = req.user.id;
    const cart = await Cart.findOne({ user_id: userId });

    if (!cart) {
      return res.status(404).json({ message: 'Cart not found' });
    }

    cart.items = [];
    cart.total_amount = 0;

    await cart.save();

    res.status(200).json({ message: 'Cart cleared', cart });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};