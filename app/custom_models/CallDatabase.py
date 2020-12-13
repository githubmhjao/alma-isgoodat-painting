import os
import psycopg2

def access_database():
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    return conn, cursor

def init_table():
    conn, cursor = access_database()
    postgres_table_query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"
    cursor.execute(postgres_table_query)
    table_records = cursor.fetchall()
    table_records = [i[0] for i in table_records]

    if 'user_dualtone_settings' not in table_records:
        create_table_query = """CREATE TABLE user_dualtone_settings (
            user_id VARCHAR ( 50 ) PRIMARY KEY,
            message_id VARCHAR ( 50 ) NOT NULL,
            original_grayscale VARCHAR ( 10 ) NOT NULL,
            adjusted_grayscale VARCHAR ( 10 ) NOT NULL,
            first_tone VARCHAR ( 50 ) NOT NULL,
            second_tone VARCHAR ( 50 ) NOT NULL
        );"""

        cursor.execute(create_table_query)
        conn.commit()

    return True

def init_record(user_id, message_id):
    conn, cursor = access_database()
    
    table_columns = '(user_id, message_id, original_grayscale, adjusted_grayscale, first_tone, second_tone)'
    postgres_insert_query = f"INSERT INTO user_dualtone_settings {table_columns} VALUES (%s,%s,%s,%s,%s,%s)"

    record = (user_id, message_id, '0', '150', '0:185:0', '0:0:185')

    cursor.execute(postgres_insert_query, record)
    conn.commit()

    cursor.close()
    conn.close()
    
    return record

def update_record(user_id, col, value):
    conn, cursor = access_database()
    
    postgres_update_query = f"UPDATE user_dualtone_settings SET {col} = %s WHERE user_id = %s"
    cursor.execute(postgres_update_query, (value, user_id))
    conn.commit()

    postgres_select_query = f"SELECT * FROM user_dualtone_settings WHERE user_id = '{user_id}';"
    
    cursor.execute(postgres_select_query)
    user_settings = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return user_settings

def check_record(user_id):
    conn, cursor = access_database()
    
    postgres_select_query = f"SELECT * FROM user_dualtone_settings WHERE user_id = '{user_id}';"
    
    cursor.execute(postgres_select_query)
    user_settings = cursor.fetchone()
    
    return user_settings
