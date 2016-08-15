import sys

# parsed params
# sys.argv[0] contains the requested url
# http://stackoverflow.com/a/30664497

# Print the data you want to return
def main(arg):
    print("Hello World, arg: '" + arg + "'")

if __name__ == "__main__":
    main(sys.argv[1])