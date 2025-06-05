const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'ecommerce',
  password: process.env.DB_PASSWORD || 'password',
  port: process.env.DB_PORT || 5432
});

class Payment {
  constructor(payment) {
    this.transactionId = payment.transactionId;
    this.paymentMethod = payment.paymentMethod;
    this.amount = payment.amount;
    this.status = payment.status;
    this.details = payment.details;
  }

  async save() {
    const query = {
      text: 'INSERT INTO Payments(transaction_id, payment_method, amount, status, details) VALUES($1, $2, $3, $4, $5)',
      values: [this.transactionId, this.paymentMethod, this.amount, this.status, JSON.stringify(this.details)]
    };

    try {
      await pool.query(query);
      console.log('Payment saved successfully');
    } catch (err) {
      console.error(err);
      throw err;
    }
  }
}

module.exports = Payment;
