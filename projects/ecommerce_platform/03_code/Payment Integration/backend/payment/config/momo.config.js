module.exports = {
  partnerCode: process.env.MOMO_PARTNER_CODE || 'YOUR_MOMO_PARTNER_CODE',
  accessKey: process.env.MOMO_ACCESS_KEY || 'YOUR_MOMO_ACCESS_KEY',
  secretKey: process.env.MOMO_SECRET_KEY || 'YOUR_MOMO_SECRET_KEY',
  returnUrl: process.env.MOMO_RETURN_URL || 'http://localhost:3000/payment/momo_return',
  notifyUrl: process.env.MOMO_NOTIFY_URL || 'http://localhost:3000/payment/momo_ipn',
  endpoint: process.env.MOMO_ENDPOINT || 'https://test-payment.momo.vn/gw_payment/transactionProcessor'
};
