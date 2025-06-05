module.exports = {
    port: process.env.PORT || 5000,
    dbURI: process.env.MONGODB_URI || 'mongodb://localhost:27017/ecommerce',
    jwtSecret: process.env.JWT_SECRET || 'secret',
  };