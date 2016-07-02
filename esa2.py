#!/usr/bin/python
# -*- coding: utf-8 -*-
# Q1 - A game
__author__ = "René Rose, info@rundwerk.de"
__version__ = "0.1.0"

'''
TODO
# AvatarGUI
# MapGUI

Allgemein

Offen Funktionalität
- Neuen Noise Name eingeben
- gewählten Noise löschen

'''
import gi, check, sqlite3, settings, json, dbconn, os, threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from random import randint

class Esa2(Gtk.Window):
    '''
    GUI
    '''
    def __init__(self):
        Gtk.Window.__init__(self, title="Esa 2 - Gtk/PyGObject", name="MyWindow")
        self.set_border_width(20)
        self.set_default_size( 400, 800 )
        self.menuGui()

    def menuGui(self):
        # Check installation
        #print( Gtk.get_major_version() )
        try:
            s = check.CheckUpSystem( )
            if s.checkUp( ) == True:
                self.DbConn = dbconn.DbConn( )
                self.box_outer = Gtk.Box( orientation=Gtk.Orientation.HORIZONTAL, spacing=6 )
                self.add( self.box_outer )
                self.listbox = Gtk.ListBox( )
                self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
                self.box_outer.pack_start(self.listbox, True, True, 0)
                row = Gtk.ListBoxRow( )
                hbox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10 )
                self.image = Gtk.Image( )
                self.image.set_from_file( "static/img/01logo.jpg" )
                hbox.pack_start( self.image, True, True, 0 )
                row.add( hbox )
                self.listbox.add( row )
                self.avatarGui( )
                print( "System checked successfully!" )

        except:
            print( "Some problems with the system configuration" )

    def avatarGui(self):
        '''implementation avatar gui'''
        self.box_outer.remove(self.listbox)
        self.listbox = Gtk.ListBox( )
        self.listbox.set_selection_mode( Gtk.SelectionMode.NONE )
        self.box_outer.pack_start( self.listbox, True, True, 0 )

        # start content
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)

        # Logo
        self.image = Gtk.Image( )
        self.image.set_from_file( "static/img/01logo.jpg")
        hbox.pack_start( self.image, True, True, 0 )

        # Chose avatar box
        label0 = Gtk.Label( "Avatar wählen", xalign=0 )
        hbox.pack_start( label0, True, True, 0 )
        name_combo= Gtk.ComboBoxText( )
        name_combo.set_entry_text_column( 0 )

        # get all avatars
        avatarsrows =  self.DbConn.crudR( " Select * from avatars" )
        for avatars in avatarsrows:
            name_combo.append_text( avatars[0] )
        hbox.pack_start( name_combo, False, False, 0 )

        # forward with avatar
        button = Gtk.Button.new_with_label("Weiter")
        button.connect("clicked", self.on_continue_one, name_combo)
        hbox.pack_start(button, True, True, 0)

        # delete avatar
        button = Gtk.Button.new_with_label("Löschen")
        button.connect("clicked", self.on_delete_avatar, name_combo)
        #button.set_sensitive( False )
        hbox.pack_start(button, True, True, 0)
        row.add( hbox )
        self.listbox.add(row)

        # Create new avatar box
        row = Gtk.ListBoxRow( )
        hbox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10 )
        label0 = Gtk.Label( "Neuen Avatar erstellen", xalign=0 )
        hbox.pack_start( label0, True, True, 0 )
        self.entry = Gtk.Entry( )
        self.entry.set_text( "" )
        hbox.pack_start( self.entry, True, True, 0 )
        button = Gtk.Button.new_with_label("Speichern")
        button.connect("clicked", self.on_save_new_avatar, name_combo)
        hbox.pack_start(button, True, True, 0)
        row.add( hbox )
        self.listbox.add(row)

        self.listbox.show_all( )

    def mapGui(self, name, start = False, chosenmap="fail"):
        '''implementation map gui'''
        # reload
        self.box_outer.remove(self.listbox)
        self.listbox = Gtk.ListBox( )
        self.listbox.set_selection_mode( Gtk.SelectionMode.NONE )
        self.box_outer.pack_start( self.listbox, True, True, 0 )

        # start content
        row = Gtk.ListBoxRow( )
        hbox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10 )

        # Logo
        self.image = Gtk.Image( )
        self.image.set_from_file( "static/img/01logo.jpg")
        hbox.pack_start( self.image, True, True, 0 )

        # show chosen avatar
        label0 = Gtk.Label( "Gewählter Avatar: " + name, xalign=0 )
        hbox.pack_start( label0, True, True, 0 )
        button = Gtk.Button.new_with_label( "Anderen Avatar wählen" )
        button.connect( "clicked", self.on_back_one)
        hbox.pack_start( button, True, True, 0 )
        row.add( hbox )
        self.listbox.add( row )

        # Chose map box
        row = Gtk.ListBoxRow( )
        hbox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10 )
        label0 = Gtk.Label( "Map wählen", xalign=0 )
        hbox.pack_start( label0, True, True, 0 )

        # get all maps
        map_store = Gtk.ListStore( int, str )
        maprows = self.DbConn.crudR( " Select * from maps WHERE name = '" + name + "'" )
        for map in maprows:
            map_store.append( [1, map[0]] )
        map_combo = Gtk.ComboBox.new_with_model_and_entry( map_store )
        map_combo.set_entry_text_column( 1 )
        hbox.pack_start( map_combo, False, False, 0 )

        # chose the map
        button = Gtk.Button.new_with_label( "Map Details anzeigen" )
        button.connect( "clicked", self.on_choosen_map, name, map_combo )
        hbox.pack_start( button, True, True, 0 )

        # delete chosen map
        button = Gtk.Button.new_with_label( "Map löschen" )
        button.connect( "clicked", self.on_delete_map, map_combo, name)
        hbox.pack_start( button, True, True, 0 )
        row.add( hbox )
        self.listbox.add( row )

        # create new map box
        row = Gtk.ListBoxRow( )
        hbox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10 )
        label0 = Gtk.Label( "Neue Map erstellen", xalign=0 )
        hbox.pack_start( label0, True, True, 0 )

        self.mapentry = Gtk.Entry( )
        self.mapentry.set_text( "" )
        hbox.pack_start( self.mapentry, True, True, 0 )

        # noise area
        label0 = Gtk.Label( "Noise wählen", xalign=0 )
        hbox.pack_start( label0, True, True, 0 )
        noise_store = Gtk.ListStore( int, str )
        noise_store.append( [1, "Neuen Noise erstellen und verwenden"] )

        # get all noises
        noiserows = self.DbConn.crudR( " Select * from noises WHERE name = '" + name + "'" )
        for noise in noiserows:
            noise_store.append( [1, noise[0]] )
        noise_combo = Gtk.ComboBox.new_with_model_and_entry( noise_store )
        noise_combo.set_entry_text_column( 1 )
        hbox.pack_start( noise_combo, False, False, 0 )

        button = Gtk.Button.new_with_label( "Neue Map speichern" )
        button.connect( "clicked", self.on_save_new_map, noise_combo, name )
        hbox.pack_start( button, True, True, 0 )

        row.add( hbox )
        self.listbox.add( row )

        # game data
        if start == True:
            row = Gtk.ListBoxRow( )
            hbox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10 )
            maprow = self.DbConn.crudR( " Select * from maps WHERE mapname = '" + chosenmap + "'" )
            label0 = Gtk.Label( "Avatar: {} ".format( maprow[0][1] ), xalign=0 )
            label1 = Gtk.Label( "Map: {} ".format( maprow[0][0] ), xalign=0 )
            label2 = Gtk.Label( "Noise: {} ".format( maprow[0][2] ), xalign=0 )
            hbox.pack_start( label0, True, True, 0 )
            hbox.pack_start( label1, True, True, 0 )
            hbox.pack_start( label2, True, True, 0 )

            # PLAY the map!!!
            button = Gtk.Button.new_with_label( "Diese Map spielen" )
            button.connect( "clicked", self.on_play_map, chosenmap, map_combo )
            hbox.pack_start( button, True, True, 0 )

            row.add( hbox )
            self.listbox.add( row )

        self.listbox.show_all( )

    ''''''''''''''''''''''''''''''''''''''''''
    ''' MAP FUNCTIONS                      '''
    ''''''''''''''''''''''''''''''''''''''''''

    def on_play_map(self, button, chosenmap, map_combo):
        ''' Start the game '''
        print("Here starts ESA 3")
            # call ESA 3
        thread = threading.Thread(target=os.system( '""C:/Python34/python.exe" "esa3.py" "' + chosenmap + '"' ))
        thread.start()

    def on_choosen_map(self, button, name, map_combo):
        ''' Show chosen map details '''
        tree_iter = map_combo.get_active_iter( )
        if tree_iter != None:
            model = map_combo.get_model( )
            row_id, map = model[tree_iter][:2]
            self.mapGui( name, start=True, chosenmap=map )

    def on_delete_map(self, button, map_combo, name):
        ''' Delete map from db '''
        tree_iter = map_combo.get_active_iter( )
        if tree_iter != None:
            model = map_combo.get_model( )
            row_id, map = model[tree_iter][:2]
            try:
                self.DbConn.crudD( "Delete from maps WHERE mapname = '" + map + "'" )
                self.mapGui( name )
            except:
                print( "Delete failed. Selected: ID=%d, name=%s" % (row_id, map) )

    def on_save_new_map(self, button, noise_combo, name):
        ''' Save the new map in db '''
        mapname = self.mapentry.get_text( )
        noise = ""

        tree_iter = noise_combo.get_active_iter( )
        if tree_iter != None:
            model = noise_combo.get_model( )
            row_id, noise = model[tree_iter][:2]

        if mapname == "":
            self.mapentry.set_text( "Bitte einen Map-Namen eingeben" )
        else:
            if noise == "":
                print ("Noise ist nicht gewählt")
            else:
                if noise == "Neuen Noise erstellen und verwenden":
                    print ("Neuer Noise wird erstellt")
                    noise = settings.firstNoise
                    noisename = "Noise " + mapname
                    noise = json.dumps( noise )
                    try:
                         self.DbConn.crudI( "Insert into noises VALUES ('" + noisename + "', '" + name + "', '" + noise + "')" )
                    except:
                        print( "Save new noise failed." )

                else:
                    # gewählten Noise aus db holen
                    print ("Noise aus db")
                    noiserow = self.DbConn.crudR( " Select * from noises WHERE name = '" + name + "'" )
                    noisename = noiserow[0][0]

                initMap = self.mapConverter( settings.firstNoise )
                initMapConv = json.dumps( initMap )
                try:
                    self.DbConn.crudI( "Insert into maps (mapname, name, noisename, map) VALUES ('" + mapname + "', '" + name + "', '" + noisename + "', '" + initMapConv + "')" )
                    self.mapGui( name )
                except:
                    print( "Save new map failed." )

    def on_back_one(self, button):
        self.avatarGui()

    def on_continue_one(self, button, name_combo):
        text = name_combo.get_active_text( )
        if text != None:
            self.mapGui(text)

    ''''''''''''''''''''''''''''''''''''''''''
    ''' AVATAR FUNCTIONS                   '''
    ''''''''''''''''''''''''''''''''''''''''''
    def on_delete_avatar(self, button, name_combo):
        ''' Delete the avatar from db '''
        name = name_combo.get_active_text( )
        if name != None:
            try:
                self.DbConn.crudD( "Delete from avatars WHERE name = '" + name + "'" )
                self.DbConn.crudD( "Delete from noises WHERE name = '" + name + "'" )
                self.DbConn.crudD( "Delete from maps WHERE name = '" + name + "'" )
                self.avatarGui()
            except:
                print( "Delete avatar failed.")

    def on_save_new_avatar(self, button, name_store):
        ''' Save the new avatar in db '''
        avatar = self.entry.get_text( )
        if avatar == "":
            self.entry.set_text( "Bitte einen Namen eingeben" )
        else:
            try:
                self.DbConn.crudI( "Insert into avatars VALUES ('" + avatar + "')" )
                name_store.append_text( avatar )
            except:
                print( "Save avatar failed." )

    def mapConverter(self, map):
        """ inDEV """
        '''
        Convert fields of the noise to an array
        structure of map array:
        absolute dummy map

        topology

        [fieldtype, walkable, editable, deadly, text]

        1 = water, 0, 0
        21 = earth, 1, 0
        61 = stona a, 0, 1
        62 = stone b, 0, 0
        127 = lava, 1, 0

        infrastructure

        128 = meadow
        161 = forest

        '''
        typeoffield = 0
        mapfield = []
        _a = []
        for list in map:
            _b = []
            for field in list:
                if field < 86:  # water
                    typeoffield = 1
                    mapfield = [typeoffield, 0, 0, 0,"Wasser"]
                elif field > 85 and field < 136:  # meadow
                    typeoffield = 128
                    fieldtext = "Wiese"
                    if field == 100:
                        typeoffield = 161  # Forest
                        fieldtext = "Wald"
                    mapfield = [typeoffield, 1, 1, 0,fieldtext]
                elif field > 135 and field < 141:  # lava
                    typeoffield = 127
                    mapfield = [typeoffield, 1, 0, 1, "Lava"]
                elif field > 140 and field < 161:  # stone A
                    typeoffield = 61
                    mapfield = [typeoffield, 0, 1, 0, "Kalkstein"]
                elif field > 160:  # stone B
                    typeoffield = 62
                    mapfield = [typeoffield, 0, 0, 0, "Granit"]

                _b.append( mapfield )

            _a.append( _b )

        _a = self.harmonizeForest(_a)
        return _a

    def harmonizeForest(self, map):
        """ inDEV """
        #print( randint( 0, 3 ) )
        _l = 0
        _forest = []

        for list in map:
            _f = 0
            for field in list:
                for value in field:
                    if value == 161:
                        #print ("to harmonize", _l, " - ", _f)
                        _forest.append((_l,_f))
                _f += 1
            _l += 1

        map = self._setNeighbours( map, _forest )
        return map

    def _setNeighbours(self, map, _forest):
        """ inDEV """
        try:
            for field in _forest:

                bottom = field[0]+1
                if bottom >= len(map):
                    bottom = len(map) - 1

                top = field[0]-1
                if top < 0:
                    top = 0;

                left = field[1]-1
                if left < 0:
                    left = 0
                right = field[1]+1
                if right >= len(map[0]):
                    right = len(map[0]) - 1

                vcenter = field[1]
                hcenter = field[0]
                #print(right, " - ", hcenter, " --- ", len(map[0]), " - ", len(map))

                if map[bottom][vcenter][0] != 1:
                    map[bottom][vcenter][0] = 161
                if map[top][vcenter][0] != 1:
                    map[top][vcenter][0] = 161
                if map[hcenter][left][0] != 1:
                    map[hcenter][left][0] = 161
                if map[hcenter][right][0] != 1:
                    map[hcenter][right][0] = 161

            #print (map)
            return map

        except:
            print ("Index error")




if __name__ == "__main__":
    win = Esa2( )
    win.connect( 'delete-event', Gtk.main_quit )
    # CSS
    screen = Gdk.Screen.get_default( )
    css_provider = Gtk.CssProvider( )
    css_provider.load_from_path( 'static/styles/styles.css' )
    priority = Gtk.STYLE_PROVIDER_PRIORITY_USER
    context = Gtk.StyleContext( )
    context.add_provider_for_screen( screen, css_provider, priority )

    win.show_all( )
    Gtk.main( )