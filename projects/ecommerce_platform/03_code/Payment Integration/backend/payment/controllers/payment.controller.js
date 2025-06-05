const vnpayService = require('../services/vnpay.service');
const momoService = require('../services/momo.service');
const Payment = require('../models/payment.model');

exports.createPaymentVNPay = async (req, res) => {
  try {
    const paymentData = req.body;
    const url = await vnpayService.createPaymentUrl(paymentData);
    res.json({ url });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Failed to create VNPay payment URL' });
  }
};

exports.vnpayReturn = async (req, res) => {
  try {
    const result = await vnpayService.vnpayReturn(req.query);
    // Save payment information to the database
    const newPayment = new Payment({
      transactionId: req.query.vnp_TransactionNo,
      paymentMethod: 'VNPay',
      amount: req.query.vnp_Amount / 100,
      status: result.success ? 'success' : 'failed',
      details: req.query
    });
    await newPayment.save();

    res.json(result);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'VNPay return processing failed' });
  }
};

exports.vnpayIpn = async (req, res) => {
  try {
    const result = await vnpayService.vnpayIpn(req.query);
    res.json(result);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'VNPay IPN processing failed' });
  }
};

exports.createPaymentMomo = async (req, res) => {
  try {
    const paymentData = req.body;
    const result = await momoService.createPayment(paymentData);
    res.json(result);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Failed to create Momo payment URL' });
  }
};

exports.momoReturn = async (req, res) => {
  try {
    // Handle Momo return
    res.json({ message: 'Momo return received', data: req.query });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Momo return processing failed' });
  }
};

exports.momoIpn = async (req, res) => {
  try {
    // Handle Momo IPN
    res.json({ message: 'Momo IPN received', data: req.body });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Momo IPN processing failed' });
  }
};
