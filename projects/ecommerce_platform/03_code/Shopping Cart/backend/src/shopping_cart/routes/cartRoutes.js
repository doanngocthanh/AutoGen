const express = require('express');
const router = express.Router();
const cartController = require('../controllers/cartController');
const { authenticateToken } = require('../../middleware/authMiddleware');

router.get('/', authenticateToken, cartController.getCart);
router.post('/items', authenticateToken, cartController.addItemToCart);
router.put('/items', authenticateToken, cartController.updateCartItem);
router.delete('/items/:product_id', authenticateToken, cartController.removeItemFromCart);
router.delete('/', authenticateToken, cartController.clearCart);

module.exports = router;