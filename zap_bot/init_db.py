def create_db(connection):
  sql = '''
    CREATE TABLE IF NOT EXISTS "messages"(
      "wa_id" TEXT,
      "role" TEXT,
      "content" TEXT,
      "tool_calls" TEXT,
      "tool_call_id" TEXT,
      "name" TEXT,
      "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS "products"(
      "id" INTEGER,
      "name" TEXT,
      "prices_per_unit" TEXT,
      "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY("id")
    );
    CREATE TABLE IF NOT EXISTS "orders"(
      "id" INTEGER,
      "customer_name" TEXT,
      "customer_phone" TEXT,
      "customer_address" TEXT,
      "customer_products" TEXT,
      "total_price" TEXT,
      "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY("id")
    );
    CREATE TABLE IF NOT EXISTS "users"(
      "name" TEXT UNIQUE,
      "password" TEXT,
      "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP
    );
  '''
  cursor = connection.cursor()
  cursor.executescript(sql)
  connection.commit()
  cursor.close()