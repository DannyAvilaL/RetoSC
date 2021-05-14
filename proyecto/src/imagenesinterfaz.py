import  os
import sys
import random as rd
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import StringProperty

class ImagenesMenu(Screen):
    """Menú que se encargará de mostrar las imágenes que se encuentran en la
    Raspberry, ya sea en memoria SD o en USB"""

    curdir = StringProperty(os.path.dirname(os.getcwd()))