from kivy.uix.button import 
Button as KivyButton from 
kivy.uix.boxlayout import 
BoxLayout class Page(BoxLayout):
    def __init__(self): 
        super().__init__(orientation='vertical')
    def add(self, widget): 
        self.add_widget(widget)
class Button(KivyButton): def 
    __init__(self, text, action):
        super().__init__(text=text)
        self.bind(on_press=lambda x: action())
