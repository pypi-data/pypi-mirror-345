class Button:
    def __init__(self, text: str):
        self.text = text

class Keyboard:
    def __init__(self, *buttons: Button):
        self.buttons = buttons

    def to_dict(self):
        return {
            'keyboard': [[{'text': btn.text} for btn in self.buttons]],
            'resize_keyboard': True
        }