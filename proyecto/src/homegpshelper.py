from kivy.app import App
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock

class HomeGpsHelper():

    has_centered_map = False
    dialog = None
    def run(self):
        # Se hace una referencia a GpsBlinker, y después llama a la función blink()
        home_gps_blinker = App.get_running_app().root.ids.home_screen.ids.mapview.ids.blinker

        # Inicia el parpadeo de GpsBlinker
        home_gps_blinker.blink()

        # Le pide permiso al dispositivo
        if platform == 'android':
            from android.permissions import Permission, request_permissions
            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all permissions")
                    from plyer import gps
                    gps.configure(on_location=self.update_blinker_position, on_status=self.on_auth_status)
                    gps.start(minTime=1000, minDistance=1)
                else:
                    print("Did not get all permissions")

            request_permissions([Permission.ACCESS_COARSE_LOCATION,
                                 Permission.ACCESS_FINE_LOCATION], callback)

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

    def on_auth_status(self, general_status, status_message):
        if general_status == 'provider-enabled':
            pass
        else:
            print("Open gps access popup")
            try:
                self.open_gps_access_popup()
            except:
                print("error")
                pass

    def open_gps_access_popup(self):
        if not self.dialog:
            self.dialog = "STOP"
            Clock.schedule_once(self.run_dialog, 2)

    def run_dialog(self, *args):
        self.dialog = MDDialog(title="GPS Error", text="You need to enable GPS access for the app to function properly", size_hint=(0.5, 0.5))
        self.dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        self.dialog.open()
        self.dialog = None
