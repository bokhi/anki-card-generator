# -*- coding: utf-8 -*-
# Copyright: Martin Boissier
# License: GNU GPL, version 3 or later; http://www.gnu.org/licenses/gpl-3.0.txt

import os, sys
import sqlite3

database = '/media/READER/Sony_Reader/database/books.db'
file = 'list.txt'

def get_annotation(database, file)
    conn = sqlite3.connect(database)
    c = conn.cursor()

    f = open(file, 'w')

    for row in c.execute('SELECT * FROM annotation'):
        f.write(row[6] + '\n')

    c.close()

def delete_annotation(database)
    conn = sqlite3.connect(database)
    c = conn.cursor()
    
    c.execute('DELETE FROM annotation')

    conn.commit()

    c.close()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        get_annotation(database, str(sys.argv[1]))
    elif len(sys.argv) == 3:
        get_annotation(str(sys.argv[2]), str(sys.argv[1]))
    else:
        get_annotation()
