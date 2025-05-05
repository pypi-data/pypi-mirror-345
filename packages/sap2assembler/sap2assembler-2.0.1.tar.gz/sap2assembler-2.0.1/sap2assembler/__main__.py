import sys
from sap2assembler import SAP2Assembler


def main():
    fileToWrite = ""
    fileToAssemble = ""
    row_width = 16
    print_data = False
    hex_data = False
    n_bytes = 256
    overflow = False

    if len(sys.argv) < 2:
        return print("type 'sap2assembler -h' for help")
    args = sys.argv[1:]

    if "-h" in args:
        return print("""
            Usage:
                sap2assembler <input_file> [options]

            Options:
                -h            Show help
                -a <file>     Specify the input assembly file to assemble (required)
                -o <file>     Specify the output file to write machine code (optional)
                -rw <width>   Set the row width for output (default is 16)
                -b <bytes>    Set the number of bytes to write to the file or print (default is 256)
                -p            Print the assembled data to the console
                -hd           Output data in hex format (instead of binary)
                -fo           Force the result of an expression to overflow
                """)

    if len(args) == 2:
        fileToWrite = args[1]
        fileToAssemble = args[0]

    if "-a" in args:
        fileToAssemble = args[args.index("-a") + 1]

    if "-o" in args:
        fileToWrite = args[args.index("-o") + 1]

    if "-rw" in args:
        try:
            row_width = int(args[args.index("-rw") + 1])
        except Exception:
            return print("Please provide a valid row width (-rw)")

    if "-b" in args:
        try:
            n_bytes = int(args[args.index("-b") + 1])
        except Exception:
            return print("Please provide a valid number of bytes (-b)")

    if "-hd" in args:
        hex_data = True

    if "-p" in args:
        print_data = True

    if "-fo":
        overflow = True

    if "--version" in args:
        return print("2.0.1")

    assembler = SAP2Assembler()
    assembler.assemble(fileToAssemble=fileToAssemble, fileToWrite=fileToWrite, hex_data=hex_data, row_width=row_width, print_data=print_data, n_bytes=n_bytes, overflow=overflow)

    return None