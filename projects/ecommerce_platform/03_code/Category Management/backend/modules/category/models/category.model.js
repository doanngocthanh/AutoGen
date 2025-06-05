const { Sequelize, DataTypes } = require('sequelize');
const sequelize = require('../../../config/database');

const Category = sequelize.define('Category', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  description: {
    type: DataTypes.STRING,
  },
  image_url: {
    type: DataTypes.STRING,
  },
}, {
  tableName: 'Categories',
  timestamps: true,
});

module.exports = Category;