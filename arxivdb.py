import os
import sys
import logging
import sqlite3

class ArxivDB:
    def __init__(self):
        project_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
        db_path = project_path + '/db/arxiv.db'
        if not os.path.exists(db_path):
            self.conn = sqlite3.connect(db_path, isolation_level=None)
            self.cursor = self.conn.cursor()
            self.create()
            logging.info('create database and arxiv table')
        else:
            self.conn = sqlite3.connect(db_path, isolation_level=None)
            self.cursor = self.conn.cursor()
        
    def create(self):
        self.cursor.execute('''
            CREATE TABLE ARXIV(
            ARXIV_LABEL    TEXT PRIMARY KEY  NOT NULL,
            AUTHOR_MON     TEXT              NOT NULL,
            ARXIV_LINK     TEXT              NOT NULL,
            TITLE          TEXT              NOT NULL,
            AUTHORS        TEXT              NOT NULL,
            ABSTRACT       TEXT              NOT NULL,
            SUBMITTED      TEXT              NOT NULL,
            COMMENTS       TEXT
            );
        ''')
    
    def insertPaper(self, p):
        try:
            self.cursor.execute('INSERT INTO ARXIV VALUES (?, ?, ?, ?, ?, ?, ?, ?)', p)
        except Exception as e:
            logging.info('insert paper error! paper is {}'.format(p))
    
    def selectByAuthorLable(self, arxiv_label):
        self.cursor.execute('SELECT * FROM ARXIV WHERE ARXIV_LABEL=(?)', arxiv_label)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()


