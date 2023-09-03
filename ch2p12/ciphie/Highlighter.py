from ciphie import colors


class Highlighter:
    def __init__(self):
        self.highlight_map = {}

    def get(self, key):
        return self.highlight_map.get(key.upper(), None)


    def highlight(self, key, color):
        self.highlight_map[key.upper()] = color

    def unhighlight(self, key):
        self.highlight_map.pop(key.upper(), None)

    def __call__(self, key, char):
        key = key.upper()
        highlight_color = self.highlight_map.get(key)
        if highlight_color:
            return highlight_color + char + colors.ENDC
        else:
            return char