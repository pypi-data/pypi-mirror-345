#!/usr/bin/env python3

import os

from gibson.core.CommandRouter import CommandRouter
from gibson.core.Configuration import Configuration
from gibson.display.Header import Header


def main():
    if os.getenv("GIBSON_CLI_DEV"):
        print(f"{Header().render('dev mode')}\n")
    try:
        configuration = Configuration()
        CommandRouter(configuration).run()
    except KeyboardInterrupt:
        exit(1)


if __name__ == "__main__":
    main()
