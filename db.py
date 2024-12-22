import psycopg2


@staticmethod
def connectPg(**kwargs):
    conn = psycopg2.connect(**kwargs, cursor_factory=psycopg2.extras.RealDictCursor)
    curs = conn.cursor()
    return conn, curs


@staticmethod
def disconnectPg(conn, curs):
    curs.close()
    conn.close()
