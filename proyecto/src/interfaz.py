'''
Programa que mostrará la interfaz gráfica donde el usuario podrá navegar por
las diferentes opciones disponibles.
Se podrá reproducir: audio, videos y mostrar música
Se tiene acceso a: clima, calendario

Se puede navegar por medio de un joystick y con botones

Autora: Nancy L. García Jiménez A01378043
Autora: Daniela Avila Luna      A01378664
'''

import  os
import sys
import random as rd
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.lang import Builder

#Importacion de clases
from imagenesinterfaz import ImagenesMenu


kv = Builder.load_file("interface.kv")


class MainInterface(Screen):
    """Clase que se encargará de mostrar el menú principal con las
    aplicaciones disponibles.
    """
    nombre = rd.choice(("DANNY", "NANCY"))
    horarios = {1: f"BUENOS DÍAS {nombre}", 2: f"BUENAS TARDES {nombre}", 3: f"BUENAS NOCHES {nombre}"}
    hora = int(datetime.now().strftime("%H"))
    if(hora > 0 and hora < 12):
        mensaje = StringProperty(horarios[1])
    elif(hora >= 12 and hora < 18):
        mensaje = StringProperty(horarios[2])
    elif(hora >= 18):
        mensaje = StringProperty(horarios[3])


class WindowManager(ScreenManager):
    pass
    # sm = ScreenManager()
    # #for pantalla in range(5):
    # #    screen = Screen(name = f"pantalla {pantalla}")
    # #   sm.add_widget(screen)
    # sm.add_widget(MainInterface())
    # sm.add_widget(ImagenesMenu())
    # sm.current = "menu"

    # def on_touch_down(self, touch):
    #     return super().on_touch_down(touch)


class MainApp(App):

    def build(self):
        Window.clearcolor = (1,1,1,1) #color de fondo        
        return kv
        

if __name__ == '__main__':
    MainApp().run()
