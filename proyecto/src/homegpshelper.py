from kivy.app import App
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock

#Clase que cambia la posición del led indicador y hace el llamado a mapview para la visualización del mapa
class HomeGpsHelper():

    has_centered_map = False
    dialog = None
    def run(self):
        # Se hace una referencia a GpsBlinker, y después llama a la función blink()
        home_gps_blinker = App.get_running_app().root.ids.home_screen.ids.mapview.ids.blinker

        # Inicia el parpadeo de GpsBlinker
        home_gps_blinker.blink()

    def update_blinker_position(self, *args, **kwargs):
        my_lat = kwargs['lat']
        my_lon = kwargs['lon']
        print("GPS POSITION", my_lat, my_lon)
        # Update GpsBlinker position
        home_gps_blinker = App.get_running_app().root.ids.home_screen.ids.mapview.ids.blinker
        home_gps_blinker.lat = my_lat
        home_gps_blinker.lon = my_lon

        # Fijar el gps al mapa
        if not self.has_centered_map:
            map2 = App.get_running_app().root.ids.home_screen.ids.mapview
            map2.center_on(my_lat, my_lon)
            self.has_centered_map = True

        App.get_running_app().current_lat = my_lat
        App.get_running_app().current_lon = my_lon
        
    def open_gps_access_popup(self):
        if not self.dialog:
            self.dialog = "STOP"
            Clock.schedule_once(self.run_dialog, 2)

    def run_dialog(self, *args):
        self.dialog = MDDialog(title="GPS Error", text="You need to enable GPS access for the app to function properly", size_hint=(0.5, 0.5))
        self.dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        self.dialog.open()
        self.dialog = None