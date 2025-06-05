const express = require('express');
const paymentController = require('../controllers/payment.controller');

const router = express.Router();

router.post('/vnpay/create_payment', paymentController.createPaymentVNPay);
router.get('/vnpay_return', paymentController.vnpayReturn);
router.get('/vnpay_ipn', paymentController.vnpayIpn);

router.post('/momo/create_payment', paymentController.createPaymentMomo);
router.get('/momo_return', paymentController.momoReturn);
router.post('/momo_ipn', paymentController.momoIpn);

module.exports = router;
