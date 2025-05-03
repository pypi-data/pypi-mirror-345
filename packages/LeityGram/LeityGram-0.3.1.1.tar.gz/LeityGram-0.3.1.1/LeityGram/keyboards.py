class Button:
    def __init__(self, text: str):
        self.text = text

class Keyboard:
    def __init__(self, *buttons: Button, row_width: int = 3):
        self.buttons = buttons
        self.row_width = row_width

    def to_dict(self):
        keyboard = []
        row = []
        for i, button in enumerate(self.buttons, 1):
            row.append({'text': button.text})
            if i % self.row_width == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        return {'keyboard': keyboard}