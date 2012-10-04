# -*- coding: utf-8 -*-
# Copyright: Martin Boissier
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os, sys
import sqlite3

def get_annotations():
    conn = sqlite3.connect('/media/READER/Sony_Reader/database/books.db')
    c = conn.cursor()

    f = open('list.txt', 'w')

    for row in c.execute('SELECT * FROM annotation'):
    f.write(row[6] + '\n')


if __name__ == "__main__":
    get_annotations()
