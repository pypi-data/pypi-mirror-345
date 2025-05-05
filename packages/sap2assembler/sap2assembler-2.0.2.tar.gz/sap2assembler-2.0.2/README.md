# SAP2 assembler

A simple assembler for the SAP2 computer architecture

sap2assembler can be installed using pip

``` bash
pip install sap2ssembler
```

To use the package, you will need to have a file containing your assembly code

``` 
# test.sap2asm
mov a, b ; this will move this contents of the Accumulator into the B register
```

You can assemble the code using the ``SAP2Assembler`` class

``` python
from sap2assembler import SAP2Assembler # import the class

assembler = SAP2Assembler() # create the assembler object

assembler.assemble("test.sap2asm", print_data=True, n_bytes=8, row_width=4) # assemble and print the first 8 bytes in hex in 4 byte rows
```
```
0000: 78 00 00 00
0004: 00 00 00 00
```

By default, it will print the first 256 bytes in binary in 16 byte rows

If you want to save the machine code into a file, you will need to use the ```fileToWrite``` parameter

``` python
from sap2assembler import SAP2Assembler # import the class

assembler = SAP2Assembler() # create the assembler object

assembler.assemble("test.sap2asm", n_bytes=8, row_width=4, fileToWrite="output.txt") # save the assembled code into output.txt
```
output.txt
```
0000: 01111000 00000000 00000000 00000000
0004: 00000000 00000000 00000000 00000000
```

To use is as a CLI, you can use the ``sap2assembler`` command

```
sap2assembler
```

```
type 'sap2assembler -h' for help
```

To assemble a file, you need to use the ``-a`` flag

```
sap2assembler -a test.sap2asm -o output.txt -b 8 -rw 4 -hd -p
```
``-o`` will specify the output file
``-b`` is the number of bytes either to write into the file or print
``-rw`` is the row width
``-hd`` will output the data in hex
``-p`` will print the data

console
```
0000: 78 00 00 00
0004: 00 00 00 00
```
output.txt

```
0000: 78 00 00 00
0004: 00 00 00 00
```
