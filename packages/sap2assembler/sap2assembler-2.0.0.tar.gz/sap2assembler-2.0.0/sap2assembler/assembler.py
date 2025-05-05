import os
import re

class assemblerError(Exception):
    pass

def insert(idx, string, char):
    return string[:idx] + char + string[idx:]

def normalize_spaces(string):
    # Replace multiple spaces with a single space
    return re.sub(r'\s+', ' ', string).strip()

def evaluate_expression(expression, variables, n_bytes, overflow):
    answer = round(eval(expression, variables))
    max_value = 2** ((n_bytes-1) * 8)
    if overflow and answer > max_value:
        answer = answer % max_value
    answer = hex(answer)[2:].zfill(2 if n_bytes == 2 else 4)
    return answer

class SAP2Assembler:
    def __init__(self):
        self.MnemonicToOpcode = {"add b": ["10000000", 1],
                                "add c": ["10000001", 1],
                                "adi": ["11000110", 2],
                                "ana b": ["10100000", 1],
                                "ana c": ["10100001", 1],
                                "ani": ["11100110", 2],
                                "call": ["11001101", 3],
                                "cmp b": ["10111000", 1],
                                "cmp c": ["10111001", 1],
                                "cpi": ["11111110", 2],
                                "dcr a": ["00111101", 1],
                                "dcr b": ["00000101", 1],
                                "dcr c": ["00001101", 1],
                                "hlt": ["01110110", 1],
                                "in": ["11011011", 2],
                                "inr a": ["00111100", 1],
                                "inr b": ["00000100", 1],
                                "inr c": ["00001100", 1],
                                "jmp": ["11000011", 3],
                                "jm": ["11111010", 3],
                                "jnz": ["11000010", 3],
                                "jz": ["11001010", 3],
                                "lda": ["00111010", 3],
                                "mov a, b": ["01111000", 1],
                                "mov a, c": ["01111001", 1],
                                "mov b, a": ["01000111", 1],
                                "mov b, c": ["01000001", 1],
                                "mov c, a": ["01001111", 1],
                                "mov c, b": ["01001000", 1],
                                "mvi a": ["00111110", 2],
                                "mvi b": ["00000110", 2],
                                "mvi c": ["00001110", 2],
                                "nop": ["00000000", 1],
                                "ora b": ["10110000", 1],
                                "ora c": ["10110001", 1],
                                "ori": ["11110110", 2],
                                "out": ["11010011", 2],
                                "ret": ["11001001", 1],
                                "sta": ["00110010", 3],
                                "sub b": ["10010000", 1],
                                "sub c": ["10010001", 1],
                                "sui": ["11010110", 2],
                                "xra b": ["10101000", 1],
                                "xra c": ["10101001", 1],
                                "xri": ["11101110", 2]}
        self.fileToAssemble = None
        self.fileToWrite = None
        self.address = "00"
        self.unformattedCodeToAssemble = ""
        self.codeToAssemble = ""
        self.labels = {}
        self.mnemonics_requiring_labels = ["call", "jmp", "jm", "jz", "jnz"]
        self.pseudo_instructions = [".org", ".word"]
        self.assemblyCodeLines = None
        self.mnemonics = [m.lower() for m in self.MnemonicToOpcode.keys()]
        self.assembledCode = [self.convertMnemonicToOpcode("nop") for i in range(65536)]
        self.variables = {}
        self.macros = {}

    def defineVariable(self, assignment):
        equals_index = assignment.find("==")
        expr = insert(equals_index, assignment, " ")
        equals_index = assignment.find("==")
        expr = insert(equals_index+3, expr, " ")
        expr = normalize_spaces(expr)

        expression = expr.split(" ")
        if len(expression) != 3:
            raise assemblerError(f"invalid variable assignment on line {self.find_line_index(assignment)}")

        if expression[2].startswith("$"):
            expression[2] = expression[2][1:]
        elif expression[2].startswith("#"):
            location = expression[2][1:]
            int_location = int(location, 2)
            hex_location = hex(int_location)[2:]
            expression[2] = hex_location

        variable_name = expression[0]
        variable_location = expression[2].zfill(4)
        variable_symbol = [variable_location, "00000000"]

        if len(variable_location) > 4:
            raise assemblerError(f"invalid variable assignment on line {self.find_line_index(assignment)}")
        self.variables[variable_name] = variable_symbol

        # print(f"assigned variable {variable_name} to location {variable_location}")

    def setVariable(self, variable_set_expression):
        equals_index = variable_set_expression.find("=")
        expr = insert(equals_index, variable_set_expression, " ")
        equals_index = variable_set_expression.find("=")
        expr = insert(equals_index + 2, expr, " ")
        expr = normalize_spaces(expr)
        variable_specs = expr.split(" ")

        if len(variable_specs) != 3:
            raise assemblerError(f"invalid variable assignment on line {self.find_line_index(variable_set_expression)}")

        if variable_specs[2].startswith("$"):
            value = variable_specs[2][1:]
            int_value = int(value, 16)
            bin_value = bin(int_value)[2:]
            variable_specs[2] = bin_value

        elif variable_specs[2].startswith("#"):
            value = variable_specs[2][1:]
            int_value = int(value, 2)
            bin_value = bin(int_value)[2:]
            variable_specs[2] = bin_value

        variable_name = variable_specs[0]
        variable_value = variable_specs[2].zfill(8)

        if len(variable_value) > 8:
            raise assemblerError(f"invalid variable assignment on line {self.find_line_index(variable_set_expression)}")

        self.variables[variable_name][1] = variable_value
        self.assembledCode[int(self.variables[variable_name][0], 16)] = variable_value

        # print(f"set variable {variable_name} to value {variable_value}")

    def handleVariable(self, expression):
        if "==" in expression:
            self.defineVariable(expression)
        elif "=" in expression:
            self.setVariable(expression)

    def addressCheck(self):
        if int(self.address, 16) > 65535:
            raise assemblerError(
                f"the SAP2 architecture only supports 16 bits of address (65536 addresses), which is exceeded by {int(self.address, 16) - 65535}")

    def printAssembledCode(self, row_width=16, hex_data=False, n_bytes=256):
        # Loop through the assembled code
        for idx, data in enumerate(self.assembledCode):
            if idx >= n_bytes:
                break  # Exit early if we reach the n_bytes limit

            # If hex_data is True, convert data to hexadecimal
            if hex_data:
                data = hex(int(data, 2))[2:].zfill(2)

            # Print the address at the start of the row
            if idx % row_width == 0:
                print(f"{hex(idx)[2:].zfill(4)}: {data}", end=" ")
            elif (idx % row_width) != (row_width - 1):  # Printing middle bytes
                print(f"{data} ", end="")
            else:  # End of the row
                print(f"{data}")

    def parseAscii(self, string):
        ascii_string = [ord(char) for char in string]
        bin_ascii_string = [bin(char)[2:].zfill(8) for char in ascii_string]
        return bin_ascii_string

    def identifyLabels(self):
        assemblyCode = ""
        assemblyCodeLines = []
        self.identifyVariables()
        self.parseMacros()
        self.address = "00"
        for line in self.assemblyCodeLines:
            # print(self.address)
            keyword_detected = False
            if ":" in line:
                # print("found label")
                label = line.split(":")[0]
                self.labels[label] = self.address
                keyword_detected = True
                continue
            for mnemonic in self.MnemonicToOpcode.keys():
                if line.startswith(mnemonic):
                    num_bytes = self.getNumBytesForMnemonic(mnemonic)
                    self.address = str(int(self.address, 16) + num_bytes)
                    assemblyCode += "\n" + line
                    assemblyCodeLines.append(line)
                    keyword_detected = True
                    break

            if "==" in line:
                pass

            if ".word" in line:
                self.address = str(int(self.address, 16) + 2)
                assemblyCode += "\n" + line
                assemblyCodeLines.append(line)
                keyword_detected = True

            if ".org" in line:
                origin = line[6:]
                operand_identifier = line[5]

                if operand_identifier == "$":
                    self.address = origin

                elif operand_identifier == "#":
                    int_origin = int(origin, 2)
                    hex_origin = hex(int_origin)[2:]
                    self.address = hex_origin

                assemblyCode += "\n" + line
                assemblyCodeLines.append(line)
                keyword_detected = True

            if line.startswith(".byte"):
                self.address = str(int(self.address, 16) + 1)
                assemblyCode += "\n" + line
                assemblyCodeLines.append(line)
                keyword_detected = True

            if line.startswith(".ascii"):
                string = line.split(" ")[1]
                ascii_string = self.parseAscii(string)
                self.address = str(int(self.address, 16) + len(ascii_string))
                assemblyCode += "\n" + line
                assemblyCodeLines.append(line)
                keyword_detected = True

            if ":" in line:
                # print("found label")
                label = line.split(":")[0]
                self.labels[label] = self.address
                keyword_detected = True

            if line.strip() != "" and keyword_detected == False:
                assemblyCode += "\n" + line
                assemblyCodeLines.append(line)

        self.address = "00"
        self.assemblyCodeLines = assemblyCodeLines
        self.codeToAssemble = assemblyCode

        # print(self.codeToAssemble)

    def convertMnemonicToOpcode(self, mnemonic):
        return self.MnemonicToOpcode[mnemonic][0]

    def getNumBytesForMnemonic(self, mnemonic):
        return self.MnemonicToOpcode[mnemonic][1]

    def areKeywordsInLine(self, line):
        for mnemonic in self.MnemonicToOpcode.keys():
            if mnemonic in line:
                return True

        if (".org" in line) or (".word" in line) or "=" in line or ".byte" in line or ".ascii" in line:
            return True

        return False

    def getCodeFromFile(self):
        with open(self.fileToAssemble, "r") as file:
            self.codeToAssemble = file.read()
            self.codeToAssemble = self.codeToAssemble.lower()
        self.assemblyCodeLines = self.codeToAssemble.split("\n")
        self.unformattedCodeToAssemble = self.codeToAssemble

    def incrementAddress(self):
        self.address = int(self.address, 16)
        self.address += 1
        self.address = hex(self.address)[2:].zfill(2)

    def find_line_index(self, lineToFind):
        # print(lineToFind)
        lines = self.unformattedCodeToAssemble.split("\n")
        for idx, line in enumerate(lines):
            if lineToFind == line.strip():
                return idx+1
        return False

    def parse_number(self, number, identifier):
        if identifier == "$":
            int_number = int(number, 16)

            if int_number < 256:
                return bin(int_number)[2:].zfill(8), "0" * 8
            first_byte = int_number & 0x00FF
            second_byte = int_number >> 8
            print(first_byte, second_byte)
            return bin(first_byte)[2:].zfill(8), bin(second_byte)[2:].zfill(8)

        elif identifier == "#":
            int_number = int(number, 2)
            if int_number < 256:
                return bin(int_number)[2:].zfill(8), "0" * 8
            first_byte = int_number & 0x00FF
            second_byte = int_number >> 8
            return bin(first_byte)[2:].zfill(8), bin(second_byte)[2:].zfill(8)
        else:
            raise assemblerError(f"Unknown operand identifier {identifier}")

    def formatAssemblyLines(self):
        lines = []
        for line in self.assemblyCodeLines:
            if line.strip() != "":
                if ";" in line:
                    comment_idx = line.find(";")
                    line = line[:comment_idx]
                    line = line.strip()
                lines.append(line.strip())
        self.assemblyCodeLines = lines

    def saveAssembledCode(self, filename, row_width=16, hex_data=False, n_bytes=256):
        with open(filename, 'w') as file:
            if hex_data:
                for idx, data in enumerate(self.assembledCode):
                    if idx < n_bytes:
                        data = hex(int(data, 2))[2:].zfill(2)
                        if idx % row_width == 0:
                            file.write(f"{hex(idx)[2:].zfill(4)}: {data} ")
                        elif (row_width - 1) > (idx % row_width) > 0:
                            file.write(f"{data} ")
                        elif (idx % row_width) == (row_width - 1):
                            file.write(f"{data}\n")
            else:
                for idx, data in enumerate(self.assembledCode):
                    if idx < n_bytes:
                        if idx % row_width == 0:
                            file.write(f"{hex(idx)[2:].zfill(4)}: {data} ")
                        elif (row_width - 1) > (idx % row_width) > 0:
                            file.write(f"{data} ")
                        elif (idx % row_width) == (row_width - 1):
                            file.write(f"{data}\n")

    def identifyVariables(self):
        for line in self.assemblyCodeLines:
            if "=" in line:
                self.handleVariable(line)

    def parseMacros(self):
        assemblyCodeLines = self.assemblyCodeLines
        self.assemblyCodeLines = []
        in_macro = False
        macro_name = ""
        for line_idx, line in enumerate(assemblyCodeLines):
            finished_macro = False
            if line.startswith(".macro") or in_macro:
                finished_macro = False
                if not in_macro:
                    macro_name = line.split(" ")[1]
                    macro_name = macro_name.strip()
                    self.macros[macro_name] = []
                if line != ".endmacro":
                    self.macros[macro_name].append(line)
                    in_macro = True

                else:
                    in_macro = False
                    finished_macro = True
            elif line != ".endmacro":
                self.assemblyCodeLines.append(line)
            if not finished_macro:
                continue
            elif line != ".endmacro":
                self.assemblyCodeLines.append(line)

            self.macros[macro_name] = self.macros[macro_name][1:]
        assemblyCodeLines = []

        num_iterations_to_skip = 0
        for line_idx, line in enumerate(self.assemblyCodeLines):
            if num_iterations_to_skip > 0:
                num_iterations_to_skip -= 1
                continue
            for macro in self.macros.keys():
                if line == macro:
                    macro_name = macro
                    break
            else:
                assemblyCodeLines.append(line)
                self.assemblyCodeLines = assemblyCodeLines
                continue

            assemblyCodeLines = assemblyCodeLines + self.macros[macro_name]

        self.assemblyCodeLines = assemblyCodeLines
        self.formatAssemblyLines()
        assemblyCode = "\n".join(self.assemblyCodeLines)
        self.codeToAssemble = assemblyCode
        self.assemblyCodeLines = assemblyCodeLines

    def assemble(self, fileToAssemble, fileToWrite="", row_width=16, hex_data=False, n_bytes=256, print_data=False, overflow=False):
        self.fileToAssemble = fileToAssemble
        self.fileToWrite = fileToWrite

        if not os.path.exists(fileToAssemble):
            raise assemblerError(f"File {fileToAssemble} not found")

        self.getCodeFromFile()
        self.formatAssemblyLines()
        self.identifyLabels()

        for line_idx, line in enumerate(self.assemblyCodeLines):
            if (".org" not in line) and (".word" not in line) and ("=" not in line) and (".ascii" not in line) and (".byte" not in line) and (":" not in line):
                # print(line)
                if not self.areKeywordsInLine(line):
                    raise assemblerError(f"Error in line {self.find_line_index(line)}, '{line}' doesn't contain a mnemonic or pseudo instruction")
                for mnemonic in self.MnemonicToOpcode.keys():
                    if line.startswith(mnemonic):
                        opcode = self.convertMnemonicToOpcode(mnemonic)
                        num_bytes = self.getNumBytesForMnemonic(mnemonic)
                        self.assembledCode[int(self.address, 16)] = opcode
                        if num_bytes == 1:
                            if line != mnemonic:
                                raise assemblerError(f"Error in line {self.find_line_index(line)}, '{line}' isn't a mnemonic")


                        if mnemonic not in self.mnemonics_requiring_labels:
                            if num_bytes > 1:
                                if "$" in line or "#" in line:
                                    number = line[len(mnemonic)+2:]
                                    operand_identifier = line[len(mnemonic)+1]
                                    first_byte, second_byte = self.parse_number(number, operand_identifier)
                                    if second_byte != "00000000" and num_bytes == 2:
                                        raise assemblerError(f"Error in line {self.find_line_index(line)}, invalid operand")
                                    self.incrementAddress()
                                    self.assembledCode[int(self.address, 16)] = first_byte
                                    if num_bytes == 3:
                                        self.incrementAddress()
                                        self.assembledCode[int(self.address, 16)] = second_byte
                                else:
                                    for label in self.labels:
                                        if label in line:
                                            break

                                    else:
                                        if ("+" not in line) and ("-" not in line) and ("/" not in line) and ("*" not in line):
                                            variable_name = line[len(mnemonic)+1:]
                                            if variable_name not in self.variables.keys():
                                                raise assemblerError(f"variable {variable_name} is not defined")

                                            variable_value = self.variables[variable_name][1]
                                            variable_location = self.variables[variable_name][0]

                                            self.incrementAddress()
                                            if num_bytes == 2:
                                                self.assembledCode[int(self.address, 16)] = variable_value
                                            else:
                                                first_byte, second_byte = self.parse_number(variable_location, "$")
                                                if second_byte != "00000000" and num_bytes == 2:
                                                    raise assemblerError(
                                                        f"Error in line {self.find_line_index(line)}, invalid operand")
                                                self.assembledCode[int(self.address, 16)] = first_byte
                                                self.incrementAddress()
                                                self.assembledCode[int(self.address, 16)] = second_byte

                                        else:
                                            variables_in_expression = {}
                                            expression = line[len(mnemonic)+1:]
                                            for variable in self.variables.keys():
                                                if variable in expression:
                                                    if num_bytes == 2:
                                                        variables_in_expression[variable] = int(self.variables[variable][1], 2)
                                                    elif num_bytes == 3:
                                                        variables_in_expression[variable] = int(self.variables[variable][0], 16)
                                            number = evaluate_expression(expression, variables_in_expression, n_bytes, overflow)
                                            first_byte, second_byte = self.parse_number(number, "$")
                                            if second_byte != "00000000" and num_bytes == 2 and not overflow:
                                                raise assemblerError(f"Error in line {self.find_line_index(line)}, operand value to large. to enable overflow, set the overflow variable")
                                            self.incrementAddress()
                                            if num_bytes == 2:
                                                self.assembledCode[int(self.address, 16)] = first_byte
                                            if num_bytes == 3:
                                                self.assembledCode[int(self.address, 16)] = first_byte
                                                self.incrementAddress()
                                                self.assembledCode[int(self.address, 16)] = second_byte

                        elif mnemonic in self.mnemonics_requiring_labels:
                            label = line[len(mnemonic)+1:]
                            # print(label)
                            if label not in self.labels.keys():
                                # print(self.codeToAssemble)
                                # print(line)
                                raise assemblerError(f"Error in line {self.find_line_index(line)}, label '{label}' doesn't exist")
                            label_address = self.labels[label]
                            # print(label_address)
                            first_byte, second_byte = self.parse_number(label_address, "$")
                            self.incrementAddress()
                            self.assembledCode[int(self.address, 16)] = first_byte
                            self.incrementAddress()
                            self.assembledCode[int(self.address, 16)] = second_byte

                        break
                self.incrementAddress()

            if ".word" in line:
                word = line[7:]
                operand_identifier = line[6]
                first_byte, second_byte = self.parse_number(word, operand_identifier)
                self.assembledCode[int(self.address, 16)] = first_byte
                self.incrementAddress()
                self.assembledCode[int(self.address, 16)] = second_byte

            if ".byte" in line:
                byte = line[7:]
                byte_identifier = line[6]
                first_byte, second_byte = self.parse_number(byte, byte_identifier)
                if second_byte != "00000000":
                    raise assemblerError(f"invalid byte {byte_identifier}{byte} in line {self.find_line_index(line)}")
                self.assembledCode[int(self.address, 16)] = first_byte

            if ".ascii" in line:
                text = line[7:]
                ascii_text = self.parseAscii(text)
                self.assembledCode[int(self.address, 16)] = ascii_text[0]
                for char in ascii_text[1:]:
                    self.incrementAddress()
                    self.assembledCode[int(self.address, 16)] = char

            if ".org" in line:
                origin = line[6:]
                operand_identifier = line[5]

                if operand_identifier == "$":
                    self.address = origin

                elif operand_identifier == "#":
                    int_origin = int(origin, 2)
                    hex_origin = hex(int_origin)[2:]
                    self.address = hex_origin

                else:
                    raise assemblerError(f"Unknown operand identifier {operand_identifier}")

            if ("=" in line) and ("==" not in line):
                self.handleVariable(line)

            self.addressCheck()

        if self.fileToWrite != "":
            self.saveAssembledCode(filename=self.fileToWrite, hex_data=hex_data, n_bytes=n_bytes, row_width=row_width)

        if print_data:
            self.printAssembledCode(row_width=row_width, hex_data=hex_data, n_bytes=n_bytes)
