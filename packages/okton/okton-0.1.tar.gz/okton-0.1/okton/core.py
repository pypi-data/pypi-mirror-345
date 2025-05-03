from kivy.app import App as KivyApp

class App:
    @staticmethod
    def run(root_widget):
        class MainApp(KivyApp):
            def build(self):
                return root_widget
        MainApp().run()
