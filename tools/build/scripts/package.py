import sys

def main():
    release = '--release' in sys.argv
    print('packaging', 'release' if release else 'debug')
    return 0

sys.exit(main())
