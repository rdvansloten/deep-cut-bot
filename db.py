import mysql.connector

# Connect to the database
cnx = mysql.connector.connect(
  user=os.getenv('MYSQL_USER'), 
  password=os.getenv('MYSQL_PASSWORD'), 
  host='localhost', 
  database=os.getenv('MYSQL_DATABASE')
)

def init_table(table_name):
  cursor = cnx.cursor()

  check_table_query = f"SHOW TABLES LIKE '{table_name}'"
  cursor.execute(check_table_query)
  result = cursor.fetchone()

  if result:
      print(f"Table {table_name} exists.")
  else:
      print(f"Table {table_name} does not exist.")
      cursor.execute(f"CREATE TABLE {table_name} (channel_id INT, guild_id INT, channel_name VARCHAR(255), guild_name VARCHAR(255), active BOOLEAN, notes TEXT)")

  # Close the cursor and the connection
  cnx.commit()
  cursor.close()
  cnx.close()

def update_row(cursor, action, table_name, guild_id, channel_id, channel_name=None, guild_name=None, active=None, notes=None):
  check_table_query = f"SHOW TABLES LIKE '{table_name}'"
  cursor.execute(check_table_query)
  result = cursor.fetchone()

  if not result:
    logging.error(f"Table {table_name} does not exist.")
    return False

  if action == "create":
    cursor.execute(f"INSERT INTO {table_name} (guild_id, channel_id, channel_name, guild_name, active, notes) VALUES ({guild_id}, {channel_id}, '{channel_name}', '{guild_name}', {active}, '{notes}')")
    print(f"Row created in table {table_name}.")
    return True

  elif action == "edit":
    cursor.execute(f"UPDATE {table_name} SET channel_name='{channel_name}', guild_name='{guild_name}', active={active}, notes='{notes}' WHERE guild_id={guild_id} AND channel_id={channel_id}")
    logging.info(f"Row edited in table {table_name}.")
    return True

  elif action == "delete":
    cursor.execute(f"DELETE FROM {table_name} WHERE guild_id={guild_id} AND channel_id={channel_id}")
    logging.info(f"Row deleted from table {table_name}.")
    return True

  else:
    logging.warning(f"Invalid action: {action}")
    return False

def get_rows():
  cursor = cnx.cursor()


  return True
  cnx.commit()
  cursor.close()
  cnx.close()