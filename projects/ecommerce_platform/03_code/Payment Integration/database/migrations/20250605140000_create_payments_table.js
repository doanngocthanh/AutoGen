exports.up = function(knex) {
  return knex.schema.createTable('Payments', (table) => {
    table.increments('id').primary();
    table.string('transaction_id').notNullable();
    table.string('payment_method').notNullable();
    table.decimal('amount').notNullable();
    table.string('status').notNullable();
    table.jsonb('details');
    table.timestamps(true, true);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('Payments');
};