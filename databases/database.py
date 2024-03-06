from sqlite3 import connect
from dotenv import dotenv_values


if __name__ == '__main__':
    if not dotenv_values('../enviroment.env')['DATABASE_PATH']:
        with connect(f'{input("Insert database name (without extension):")}.db') as con:
            cur = con.cursor()
            cur.execute('''CREATE TABLE users (
        id       INTEGER PRIMARY KEY
                         NOT NULL,
        size     STRING  DEFAULT [1:1],
        gradient STRING  DEFAULT [ `.'_~:!/r?(l1Zё4h9W8$@],
        format   STRING  DEFAULT telegraph  
        );
        ''')
            con.commit()
        print('Please insert your database name in enviroment.env file')
    else:
        print("You already have a database")