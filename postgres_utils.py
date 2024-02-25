import psycopg2
from psycopg2 import sql

def connect(dbname, user, password, host):
    try:
        conn = psycopg2.connect(f"dbname={dbname} user={user} password={password} host={host}")
        return conn
    except psycopg2.Error as e:
        print("An error occurred while connecting to PostgreSQL", e)


def show_existing(conn):
    cur = conn.cursor()
    cur.execute(sql.SQL("SELECT datname FROM pg_database"))
    rows = cur.fetchall()

    for row in rows:
        print(f"Database name: {row[0]}")


def create_database(conn, dbname):
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()

    create_db_command = sql.SQL("CREATE DATABASE {};").format(sql.Identifier(dbname))

    cur.execute(create_db_command)

    cur.close()

def remove_database(conn, dbname):
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()

    # Prepare a string with the SQL command
    remove_db_command = sql.SQL("DROP DATABASE IF EXISTS {};").format(sql.Identifier(dbname))
    
    # Execute the SQL command
    cur.execute(remove_db_command)
    
    # Close the connection
    cur.close()


def create_table(conn, table_name, columns):
    cur = conn.cursor()

    columns_str_list = [f"{column} {data_type}" for column, data_type in columns.items()]
    columns_str = ", ".join(columns_str_list)

    create_table_command = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({});").format(
        sql.Identifier(table_name),
        sql.SQL(columns_str)
    )
    
    cur.execute(create_table_command)
    
    conn.commit()
    cur.close()


def remove_table(conn, table_name):
    cur = conn.cursor()

    remove_table_command = sql.SQL("DROP TABLE IF EXISTS {};").format(sql.Identifier(table_name))
    
    cur.execute(remove_table_command)
    
    conn.commit()
    cur.close()

# date, full_name, quote, document
def insert_document_data(conn, table_name, columns, data):
    cur = conn.cursor()
    
    # Prepare the SQL command and execute it for each row of data
    for row in data:
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({});").format(
            sql.Identifier(table_name),
            sql.SQL(columns_str),
            sql.SQL(placeholders)
        )
        cur.execute(query, tuple(row[column] for column in columns))
    
    # Commit the changes and close the connection
    conn.commit()
    cur.close()

# date, full_name, quote, document
def retrieve_data(conn, table_name, columns, data):
    # Create a new cursor object
    cur = conn.cursor()
    
    # Prepare a string with the SQL command
    columns_str = ', '.join(columns)
    select_command = sql.SQL("SELECT {} FROM {};").format(
        sql.SQL(columns_str),
        sql.Identifier(table_name)
    )
    
    # Execute the SQL command
    cur.execute(select_command)
    
    # Fetch all the rows
    rows = cur.fetchall()
    
    # Close the connection
    cur.close()
    conn.close()
    
    # Return the fetched rows
    return rows