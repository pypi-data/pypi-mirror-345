"""Boilerplate magic to make the module executable."""

import sys

from lippu.cli import main

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
