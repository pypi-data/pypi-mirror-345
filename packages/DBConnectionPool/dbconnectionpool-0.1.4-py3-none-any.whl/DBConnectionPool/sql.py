from .database import ConnectionPool
import argparse
import pymysql


def runsql(conn: ConnectionPool):
    sql = None
    while not sql == 'exit':
        if sql:
            if 'select'in sql:
                with conn.select(sql) as r:
                    head = ''
                    for i in range(len(r.sqlres[0].keys())):
                        column = list(r.sqlres[0].keys())[i]
                        head += column + ' | ' if not i == len(r.sqlres[0].keys()) - 1 else ''
                        print(column, end=' | ' if not i == len(r.sqlres[0].keys()) - 1 else '')
                    print()
                    for char in range(len(head) + 5):
                        print('-', end='')
                    print()
                    for row in r.sqlres:
                        for i in range(len(row.keys())):
                            column = list(row.keys())[i]
                            print(row[column], end=' | ' if not i == len(row.keys()) - 1 else '')
                        print()
            else:
                r = conn.runsql(sql)
                print(f'Rowcount: {r}')
        sql = input('>>>')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('password', help="The password for the mysql server.")
    parser.add_argument('-i', '--host', default='localhost', type=str, help="The host (ip) of the mysql server.")
    parser.add_argument('-p', '--port', default='3306', type=int, help="The port of the mysql server.")
    parser.add_argument('-u', '--user', default='root', type=str, help="The user for the mysql server.")
    parser.add_argument('-d', '--database', default=None, help="The databse to connect to.")
    args = parser.parse_args()
    host = args.host
    port = args.port
    user = args.user
    password = args.password
    db = args.database
    try:
        connection = ConnectionPool(password, user, host, port, db)
        print('Connection successful!')
        runsql(connection)
    except pymysql.err.OperationalError:
        print('Server not found!')
