def hhmmss(ms):
    # s = 1000
    # m = 60000
    # h = 360000
    # h, r = divmod(ms, 36000)
    # m, r = divmod(r, 60000)
    # s, _ = divmod(r, 1000)

    seconds = (ms / 1000) % 60
    minutes = (ms / 60000) % 60
    hours = (ms / 3600000) % 24

    return ("%d:%02d:%02d" % (hours,minutes,seconds)) if hours else ("%d:%02d" % (minutes,seconds))