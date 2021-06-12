from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.uix.image import Image
# Para el snackbar
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from kivy.metrics import dp

#obtener todos los datos del html
from bs4 import BeautifulSoup
import requests

#clase de la pantalla del clima
class weatherScreen(Screen):
    weather = StringProperty()
    location = StringProperty()
    time = StringProperty()
    humidity = StringProperty()
    description = StringProperty()
    
    #clase que consigue la información del clima con web scraping
    def search(self):
        try:
            city_name = self.ids.city_name.text
            country_name = self.ids.country_name.text
            print(city_name)
            url = f"https://www.timeanddate.com/weather/{country_name}/{city_name}"
            #response = requests.get("https://www.timeanddate.com/weather/mexico/mexico-city")
            response = requests.get(url)
            print(response.status_code)

            #creating a soup: obtener todo el texto html
            soup = BeautifulSoup(response.content,'html.parser')
            #print(soup.prettify())

            mainid = soup.find(id="qlook")
            mainclass = mainid.find(class_='h2')
            f = str(mainclass.get_text())
            celsius = str(f.split("°"))
            celsius = ((int(celsius[2]+celsius[3]))-32)*5/9
            infoclass = soup.find(class_="bk-focus__info")

            self.weather = str(round(celsius))+' °C'
            self.description = mainid.find('p').get_text()

            self.location = infoclass.find_all('tr')[0].get_text()[10:]
            self.time = infoclass.find_all('tr')[1].get_text()[14:]
            self.humidity = infoclass.find_all('tr')[5].get_text()[10:]
            
        except:
            pass

