from os import getenv

SECRET = getenv('USELESS_SECRET')

def main():
    print("hello world from pyflag")
    print("here is my secret from env var:", SECRET)


if __name__ == '__main__':
    main()
