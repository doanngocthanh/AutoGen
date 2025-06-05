module.exports = {
  tmnCode: process.env.VNP_TMN_CODE || 'YOUR_VNPAY_TMN_CODE',
  secretKey: process.env.VNP_SECRET_KEY || 'YOUR_VNPAY_SECRET_KEY',
  returnUrl: process.env.VNP_RETURN_URL || 'http://localhost:3000/payment/vnpay_return',
  apiUrl: process.env.VNP_API_URL || 'http://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
  ipnUrl: process.env.VNP_IPN_URL || 'http://localhost:3000/payment/vnpay_ipn',
  version: '2.1.0',
  command: 'pay',
  currCode: 'VND',
  locale: 'vn'
};
