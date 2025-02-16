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
                sql = "CREATE TABLE tasks (id SERIAL PRIMARY KEY, description TEXT, responsible VARCHAR(50), cabinet VARCHAR(50), date DATE, comment TEXT, status BOOLEAN DEFAULT False, completed DATE, reminder BOOLEAN DEFAULT False, reminder_datetime DATETIME);"
                cur.execute(sql)
                conn.commit()
            conn.close()
        except Exception as error:
            pass

    def get_tasks(status, sort):
        conn = Database.connection()
        sql = f"SELECT id, description, responsible, cabinet, date, comment, status, completed, reminder, reminder_datetime FROM tasks WHERE status={status} ORDER BY {sort};"
        with conn.cursor() as cur:
            cur.execute(sql)
            res_list = cur.fetchall()
        conn.close()
        return res_list # список
    
    def set_task(data_list):
        conn = Database.connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tasks (description, responsible, cabinet, date, comment, reminder, reminder_datetime) VALUES (%s, %s, %s, %s, %s, %s, %s);", data_list)
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

    def update_task(data_list):
        conn = Database.connection()
        with conn.cursor() as cur:
            if data_list[7] == 'NULL':
                sql = f"""UPDATE tasks SET description='{data_list[1]}', responsible='{data_list[2]}', cabinet='{data_list[3]}', date='{data_list[4]}', comment='{data_list[5]}', reminder='{data_list[6]}', reminder_datetime={data_list[7]} WHERE id={data_list[0]};"""
            else:
                sql = f"""UPDATE tasks SET description='{data_list[1]}', responsible='{data_list[2]}', cabinet='{data_list[3]}', date='{data_list[4]}', comment='{data_list[5]}', reminder='{data_list[6]}', reminder_datetime='{data_list[7]}' WHERE id={data_list[0]};"""
            cur.execute(sql)
            conn.commit()  
        conn.close()