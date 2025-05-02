from .speakers import Mohan
from pathlib import Path
#from raj_mohan.speakers import Mohan

def main():

    Mohan().print_name()
    #with open("names.txt") as f:
    with (Path(__file__).parent / "names.txt").open() as f:
        print(f.read())

if __name__ == "__main__":
    main()