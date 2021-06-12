from kivy_garden.mapview import MapMarker
from kivy.animation import Animation

#Clase que hace la animación del indicador led de la posición seleccionada por el usuario
class GpsBlinker(MapMarker):

    def blink(self):
        # función Animation que cambia el tamaño del blink y la opacity
        anim = Animation(outer_opacity=0, blink_size=50)

        # Cuando se completa la animación, se resetea y repite
        anim.bind(on_complete = self.reset)
        anim.start(self)

    def reset(self, *args):
        self.outer_opacity = 1
        self.blink_size = self.default_blink_size
        self.blink()
