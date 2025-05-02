from sys import argv, exit, stderr, stdout
from sqlcompose.core.app import app


if __name__ == "__main__":
    result, code = app(argv[1:])

    if code == 0:
        stdout.write(result)
    else:
        stderr.write(result)

    exit(code)
