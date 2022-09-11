from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class LibrarySystemUi(App):
    def build(self):
        self.window = GridLayout()
        self.title = 'Library System'
        self.icon = "logo.png"
        self.window.cols = 1
        self.window.size_hint = (0.5, 0.7)
        self.window.pos_hint = {"center_x":0.5, "center_y":0.5}
        

        #add widgets to window  
        self.window.add_widget(Image(source='logo_white.ico'))

        self.greeting = Label(
            text="Welcome To Library System.",
            font_size = 18,
            color="#f1f1f1"
            )
        self.window.add_widget(self.greeting)
        
        self.button = Button(
            text="ENTER LIBRARY",
            size_hint = (1, 0.5),
            bold = True,
            color = "#f1f1f1",
            background_color = "#ff1c1c",
            background_normal = ""
        )
        self.button.bind(on_press=self.callback)
        self.window.add_widget(self.button)

        return self.window

    def callback(self, instance):
        self.root_window.close()
        import os
        os.system("CLS")
        import LibrarySystemMain
        LibrarySystemMain.run()
    

if __name__ == "__main__":
    LibrarySystemUi().run()
