# Kivy libraries
import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, NumericProperty, StringProperty

from kivy.factory import Factory
from kivy.animation import Animation
from kivy.core.window import Window

from kivy.storage.jsonstore import JsonStore


# Python libraries
import os
import random
import math



# Pantalla inicial. Es una RelativeLayout porque sobre ella voy a poner una BoxLayout con la pantalla de presentación y, sobre ésta, otra BoxLayout con el sorteo en sí.
class MainScreen(RelativeLayout):

    pantalla = ObjectProperty()
    alumnos = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.store = JsonStore(os.path.join(App.get_running_app().data_folder, 'data.json'))

        if self.store.exists('Alumnos'):
             self.alumnos = self.store.get('Alumnos')['n']


    def alumnos_text(self, widget, focus):
        if not focus:
            self.alumnos = int(widget.text) if not widget.text=='' else 0

            self.store = JsonStore(os.path.join(App.get_running_app().data_folder, 'data.json'))
            self.store.put('Alumnos', n=self.alumnos)


    def sortear(self):
        if not self.alumnos==0:
            self.sorteo_screen = Sorteo(self.alumnos, [0,Window.height])
        
            self.add_widget(self.sorteo_screen)

            anim = Animation(y=0, t='linear', duration=0.5)
            anim.start(self.sorteo_screen)
            anim.bind(on_complete=self.clean_open)

        else:
            Factory.ErrorPopup().open()

                            
    def clean_open(self,*args):
        self.remove_widget(self.pantalla)
        

    def close(self):
        self.add_widget(self.pantalla, index=1)
        
        anim = Animation(y=Window.height, t='linear', duration=0.5)
        anim.start(self.sorteo_screen)
        anim.bind(on_complete=self.clean_close)

        
    def clean_close(self,*args):
        self.remove_widget(self.sorteo_screen)

        
        
# Clase del Popup para resetear toda la data.       
class ResetPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

      
    def resetear(self):
        Store = JsonStore(os.path.join(App.get_running_app().data_folder, 'data.json'))

        keys = []
        
        for key in Store.keys():
            keys.append(key)

        for key in keys:
            if not key=='Alumnos':
                Store.delete(key)



# Clase que sortea. Tiene una BoxLayout con una Label que muestra el valor sorteado y dos botones para aceptarlo o rechazarlo, que además retornan a la pantalla de presentación.
class Sorteo(BoxLayout):
    
    N = NumericProperty()
    
    def __init__(self, alumnos, pos, **kwargs):
        super().__init__(**kwargs)

        self.x = pos[0]
        self.y = pos[1]

        self.store = JsonStore(os.path.join(App.get_running_app().data_folder, 'data.json'))
        self.alumnos = alumnos
        
        self.N, self.veces = self.quien(self.alumnos)


    def quien(self, Alumnos):
    
        choice = False

        while not choice:
            N = random.randint(1, Alumnos)

            if self.store.exists(str(N)):
                veces = self.store.get(str(N))['n']
            else:
                veces = 0

            r = random.random()

            if r < math.exp(-veces):
                choice = True
                return N, veces

            
    def aceptar(self):
        self.store.put(str(self.N), n=self.veces+1)

        
        
# Clase para poder usar halign y valign en el TextInput.
class AlignedTextInput(TextInput):

    halign = StringProperty('left')
    valign = StringProperty('top')

    def __init__(self, **kwargs):
        self.halign = kwargs.get("halign", "left")
        self.valign = kwargs.get("valign", "top")

        self.bind(on_text=self.on_text)

        super().__init__(**kwargs)
        
    def on_text(self, instance, value):
        self.redraw()
        
    def on_size(self, instance, value):
        self.redraw()

    def redraw(self):
        """ 
        Note: This methods depends on internal variables of its TextInput
        base class (_lines_rects and _refresh_text())
        """
        
        DEFAULT_PADDING = 6
        
        self._refresh_text(self.text)
        
        max_size = max(self._lines_rects, key=lambda r: r.size[0]).size
        num_lines = len(self._lines_rects)

        px = [DEFAULT_PADDING, DEFAULT_PADDING]
        py = [DEFAULT_PADDING, DEFAULT_PADDING]
        
        if self.halign == 'center':
            d = (self.width - max_size[0]) / 2.0 - DEFAULT_PADDING
            px = [d, d]
        elif self.halign == 'right':
            px[0] = self.width - max_size[0] - DEFAULT_PADDING
            
        if self.valign == 'middle':
            d = (self.height - max_size[1] * num_lines) / 2.0 - DEFAULT_PADDING
            py = [d, d]
        elif self.valign == 'bottom':
            py[0] = self.height - max_size[1] * num_lines - DEFAULT_PADDING

        self.padding_x = px
        self.padding_y = py



# App class. Se construye a partir de la clase MainScreen.
class RandomStudentApp(App):

    def build(self):
        self.title = 'Alumno Random'

        self.icon = 'icon.png'

        self.initialize_global_vars()
        
        return MainScreen()

    
    def initialize_global_vars(self):
        root_folder = self.user_data_dir

        self.data_folder = os.path.join(root_folder, 'data')

        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)



if __name__ == "__main__":
    RandomStudentApp().run()
