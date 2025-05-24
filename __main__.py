import click
import win32gui
from strobe import OverlayWindow

# (hide_time, show_time)
levels = [
    (200, 400),
    (200, 300),
    (200, 200),
    (225, 175),
    (225, 150),
    (250, 125),
    (250, 100),
]
level_count = len(levels)


@click.command()
@click.option('--level', prompt=f'What level do you want to play on (1-{level_count})', type=int)
def startStrobe(level):
    if (level < 1 or level > level_count):
        raise f'Invalid level, please select a level between 1 and {level_count}'   

    hide_time, show_time = levels[level - 1]
    overlay = OverlayWindow(hide_time, show_time)
    try:
        overlay.run()
    except KeyboardInterrupt:
        overlay.running = False
        win32gui.DestroyWindow(overlay.hwnd)


if __name__ == "__main__":
    startStrobe()
