const axios = require('axios');
const momoConfig = require('../config/momo.config');
const crypto = require('crypto');

exports.createPayment = async (paymentData) => {
  try {
    const orderId = paymentData.orderId;
    const amount = paymentData.amount;
    const orderInfo = paymentData.orderInfo || 'Payment for order';
    const returnUrl = momoConfig.returnUrl;
    const notifyUrl = momoConfig.notifyUrl;
    const partnerCode = momoConfig.partnerCode;
    const accessKey = momoConfig.accessKey;
    const secretKey = momoConfig.secretKey;
    const endpoint = momoConfig.endpoint;

    const requestId = orderId;
    const requestType = 'captureWallet';
    const extraData = paymentData.extraData || '';
n
    const rawSignature = `accessKey=${accessKey}&amount=${amount}&extraData=${extraData}&ipnUrl=${notifyUrl}&orderId=${orderId}&orderInfo=${orderInfo}&partnerCode=${partnerCode}&redirectUrl=${returnUrl}&requestId=${requestId}&requestType=${requestType}`;

    const signature = crypto.createHmac('sha256', secretKey)
      .update(rawSignature)
      .digest('hex');

    const requestBody = {
      partnerCode: partnerCode,
      accessKey: accessKey,
      requestId: requestId,
      amount: amount,
      orderId: orderId,
      orderInfo: orderInfo,
      redirectUrl: returnUrl,
      ipnUrl: notifyUrl,
      extraData: extraData,
      requestType: requestType,
      signature: signature
    };

    const response = await axios.post(endpoint, requestBody, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
