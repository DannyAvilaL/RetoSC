'''

Programa que mostrará la interfaz gráfica donde el usuario podrá navegar por
las diferentes opciones disponibles.
Se podrá reproducir: audio, videos y mostrar música
Se tiene acceso a: clima, calendario
Se puede navegar por medio de un joystick y con botones

Autora: Nancy L. García Jiménez A01378043
Autora: Daniela Avila Luna      A01378664

'''
#para escuchar audio en raspberry
import os
os.environ['KIVY_AUDIO'] = 'sdl2'

#necesarias para las aplicaciones
import sys
import random as rd
from datetime import datetime
import calendar
import time
from plyer import filechooser

#del framework kivy (para agregar botones, cuadros de texto, pantallas, etc)
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen,  NoTransition, CardTransition
from kivy.uix.widget import Widget
from kivy_garden.mapview import MapView
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.event import EventDispatcher
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

#Importacion de clases
from weatherApp import weatherScreen
from videoMenu import homeVideoScreen, videoScreen
from searchpopupmenu import SearchPopupMenu
from homegpshelper import HomeGpsHelper
from musica import Reproductor

#agregar el archivo kv
Builder.load_file("interface.kv")

print(Window.size)

#administrador de "pantallas"
class RootWidget(ScreenManager):
    pass

class ImageButton(ButtonBehavior, Image):
    pass

class LabelButton(ButtonBehavior, Label):
    pass

class HomeMapView(MapView):
    pass

#clase de la pantalla del localizador
class gpsScreen(Screen):
    pass

class Status(BoxLayout,EventDispatcher):
    pass

#clase de la pantalla del calendario
class Calender(Screen):
    pass

#Clase que muestra la pantalla principal con botones (widgets), que direccionan a otras aplicaciones
class MainInterface(Screen):
    """Clase que se encargará de mostrar el menú principal con las
    aplicaciones disponibles.
    """

    horario = StringProperty()
    nombre = rd.choice(("DANNY", "NANCY"))
    horarios = {1: f"BUENOS DÍAS {nombre}", 2: f"BUENAS TARDES {nombre}", 3: f"BUENAS NOCHES {nombre}"}
    hora = int(datetime.now().strftime("%H"))
    print(hora)
    horario = str(hora)

    if(hora > 0 and hora < 12):
        mensaje = StringProperty(horarios[1])
    elif(hora >= 12 and hora < 18):
        mensaje = StringProperty(horarios[2])
    elif(hora >= 18):
        mensaje = StringProperty(horarios[3])

class MainApp(MDApp):

    video = StringProperty()
    volume = NumericProperty(1)
    search_menu = None
    current_lat = 19.4978
    current_lon = -99.1269
    time = StringProperty()

    def build(self):
        Window.clearcolor = (1,1,1,1) #color de fondo
        wm = RootWidget()
        wm.add_widget(MainInterface())
        wm.add_widget(weatherScreen())
        wm.add_widget(homeVideoScreen())
        wm.add_widget(videoScreen())
        wm.add_widget(Calender())
        wm.add_widget(Reproductor())
        wm.current = "menu"
        Clock.schedule_interval(self.update,1)
        return wm

    def choose_video(self):
        filechooser.open_file(on_selection=self.handle_selection)

    def change_screen(self,screenname):
        #screenmanager = self.root.ids['screenmanager']
        screenmanager = self.root
        screenmanager.current = screenname

    def handle_selection(self,selection):
        selection_list = selection
        self.video = selection_list[0]
        self.change_screen('video')

    def change_volume(self):
        slider = self.root.ids['video'].ids['volume_slider']
        print(slider.value)
        #slider.current =
        self.volume = slider.value

    def on_start(self, **kwargs):
        # Se inicializa el GPS
        HomeGpsHelper().run()
        # Instancia de SearchPopupMenu
        self.search_menu = SearchPopupMenu()

    def update(self,args):
        self.time = str(time.asctime())
        
#Clase necesaria en la aplicación calendario para desplegar el cuadro de texto de los recordatorios
class Reminder(BoxLayout):

    def __init__(self,**kwargs):
        super(Reminder,self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.add_widget(TextInput())
        self.b = BoxLayout(orientation = 'horizontal' , size_hint = (1,.15))
        self.add_widget(self.b)
        self.b.add_widget(Button(on_release = self.on_release,text = "OK!"))

    def on_release(self,event):
        print("OK clicked!")

#Clase necesaria en la aplicación calendario para desplegar los meses de manera vertical
class get_months(GridLayout):

    def __init__(self,c,**kwargs):
        super(get_months,self).__init__(**kwargs)
        self.cols = 7
        self.c  = calendar.monthcalendar(2021,6)
        for i in self.c:
            for j in i:
                if j == 0:
                    self.add_widget(Button(on_release = self.on_release,text = '{j}'.format(j='')))
                else:
                    self.add_widget(Button(on_release = self.on_release, text = '{j}'.format(j=j)))

    def on_release(self,args):
        background_color = .5,.6,.7,1
        
#Clase necesaria en la aplicación calendario para desplegar los botones con los numeros de las fechas
class Dates(GridLayout):

    now = datetime.now()
    def __init__(self,**kwargs):
        super(Dates,self).__init__(**kwargs)
        self.cols = 7
        self.c  = calendar.monthcalendar(2021,6)
        for i in self.c:
            for j in i:
                if j == 0:
                    self.add_widget(Button(on_release = self.on_release,text = '{j}'.format(j='')))
                else:
                    self.add_widget(Button(on_release = self.on_release, text = '{j}'.format(j=j)))

    def on_release(self,event):
        print("Fecha seleccionada :" + event.text)
        event.background_color = 1,0,0,1
        self.popup = Popup(title= "Establecer recordatorio :",
        content = Reminder(),
        size_hint=(None, None), size=(self.width*3/4, self.height))
        self.popup.open()

#Clase necesaria en la aplicación calendario para convertir el gridlayout en Boxlayout
class Months(BoxLayout):
    def __init__(self,**kwargs):
        super(Months,self).__init__(**kwargs)

#Clase que despliega un menu para que el usuario seleccione el año de la fecha que quiere conocer
class Select(BoxLayout):

    n = ListProperty()
    anio1_ = ObjectProperty(None)
    anio2 = ObjectProperty(None)
    str_ = ObjectProperty(None)
    btn = ObjectProperty(None)
    global count

    def __init__(self,**kwargs):
        super(Select,self).__init__(**kwargs)
        self.count = 0

    def get_years(self):
        if self.count == 0:
            for i in range(19,21):
                if i<10:
                    self.n.append('0'+str(i))
                else:
                    self.n.append(str(i))
        self.count = 1
        self.anio1_.values = self.n
        self.anio2.values = self.n

if __name__ == '__main__':
    MainApp().run()
