from keyboard import mouse
from time import sleep
from random import randint
from humanfriendly import format_timespan


def main(interval=15, maxdev=5):
    s = 0
    while True:
        w = interval + randint(-maxdev, maxdev)
        s += w
        print(f"waiting {w}s. ({format_timespan(s)})")
        # NB: devrait supprimer la ligne courante!
        sleep(w)
        mouse.click()


if __name__ == "__main__":
    main()
