class Color:
    COLORS = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }

    @classmethod
    def colorize(cls, text, color):
        return f"{cls.COLORS[color]}{text}{cls.COLORS['reset']}"

def create_color_func(color):
    def func(text):
        return Color.colorize(text, color)
    return func

# Create color functions dynamically
for color in Color.COLORS:
    if color != 'reset':
        globals()[color] = create_color_func(color)