const Order = require('../models/order');
const OrderItem = require('../models/orderItem');

exports.getAllOrders = async (req, res) => {
  try {
    const orders = await Order.findAll();
    res.status(200).json(orders);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error fetching orders' });
  }
};

exports.getOrderById = async (req, res) => {
  const { id } = req.params;
  try {
    const order = await Order.findByPk(id, {
      include: [OrderItem],
    });
    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }
    res.status(200).json(order);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error fetching order' });
  }
};

exports.createOrder = async (req, res) => {
  try {
    const { user_id, order_date, total_amount, status, orderItems } = req.body;

    const order = await Order.create({
      user_id,
      order_date,
      total_amount,
      status,
    });

    if (orderItems && orderItems.length > 0) {
      await Promise.all(
        orderItems.map(async (item) => {
          await OrderItem.create({
            order_id: order.id,
            product_id: item.product_id,
            quantity: item.quantity,
            price: item.price,
          });
        })
      );
    }

    res.status(201).json(order);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error creating order' });
  }
};

exports.updateOrder = async (req, res) => {
  const { id } = req.params;
  try {
    const [updated] = await Order.update(req.body, {
      where: { id: id },
    });
    if (updated) {
      const updatedOrder = await Order.findByPk(id);
      return res.status(200).json(updatedOrder);
    }
    return res.status(404).json({ message: 'Order not found' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error updating order' });
  }
};

exports.deleteOrder = async (req, res) => {
  const { id } = req.params;
  try {
    const deleted = await Order.destroy({
      where: { id: id },
    });
    if (deleted) {
      return res.status(204).send();
    }
    return res.status(404).json({ message: 'Order not found' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error deleting order' });
  }
};