from os import path
import psycopg2


class Database():
    def connection():
        return psycopg2.connect(dbname="helpdesk", user="postgres", password="postgres", host="127.0.0.1")

    def create_db():
        try:
            conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="127.0.0.1")
            conn.autocommit = True
            with conn.cursor() as cur:
                sql = "CREATE DATABASE helpdesk;"
                cur.execute(sql)
            conn.close()
        except Exception as error:
            pass
        try:
            conn = Database.connection()
            with conn.cursor() as cur:
                sql = "CREATE TABLE tasks (id SERIAL PRIMARY KEY, description TEXT, responsible VARCHAR(50), cabinet VARCHAR(50), date DATE, comment TEXT, status BOOLEAN DEFAULT False, completed DATE);"
                cur.execute(sql)
                conn.commit()
            conn.close()
        except Exception as error:
            pass

    def get_tasks(status):
        conn = Database.connection()
        sql = f"SELECT id, description, responsible, cabinet, date, comment, status, completed FROM tasks WHERE status={status} ORDER BY id;"
        with conn.cursor() as cur:
            cur.execute(sql)
            res_list = cur.fetchall()
        conn.close()
        return res_list # список
    
    def set_task(data_list):
        conn = Database.connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tasks (description, responsible, cabinet, date, comment) VALUES (%s, %s, %s, %s, %s);", data_list)
            conn.commit()  
        conn.close() 

    def delete_task(id):
        conn = Database.connection()
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM tasks WHERE id={id};")
            conn.commit()  
        conn.close()
    
    def set_status_ready(id):
        conn = Database.connection()
        with conn.cursor() as cur:
            cur.execute(f"UPDATE tasks SET status=True, completed=NOW() WHERE id={id};")
            conn.commit()  
        conn.close()