import sqlite3
import numpy as np
import pandas as pd

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

df = pd.read_csv('ramen-ratings.csv', dtype={'ID': np.int32, 'Country': str, 'Brand': str,
                 'Type': str, 'Package': str, 'Rating': np.float64}, na_values=['#VALUE!', ''])
df.dropna(how='any', inplace=True)

cur = connection.cursor()
for i, row in df.iterrows():
    print(str(i) + ' - ' + str(row['ID']) + '  ' + row['Country'] + '  ' + row['Brand'] +
          '  ' + row['Type'] + '  ' + row['Package'] + '  ' + str(row['Rating']))
    cur.execute("INSERT INTO reviews (ExID, Country, Brand, Type, Package, Rating) VALUES (?, ?, ?, ?, ?, ?)",
                (row['ID'], row['Country'], row['Brand'], row['Type'], row['Package'], row['Rating']))
connection.commit()
connection.close()
