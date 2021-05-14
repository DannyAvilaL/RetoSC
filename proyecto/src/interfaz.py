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
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

class MainInterface(Widget):
    """Clase que se encargará de mostrar el menú principal con las
    aplicaciones disponibles.
    """
    pass
        

class Interface(App):

    def build(self):
        Window.clearcolor = (1,1,1,1)
        return MainInterface()

if __name__ == '__main__':
    Interface().run()