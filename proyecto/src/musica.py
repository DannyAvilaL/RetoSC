'''
Programa que mostrará la interfaz gráfica de la aplicación de música donde el usuario podrá navegar por
las diferentes opciones disponibles.
Se podrá reproducir música, crear playlists, reproducir una sola canción o los playlist en loop
Muestra las canciones de la carpeta de música y al reproducirse el título, el tiempo y una imágen

Autora: Nancy L. García Jiménez A01378043
Autora: Daniela Avila Luna      A01378664

'''
import os
os.environ['KIVY_AUDIO'] = 'sdl2'
#os.environ["KIVY_AUDIO"] = "ffpyplayer" 
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.slider import  Slider
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock

from kivy.core.audio import SoundLoader
from kivy.uix.image import Image


import io
import re
from tinytag import TinyTag
from PIL import Image
from datetime import datetime, timedelta
from random import randint


import serial


COLOR = [19/255, 19/255, 117/255, 1] #[R, G, B, A]


class Cancion():

    
    def __init__(self, filename, dirCanciones):
        self.artist = "Desconocido"
        self.album = "Album desconocido"
        self.year = "2021" #'2013-09-13T07:00:00Z'
        self.dirCanciones = dirCanciones
        self.filename = self.dirCanciones + "/" + filename
        self.getData()

    def getData(self):
        tag = TinyTag.get(self.filename, image = True)
        self.artist = tag.artist
        self.album = tag.album
        self.duracion = tag.duration # d
        self.title = tag.title
        try:
            self.year = tag.year[:4:]
        except:
            self.year = " "
        self.artwork = tag.get_image() # tipo bytes


class Scroll(ScrollView):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.size = (Window.width, Window.height - 350)
        self.padding = 10
        self.do_scroll_x = False
        self.do_scroll_y = True


class GridCanciones(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.rows = 70
        self.size_hint_y = None


class BotonCancion(GridLayout):

    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.cols_minimum = {0: 600, 1: 20}
        self.size_hint_y = None
        self.index = index


class SongButton(Button):

    def __init__(self, indice, **kwargs):
        super().__init__(**kwargs)
        self.indice = indice


class AddSongButton(Button):

    def __init__(self, indice, **kwargs):
        super().__init__(**kwargs)
        self.text = '+'
        self.indice = indice


class Volumen(Slider):

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.min = 0
        self.max = 100
        self.value = 50
        self.orientation = 'vertical'
        self.step = 0.1
        self.value_track = True
        self.value_track_color = COLOR
        self.cursor_size = (10, 10)
        self.size_hint_y = 0.3
        self.size_hint_x = None
        self.pos = (30, 320)
        self.boder_vertical = [2, 0, 2, 0]


class TimeStamp(Slider):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.min = 0
        self.max = 300 # 5 min
        self.value = 0
        self.orientation = 'horizontal'
        self.step = 0.5
        self.value_track = True
        self.value_track_color = COLOR
        self.cursor_size = (15, 15)
        self.size_hint_y = None
        self.size_hint_x = 0.46
        self.pos = (340, 295)
        self.border_horizontal = [0, 2, 0, 2]


class TimeStampSTR(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "0:00"
        self.color = COLOR
        self.font_size = 10
        self.pos = (320, 341)


class Reproductor(Screen):

    #dirCanciones = "D:/danny/musica"
    dirCanciones = "/home/pi/Music"


    nombre = StringProperty(rebind = True)
    info = StringProperty(rebind = True)
    portada = StringProperty(rebind = True)
    duracion = NumericProperty(rebind = True)
    duracionStr = StringProperty(rebind = True)
    estado = StringProperty(rebind = True)
    hora = StringProperty(rebind = True)
    temperatura = StringProperty(rebind = True)

    tiempo = 0

    index = 0
    songPos = 0  
    objetosCanciones = []
    estadoLoop = "LOOP"
    estadoLoopStr = StringProperty(rebind = True)
    #gridCanciones = GridCanciones(spacing = 10) # GridLayout en ScrollView
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.canciones = []
        self.queue = []
        
        self.scrollview = Scroll()
        self.gridCanciones = GridCanciones(spacing = 10)
        self.gridCanciones.bind(minimum_height = self.gridCanciones.setter('height'))
        
        self.nombre = "Seleccione una canción"
        self.info = "No hay ninguna canción reproduciéndose"
        self.estado = "PLAY"
        self.estadoLoopStr = "LOOP QUEUE"
    
        self.duracionStr = "0:00"
        self.timestampSlider = TimeStamp()
        self.musicSlider()
        
    
        self.timestamp = TimeStampSTR()
        self.musicStr()

       
        self.volumeSlider = Volumen()
        self.add_widget(self.volumeSlider)
        self.volumeSlider.bind(value = self.ajustaVolumen)
        self.vol = 50
        self.obtenerCanciones()

        self.serial = serial.Serial('/dev/ttyACM0', 9600)
        self.serial.flush()

  
        Clock.schedule_interval(self.update_clock, 1)
        self.now = datetime.now()
        self.hora = self.now.strftime("%H:%M")
        self.temperatura = ""
        self.humedad = ""


    def update_clock(self, *args):
    
        self.now = self.now + timedelta(seconds = 1)
        self.hora = self.now.strftime("%H:%M")
        if self.serial.in_waiting > 0:
            linea = self.serial.readline().decode('utf-8').rstrip()
            print(linea)
            if linea == "Stop":
                self.stopSong()
            elif linea == "Play":
                self.playSong()
            elif linea == "next":
                self.nextSong()
            elif linea == "prev":
                self.prevSong()
            elif linea.endswith("%") == True:
                self.temperatura = linea
                self.sensTemp(self.temperatura)
            else:
                try:
                    self.vol = float(linea)
                    if self.estado == "STOP":
                        self.cancion.volume = self.vol
                except:
                    pass
    
    def sensTemp(self,temp_string):
        temp = re.findall(r'\d+', temp_string)
        res = list(map(int, temp))
        print(res)
        print("Sensor temperature read = ", res[0])
        if res[0] > 24:
            self.serial.write(b"turn_on\n")
        else:
            print("no hace tanto calor")
                
    def ajustaVolumen(self, instance, value):

        self.vol = float(value/100)
        if self.estado == "STOP":
            self.cancion.volume = self.vol
            self.timestampSlider.value = self.vol


    def musicSlider(self):

        self.add_widget(self.timestampSlider)
        self.timestampSlider.bind(value = self.on_value_change)


    def on_value_change(self, instance, value):
     
        if self.estado == "STOP":
            self.value = value
            value = f"{int(value//60)}:{int(value%60) if value%60 > 10 else str(0) + str(int(value%60))}"
            self.timestamp.text = f"{value}"
            self.cancion.seek(self.value)


    def musicStr(self):
     
        Clock.schedule_interval(self.updateTime, 1)
        self.add_widget(self.timestamp)


    def updateTime(self, *args):
     
        try:
            if self.estado == "STOP":
                if self.prettyDuracion(self.tiempo) == self.prettyDuracion(self.duracion-1):
                    self.repeat()
                self.timestampSlider.value = self.tiempo
                self.tiempo += 1
        except AttributeError:
            print("Canción no cargada")


    def obtenerCanciones(self):
  
        index = 0
        for root, dirs, files in os.walk(self.dirCanciones):
            for filename in files:
                if not(filename.endswith((".jpg", ".png", ".gif"))):
                    try:
                        cancion = Cancion(filename, self.dirCanciones)
                        print(type(cancion.filename))
                        self.objetosCanciones.append(cancion)
                        self.canciones.append(cancion.filename)
                        botonCancion = BotonCancion(index, size = (self.width, 50))
                        btnText = f"{cancion.title} - {cancion.artist} - {self.prettyDuracion(cancion.duracion)}" 
                        botonCancion.add_widget(SongButton(index, text = btnText), index)
                        botonCancion.add_widget(AddSongButton(index, text= '+'))          
                        self.gridCanciones.add_widget(botonCancion)
                        index += 1
                    except: pass
        print(len(self.canciones))
        self.scrollview.add_widget(self.gridCanciones)
        self.add_widget(self.scrollview)

    def prueba(self):
        print("cancion")

    def prettyDuracion(self, tiempo):
        return f"{int(tiempo//60)}:{int(tiempo%60) if tiempo%60 > 10 else str(0) + str(int(tiempo%60))}"


    def obtenerInfo(self):
        self.nombre = self.objetosCanciones[self.index % len(self.canciones)].title 
        autor = self.objetosCanciones[self.index % len(self.canciones)].artist
        if autor == None:
            autor = "Desconocido"
        album = self.objetosCanciones[self.index % len(self.canciones)].album
        if album == None:
            album = "Desconocido"
        self.duracion = self.objetosCanciones[self.index % len(self.canciones)].duracion
        year = self.objetosCanciones[self.index % len(self.canciones)].year
        portada = Image.open(io.BytesIO(self.objetosCanciones[self.index % len(self.canciones)].artwork))
        portada.save(f"portada{self.index}.png")
        duracion = self.objetosCanciones[self.index % len(self.canciones)].duracion
        self.duracionStr = self.prettyDuracion(duracion)
        self.timestampSlider.max = duracion #5 min
        return f"{autor} - {album} - {year}"


    def updateportada(self):
        self.portada = f"portada{self.index}.png"


    def statusSong(self): #KV
        if self.estado == "STOP":
            self.stopSong()
        else:
            self.playSong()


    def playSong(self):
        try:
            self.cancion = SoundLoader.load(self.canciones[self.index % len(self.canciones)])
            print(type(self.cancion))
            self.queue.append(self.cancion)
            self.info = self.obtenerInfo()
            if self.cancion:
                self.cancion.play()
                self.cancion.volume = self.vol
                self.cancion.seek(self.songPos)
                self.estado = "STOP"
            print(True)
            self.updateportada()
            
        except: pass
    

    def stopSong(self):
        try:
            self.songPos = self.tiempo
            self.cancion.stop()
        except:
            pass
        self.estado = "PLAY"
        print(False)

    def nextSong(self):
        try:
            self.tiempo = 0
            self.cancion.stop()
            nextS = self.queue.pop(0)
            self.cancion.unload()
            self.cancion = self.queue[0]
            self.queue.append(nextS)
        except:
            self.queue.append(SoundLoader.load(self.canciones[self.index % len(self.canciones)]))
        self.cancion = self.queue[0]
        self.index += 1
        print(self.index)
        print(self.canciones[self.index % len(self.canciones)])
        self.cancion = SoundLoader.load(self.canciones[self.index % len(self.canciones)])
        #self.nombre = self.objetosCanciones[self.index % len(self.canciones)].title
        self.info = self.obtenerInfo()
        self.cancion.play()
        self.updateportada()
        self.estado = "STOP"

    
    def prevSong(self):
        try:
            self.tiempo = 0
            self.cancion.stop()
            self.queue.pop(0)
            self.cancion.unload()
            self.cancion = self.queue[0]
        except:
            self.queue.append(SoundLoader.load(self.canciones[self.index % len(self.canciones)]))
        self.cancion = self.queue[0]
        self.index -= 1
        #print(self.index)
        #print(self.canciones[self.index % len(self.canciones)])
        self.cancion = SoundLoader.load(self.canciones[self.index % len(self.canciones)])
        #self.nombre = self.objetosCanciones[self.index % len(self.canciones)].title
        self.info = self.obtenerInfo()
        self.cancion.play()
        self.updateportada()
        self.estado = "STOP"


    def shuffle(self):
        try:
            self.cancion.stop()
            self.queue.pop(0)
            self.cancion.unload()
            self.queue = self.queue[0]
            self.tiempo = 0
        except:
            self.index = randint(0, len(self.canciones)-1)
            self.queue.append(SoundLoader.load(self.canciones[self.index % len(self.canciones)]))
        self.cancion = self.queue[0]
        self.index = randint(0, len(self.canciones)-1)
        self.cancion = SoundLoader.load(self.canciones[self.index % len(self.canciones)])
        self.info = self.obtenerInfo()
        self.cancion.play()
        self.updateportada()
        self.estado = "STOP"


    def repeat(self):
        """Funcion que debe de regresar si hay queue o no
        return rep?: no, cola, loop1
        """
        if self.cancion:
            self.cancion.stop()
            self.tiempo = 0
        if len(self.queue) > 0:
            self.nextSong()