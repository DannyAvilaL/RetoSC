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
from tinytag import TinyTag
from PIL import Image
from datetime import datetime, timedelta
from random import randint
import serial


COLOR = [19/255, 19/255, 117/255, 1] #[R, G, B, A]

#Clase que guarda los atributos del archivo de audio.
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

# Clase que contiene un GridLayout con todas las canciones seleccionables
class Scroll(ScrollView):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.size = (Window.width, Window.height - 350)
        self.padding = 10
        self.do_scroll_x = False
        self.do_scroll_y = True

#Clase dentro de Scroll donde se guardarán los botones de las canciones
class GridCanciones(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.rows = 70
        self.size_hint_y = None

# Clase con 2 botones: cancion y añadir a la cola
class BotonCancion(GridLayout):

    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.cols_minimum = {0: 600, 1: 20}
        self.size_hint_y = None
        self.index = index

# Clase que hereda a Button para ser seleccionado y reproducir esa canción.
class SongButton(Button):

    def __init__(self, indice, **kwargs):
        super().__init__(**kwargs)
        self.indice = indice

# Clase que hereda a Button para agregar el índice que tenga en el queue
class AddSongButton(Button):

    def __init__(self, indice, **kwargs):
        super().__init__(**kwargs)
        self.text = '+'
        self.indice = indice

# Clase que manipula el volumen del audio por medio de un slider
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

#Clase que manipula la posición de la canción con un slider
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

# Clase que actualiza el tiempo actual de la canción
class TimeStampSTR(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "0:00"
        self.color = COLOR
        self.font_size = 10
        self.pos = (320, 341)

# Clase principal que manipula las canciones y demás objetos
class Reproductor(Screen):

    #dirCanciones = "D:/danny/musica" #windows
    dirCanciones = "/home/pi/Music" #raspberry


    # atributos que cambiarán con cada canción
    nombre = StringProperty(rebind = True)
    info = StringProperty(rebind = True)
    portada = StringProperty(rebind = True)
    duracion = NumericProperty(rebind = True)
    duracionStr = StringProperty(rebind = True)
    estado = StringProperty(rebind = True)
    hora = StringProperty(rebind = True)
    # variables que servirán para el control de reproducción
    index = 0
    songPos = 0  
    objetosCanciones = []
    estadoLoop = "LOOP" #No, Queue, Cancion
    estado = StringProperty(rebind = True)
    estadoLoopStr = StringProperty(rebind = True)
    #gridCanciones = GridCanciones(spacing = 10) # GridLayout en ScrollView
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.canciones = []
        self.queue = []
        self.index = 0
        # Código para el scrollview de las canciones
        self.scrollview = Scroll()
        self.gridCanciones = GridCanciones(spacing = 10)
        self.gridCanciones.bind(minimum_height=self.gridCanciones.setter('height'))
       
        self.nombre = "Seleccione una canción"
        self.info = "No hay ninguna canción reproduciéndose"
        self.estado = "PLAY"
        self.estadoLoopStr = "LOOP QUEUE"
        

        # Código para la barra del tiempo de reproducción
        self.duracionStr = "0:00"
        self.timestampSlider = TimeStamp()
        self.musicSlider()
        
        # Código para el str del tiempo actual de reproducción
        self.timestamp = TimeStampSTR()
        self.musicStr()

        # Código para el slider del volumen
        self.volumeSlider = Volumen()
        self.add_widget(self.volumeSlider)
        self.volumeSlider.bind(value = self.ajustaVolumen)
        self.vol = 50
        self.obtenerCanciones()

        # Reloj de sistema
        Clock.schedule_interval(self.update_clock, 1)
        self.now = datetime.now()
        self.hora = self.now.strftime("%H:%M")

        self.serial = serial.Serial('/dev/ttyACM1', 9600)
        self.serial.flush()

        Clock.schedule_interval(self.lecturaSerial, 0.5)
        self.temperatura = ""
        self.humedad = ""

    # Método que realiza la lectura serial con el arduino
    def lecturaSerial(self, *args):
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

    # Método que se actualiza cada segundo para el reloj integrado
    def update_clock(self, *args):
        self.now = self.now + timedelta(seconds = 1)
        self.hora = self.now.strftime("%H:%M")
        self.temperatura = ""
        self.humedad = ""


    # Método que actualiza el volumen de la canción de acuerdo con el
    # movimiento del slider
    def ajustaVolumen(self, instance, value):
        self.vol = float(value/100)
        if self.estado == "STOP":
            self.cancion.volume = self.vol
            self.timestampSlider.value = self.vol

    # Método que actualiza el slider de la canción
    def musicSlider(self):
        self.add_widget(self.timestampSlider)
        self.timestampSlider.bind(value = self.on_value_change)

    # Método que actualiza el texto del tiempo de la canción cuando se mueva el slider
    def on_value_change(self, instance, value):
        if self.estado == "STOP":
            self.value = value
            value = f"{int(value//60)}:{int(value%60) if value%60 > 10 else str(0) + str(int(value%60))}"
            self.timestamp.text = f"{value}"
            self.cancion.seek(self.value)

    # Método que actualiza el texto de la canción
    def musicStr(self):
        Clock.schedule_interval(self.updateTime, 1)
        self.add_widget(self.timestamp)

    # Método que compara detecta si la canción ya terminó para ver saber si debe
    # pasar a la siguiente o permanecer en loop
    def updateTime(self, *args):
        try:
            if self.estado == "STOP":
                if self.prettyDuracion(self.tiempo) == self.prettyDuracion(self.duracion-1):
                    self.repeat()
                self.timestampSlider.value = self.tiempo
                self.tiempo += 1
        except AttributeError:
            print("Canción no cargada")

    # Métdodo que se encarga de obtener todas las canciones disponibles
    # en el directorio que se especificó.
    def obtenerCanciones(self):
        index = 0
        for root, dirs, files in os.walk(self.dirCanciones):
            for filename in files:
                if not(filename.endswith((".jpg", ".png", ".gif"))):
                    cancion = Cancion(filename, self.dirCanciones)
                    self.objetosCanciones.append(cancion)
                    botonCancion = BotonCancion(index, size = (self.width, self.height))
                    btnText = f"{cancion.title} - {cancion.artist} - {self.prettyDuracion(cancion.duracion)}" 
                    sb = SongButton(index, text = btnText)
                    sb.bind(on_release = self.playSong)
                    botonCancion.add_widget(sb, index)
                    ads = AddSongButton(index, text= '+')
                    ads.bind(on_release = self.addSong)
                    botonCancion.add_widget(ads)          
                    self.gridCanciones.add_widget(botonCancion)
                    self.canciones.append(cancion.filename)
                    self.queue.append([cancion.filename, index])
                    index += 1
        self.scrollview.add_widget(self.gridCanciones)
        self.add_widget(self.scrollview)
        self.cancion = False

    # Método que obtiene un str del tiempo de las canciones
    def prettyDuracion(self, tiempo):
        return f"{int(tiempo//60)}:{int(tiempo%60) if tiempo%60 > 10 else str(0) + str(int(tiempo%60))}"

    # Método que actualiza en la pantalla la canción actual en reproducción
    def obtenerInfo(self, index):
        self.nombre = self.objetosCanciones[index].title 
        autor = self.objetosCanciones[index].artist
        if autor == None:
            autor = "Desconocido"
        album = self.objetosCanciones[index].album
        if album == None:
            album = "Desconocido"
        self.duracion = self.objetosCanciones[index].duracion
        year = self.objetosCanciones[index].year
        portada = Image.open(io.BytesIO(self.objetosCanciones[index].artwork))
        portada.save(f"portada{index}.png")
        duracion = self.objetosCanciones[index].duracion
        self.duracionStr = self.prettyDuracion(duracion)
        self.timestampSlider.max = duracion #5 min
        return f"{autor} - {album} - {year}"

    # Método que actualiza la portada de la canción en reproducción
    def updateportada(self, index):
        self.portada = f"portada{index}.png"

    # Método que agrega una canción a la cola de reproducción.
    def addSong(self, ctx):
        try:
            newSong = self.canciones[ctx.index]
            self.queue.insert(self.index+1, [newSong, ctx.index])
        except:
            print(f"No se pudo agregar la canción")

    # Método que indica si la cancion está en play o pausa
    def statusSong(self): #KV
        if self.estado == "STOP":
            self.stopSong()
            self.estado = "PLAY"
        else:
            self.playSong(self.index)
            self.estado = "STOP"

    # Método que reproduce la canción actual o nueva
    def playSong(self, ctx = 0, auto = 0):
        self.estado == "STOP"
        try:  # si viene del boton de la cancion
            if self.cancion:
                self.queue.insert(0, [self.canciones[ctx.index], ctx.index])
                self.cancion.stop()
                self.cancion.unload()
                # poner la canción en primera posición
                self.cancion = SoundLoader.load(self.queue[0][0])
            else:
                # poner la canción en primera posición
                self.queue.insert(0, [self.canciones[ctx.index], ctx.index])
                self.cancion = SoundLoader.load(self.queue[0][0])
            self.index = ctx.index
            #print(self.queue[self.index][0])
            self.songPos = 0
            self.updateportada(self.queue[0][1])
            self.info = self.obtenerInfo(self.queue[0][1])
            if self.cancion:
                self.cancion.play()
                self.cancion.volume = 0.2
            
        except:  # sin NO viene del boton de la cancion
            try:
                if self.cancion and auto == 0:
                    self.cancion.play()
                    self.cancion.seek(self.songPos)
                    self.cancion.volume = 0.2
                else:
                    try:
                        self.cancion.stop()
                        self.cancion.unload()
                    except: pass
                    print(self.queue[ctx % len(self.queue)][0])
                    self.cancion = SoundLoader.load(self.queue[ctx % len(self.queue)][0])
                    self.updateportada(self.queue[ctx % len(self.queue)][1])
                    self.info = self.obtenerInfo(self.queue[ctx % len(self.queue)][1])
                    self.cancion.play()
                    self.cancion.volume = 0.2
            except:
                pass
            self.index = ctx
    
    # Método que pausa la canción actual de reproducción
    def stopSong(self):
        try:
            self.songPos = self.cancion.get_pos()
            self.cancion.stop()
        except:
            pass
        self.estado = "PLAY"

    # Método que pasa a la siguiente canción.
    def nextSong(self):
        if self.estadoLoop == "LOOP CANCION":
            self.index -= 1
        self.index += 1
        self.songPos = 0
        self.playSong(self.index, 1)

    # Método que regresa a la canción previa en la cola
    def prevSong(self):
        if self.estadoLoop == "LOOP CANCION":
            self.index += 1
        self.index -= 1
        self.songPos = 0
        self.playSong(self.index, 1)

    # Método que selecciona una canción de forma aleatoria
    def shuffle(self):
        self.index = randint(0, len(self.canciones))
        self.playSong(self.index, 1)

    # Método que mantiene la canción actual o el loop de la cola
    def repeat(self):
        """Funcion que debe de regresar si hay queue o no
        return rep?: No, Queue, Cancion
        """
        if self.estadoLoop == "LOOP QUEUE":
            self.nextSong()
        elif self.estadoLoop == "LOOP CANCION":
            self.index -= 1
            self.nextSong()
    
    # Método que cambia el texto del botón de LOOP
    def repetir(self):
        if self.estadoLoop == "LOOP CANCION":
            print("Loop de la canción actual")
            self.estadoLoopStr = "LOOP QUEUE"
            self.estadoLoop = "LOOP QUEUE"
        elif self.estadoLoop == "LOOP QUEUE":
            print("La cola se repite")
            self.estadoLoopStr = "LOOP CANCION"
            self.estadoLoop = "LOOP CANCION"
