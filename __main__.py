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
@click.option('--verify', is_flag=True, default=True, prompt='⚠️ WARNING: This program flashes rapidly and may trigger seizures in individuals with photosensitive epilepsy.\nDo not use if you have a history of seizures or epilepsy.\nBy Pressing enter, you confirm that you have read the epilepsy warning and do not have a history of photosensitive epilepsy')
@click.option('--level', prompt=f'What level do you want to play on (1-{level_count})', type=int, default=1)
@click.option('--custom-timings', help="Custom timings (hide_time show_time)", nargs=2, is_flag=False, type=int)
def startStrobe(verify, level, custom_timings):
    if not verify:
        exit(1)

    if (level < 1 or level > level_count):
        raise f'Invalid level, please select a level between 1 and {level_count}'   

    hide_time, show_time = levels[level - 1] if custom_timings == None else custom_timings
    overlay = OverlayWindow(hide_time, show_time)
    try:
        overlay.run()
    except KeyboardInterrupt:
        overlay.running = False
        win32gui.DestroyWindow(overlay.hwnd)


if __name__ == "__main__":
    startStrobe()
