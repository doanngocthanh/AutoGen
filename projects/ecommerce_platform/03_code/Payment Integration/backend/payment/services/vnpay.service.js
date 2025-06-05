const querystring = require('qs');
const crypto = require('crypto');
const vnpayConfig = require('../config/vnpay.config');

exports.createPaymentUrl = async (paymentData) => {
  const createDate = new Date();
  const ipAddr = paymentData.ipAddr || '127.0.0.1';

  const tmnCode = vnpayConfig.tmnCode;
  const secretKey = vnpayConfig.secretKey;
  let vnpUrl = vnpayConfig.apiUrl;
  const returnUrl = vnpayConfig.returnUrl;

  const vnp_Params = {};
  vnp_Params['vnp_Version'] = vnpayConfig.version;
  vnp_Params['vnp_Command'] = vnpayConfig.command;
  vnp_Params['vnp_TmnCode'] = tmnCode;
  vnp_Params['vnp_Locale'] = vnpayConfig.locale;
  vnp_Params['vnp_CurrCode'] = vnpayConfig.currCode;
  vnp_Params['vnp_TxnRef'] = paymentData.orderId;
  vnp_Params['vnp_Amount'] = paymentData.amount * 100;
  vnp_Params['vnp_ReturnUrl'] = returnUrl;
  vnp_Params['vnp_IpAddr'] = ipAddr;
  vnp_Params['vnp_CreateDate'] = formatDate(createDate);
  vnp_Params['vnp_BankCode'] = paymentData.bankCode || '';
  vnp_Params['vnp_OrderInfo'] = paymentData.orderInfo || 'Payment for order';
  vnp_Params['vnp_TransactionType'] = '01'; // Adjust as needed

  const secureHash = generateVnpayHash(vnp_Params, secretKey);

  vnp_Params['vnp_SecureHash'] = secureHash;

  vnpUrl += '?' + querystring.stringify(vnp_Params, { encode: false });

  return vnpUrl;
};

exports.vnpayReturn = async (vnpayQuery) => {
  try {
    const secureHash = vnpayQuery['vnp_SecureHash'];
    delete vnpayQuery['vnp_SecureHash'];
    delete vnpayQuery['vnp_SecureHashType'];

    const secretKey = vnpayConfig.secretKey;

    const checkHash = generateVnpayHash(vnpayQuery, secretKey);

    if (secureHash === checkHash) {
      if (vnpayQuery['vnp_ResponseCode'] === '00') {
        return { success: true, message: 'Payment successful', data: vnpayQuery };
      } else {
        return { success: false, message: 'Payment failed', data: vnpayQuery };
      }
    } else {
      return { success: false, message: 'Invalid signature', data: vnpayQuery };
    }
  } catch (error) {
    console.error(error);
    return { success: false, message: 'Error processing VNPay return', error: error };
  }
};

exports.vnpayIpn = async (vnpayQuery) => {
  try {
    const secureHash = vnpayQuery['vnp_SecureHash'];
    delete vnpayQuery['vnp_SecureHash'];
    delete vnpayQuery['vnp_SecureHashType'];

    const secretKey = vnpayConfig.secretKey;

    const checkHash = generateVnpayHash(vnpayQuery, secretKey);

    if (secureHash === checkHash) {
      if (vnpayQuery['vnp_ResponseCode'] === '00') {
        // Update order status in database
        return { success: true, message: 'IPN: Payment successful', data: vnpayQuery };
      } else {
        return { success: false, message: 'IPN: Payment failed', data: vnpayQuery };
      }
    } else {
      return { success: false, message: 'IPN: Invalid signature', data: vnpayQuery };
    }
  } catch (error) {
    console.error(error);
    return { success: false, message: 'Error processing VNPay IPN', error: error };
  }
};

function generateVnpayHash(vnp_Params, secretKey) {
  const signData = querystring.stringify(vnp_Params, { encode: false });
  const hmac = crypto.createHmac('sha512', secretKey);
  const signed = hmac.update(new Buffer(signData, 'utf-8')).digest('hex');
  return signed;
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const minute = String(date.getMinutes()).padStart(2, '0');
  const second = String(date.getSeconds()).padStart(2, '0');
  return `${year}${month}${day}${hour}${minute}${second}`;
}
