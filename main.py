import psycopg2


def create_db(conn):
    with conn.cursor() as c:

        c.execute('''CREATE TABLE IF NOT EXISTS clients
                     (id SERIAL PRIMARY KEY,
                      first_name TEXT,
                      last_name TEXT,
                      email TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS phones
                     (id SERIAL PRIMARY KEY,
                      client_id INTEGER,
                      phone_number TEXT,
                      FOREIGN KEY(client_id) REFERENCES clients(id))''')




def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as c:

        c.execute("INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id",
                  (first_name, last_name, email))

        client_id = c.fetchone()[0]

        if phones:
            for phone in phones:
                c.execute("INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)", (client_id, phone))


def add_phone(conn, client_id, phone):
    with conn.cursor() as c:

        c.execute("INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)", (client_id, phone))


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as c:

        if first_name:
            c.execute("UPDATE clients SET first_name=%s WHERE id=%s", (first_name, client_id))
        if last_name:
            c.execute("UPDATE clients SET last_name=%s WHERE id=%s", (last_name, client_id))
        if email:
            c.execute("UPDATE clients SET email=%s WHERE id=%s", (email, client_id))

        c.execute("DELETE FROM phones WHERE client_id=%s", (client_id,))

        if phones:
            for phone in phones:
                c.execute("INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)", (client_id, phone))


def delete_phone(conn, client_id, phone):
    with conn.cursor() as c:
        c.execute("""
                   DELETE FROM client_Phone
                   WHERE client_id=%s
                   RETURNING client_id
                   """, (client_id,))
        return c.fetchone()


def delete_client(conn, client_id):
    with conn.cursor() as c:
        delete_phone(conn, client_id)
        with conn.cursor() as cur:
            cur.execute("""
                    DELETE FROM client_info
                    WHERE client_id = %s
                    """, (client_id,))


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as c:

        query = "SELECT * FROM clients LEFT JOIN phones ON clients.id = phones.client_id WHERE "
        params = []

        if first_name:
            query += "first_name = %s OR "
            params.append(first_name)
        if last_name:
            query += "last_name = %s OR "
            params.append(last_name)
        if email:
            query += "email = %s OR "
            params.append(email)
        if phone:
            query += "phone_number = %s OR "
            params.append(phone)

        query = query[:-4]

        c.execute(query, params)
        rows = c.fetchall()

        return rows


if __name__ == '__main__':
    with psycopg2.connect(database = 'clients_db', user = 'postgres', password = 'g87f15cd9816w') as conn:
        print(add_client(conn, 'Vladimir', 'Milutin', 'milutin@gmail.com'))
        print(add_phone(conn, '1', '88005553535'))
        print(find_client(conn, 'Vladimir' ))

conn.close()