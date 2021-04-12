import sqlite3,time
def clear():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('DELETE FROM sessionadmin')
    cur.execute('DELETE FROM sessionuser')
    conn.commit()
while True:
    clear()
    print('Сессия очищена!')
    time.sleep(3600)
