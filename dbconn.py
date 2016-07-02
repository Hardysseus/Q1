#!/usr/bin/python
# -*- coding: utf-8 -*-
# Q1 - A game
__author__ = "René Rose, info@rundwerk.de"
__version__ = "0.1.0"

import sqlite3

class DbConn(object):
    """ Connector and crud method """
    def __init__(self):
        self.conSqlite3 = sqlite3.connect( "data\storage.db" )
        self.cursor = self.conSqlite3.cursor( )

    def crudI(self, crud=""):
        """ Insert operations """
        self.cursor.execute( crud )
        self.conSqlite3.commit( )

    def crudR(self, crud=""):
        """ Read operations """
        self.cursor.execute( crud )
        self.conSqlite3.commit( )
        rows = self.cursor.fetchall( )
        return rows

    def crudU(self):
        pass

    def crudD(self, crud=""):
        """ Delete operations """
        self.cursor.execute( crud )
        self.conSqlite3.commit( )
