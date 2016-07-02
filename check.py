#!/usr/bin/python
# -*- coding: utf-8 -*-
# Q1 - A game
__author__ = "René Rose, info@rundwerk.de"
__version__ = "0.1.0"

import sqlite3

class CheckUpSystem(object):
    """ Class for checkup the system """
    def __init__(self):
        print("Checkup start!")

    def checkUp(self):
        try:
            self.__setDb( config=True )
            return True
        except:
            return False

    def __setDb(self, config):
        try:
            con = sqlite3.connect( "data\storage.db" )
            cursor = con.cursor( )
            cursor.execute( "Create table if not exists avatars (name varchar(32) UNIQUE )" )
            cursor.execute( "Create table if not exists noises (noisename varchar(32) UNIQUE, name varchar(32), noise text)" )
            cursor.execute( "Create table if not exists maps (mapname varchar(32) UNIQUE, name varchar(32), noisename varchar(32), map text)" )
            con.commit( )
            if config == True:
                cursor.execute( "Insert into avatars VALUES ('Hinz')" )
                cursor.execute( "Insert into avatars VALUES ('Kunz')" )
                cursor.execute( "Insert into noises VALUES ('First Noise', 'Hinz', '')" )
                con.commit( )
            return True
        except:
            return False


