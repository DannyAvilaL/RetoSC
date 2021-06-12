from kivymd.uix.dialog import MDInputDialog
from urllib import parse
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
import certifi
from kivy.clock import Clock
# Para el snackbar
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from kivy.metrics import dp
apikey_ = "2qLan9CBSfj1Nd9QT3qCCkrT02Lx5qqh3XyRGDwmOYE"

class SearchPopupMenu(MDInputDialog):

    title = 'Ingrese la dirección'
    text_button_ok = 'Search'

    def __init__(self):
        super().__init__()
        self.size_hint = [.9, .3]
        #callback está en la misma clase
        self.events_callback = self.callback

    def open(self):
        super().open()
        Clock.schedule_once(self.set_field_focus, 0.5)

    def callback(self, *args):
        address = self.text_field.text
        self.geocode_get_lat_lon(address)

    def geocode_get_lat_lon(self, address):
        api_key = apikey_
        address = parse.quote(address)
        url = "https://geocoder.ls.hereapi.com/6.2/geocode.json?searchtext=%s&apiKey=%s"%(address, api_key)
        UrlRequest(url, on_success=self.success, on_failure=self.failure, on_error=self.error, ca_file=certifi.where())
        #La librería certifi redirige a la certificación ssl

    def success(self, urlrequest, result):
        print("Success")
        print(result)
        try:
            latitude = result['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Latitude']
            longitude = result['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Longitude']
            print(latitude, longitude)
            app = App.get_running_app()
            mapview = app.root.ids.home_screen.ids.mapview
            mapview.center_on(latitude, longitude)
        except:
            pass


    def error(self, urlrequest, result):
        print("Error")
        print(result)

    def failure(self, urlrequest, result):
        print("Failure")
        print(result)
