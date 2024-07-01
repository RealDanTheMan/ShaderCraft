from .appwindow import AppWindow

def Main() -> int:
    print('Starting Shadercraft')

    window = AppWindow()
    window.run()

    print('Exiting application')

    return 0