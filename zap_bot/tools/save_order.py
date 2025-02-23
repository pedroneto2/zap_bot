from app import connection
import json

def save_order(customer_name, customer_phone, customer_address, customer_products, total_price):
  sql = "INSERT INTO orders(customer_name, customer_phone, customer_address, customer_products, total_price) VALUES (?, ?, ?, ?, ?)"

  cursor = connection.cursor()

  cursor.execute(sql, (customer_name, customer_phone, customer_address, json.dumps(customer_products), total_price))

  connection.commit()
  cursor.close()