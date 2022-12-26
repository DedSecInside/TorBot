#!/usr/bin/env python3
from torbot import main

if __name__ == '__main__':
    try:
        args = main.get_args()
        torbot = main.TorBot(args)
        torbot.perform_action()
    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
