import psycopg2
from psycopg2 import sql
import pandas as pd

def connect(dbname, user, password, host):
    try:
        conn = psycopg2.connect(f"dbname={dbname} user={user} password={password} host={host}")
        return conn
    except psycopg2.Error as e:
        print("An error occurred while connecting to PostgreSQL", e)


def get_existing(conn):
    cur = conn.cursor()
    cur.execute(sql.SQL("SELECT datname FROM pg_database"))
    rows = cur.fetchall()

    # for row in rows:
    #     print(f"Database name: {row[0]}")

    return rows


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

def get_all_tables(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    return [table[0] for table in tables]


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
def insert_document_data(conn, table_name, columns, data_df):
    cur = conn.cursor()
    
    # Prepare the SQL command and execute it for each row of data
    for index, row in data_df.iterrows():
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

def head_postgresql(conn, table_name, n):
    query = "SELECT * FROM {} LIMIT {}".format(table_name, n)
    df = pd.read_sql_query(query, conn)
    return df

def filter_by_name(conn, table_name, name):
    # Create a new cursor object
    cur = conn.cursor()
    
    # Prepare a string with the SQL command
    select_command = sql.SQL("SELECT * FROM {} WHERE name = %s;").format(
        sql.Identifier(table_name)
    )
    
    # Execute the SQL command
    cur.execute(select_command, (name,))

    primary_keys = []
    for row in cur.fetchall():
        primary_keys.append(row[-1])
    
    # Close the connection
    cur.close()
    
    # Return the fetched rows
    return primary_keys