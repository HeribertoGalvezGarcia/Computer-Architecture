"""CPU functionality."""

import sys
from typing import List, Tuple, Union

instructions = {
    0b10000010: (2, lambda cpu, reg1, reg2: cpu.reg.__setitem__(reg1, reg2)),  # LDI
    0b00000001: (0, lambda cpu: sys.exit()),  # HLT
    0b01000111: (1, lambda cpu, reg1: print(cpu.reg[reg1])),  # PRN
    0b10100000: (2, lambda cpu, reg1, reg2: cpu.alu('ADD', reg1, reg2)),  # ADD
    0b10100010: (2, lambda cpu, reg1, reg2: cpu.alu('MLT', reg1, reg2)),  # MLT
    0b01000101: (1, lambda cpu, reg1: cpu.push_stack(cpu.reg[reg1])),  # PUSH
    0b01000110: (1, lambda cpu, reg1: cpu.reg.__setitem__(reg1, cpu.pop_stack())),  # POP
    0b01010000: (1, lambda cpu, reg1: (cpu.push_stack(cpu.pc), setattr(cpu, 'pc', cpu.reg[reg1]))),  # CALL
    0b00010001: (0, lambda cpu: setattr(cpu, 'pc', cpu.pop_stack())),  # RET
}


class CPU:
    """Main CPU class."""

    pc: int
    ram: List[int]
    reg: List[int]

    def __init__(self) -> None:
        """Construct a new CPU."""

        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 7 + [0x74]

    def ram_read(self, address: int) -> int:
        return self.ram[address]

    def ram_write(self, address: int, value: int) -> None:
        self.ram[address] = value

    def push_stack(self, value: int) -> None:
        self.reg[-1] -= 1
        self.ram[self.reg[-1]] = value

    def pop_stack(self) -> int:
        value = self.ram[self.reg[-1]]
        self.reg[-1] += 1
        return value

    def load(self, file_name: str) -> None:
        """Load a program into memory."""

        address = 0

        program = []

        with open(file_name) as f:
            lines = f.readlines()

        for line in lines:
            instruction, _, _ = line.strip('\n').partition('#')
            if not instruction:
                continue

            program.append(int(instruction, 2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op: str, reg_a: int, reg_b: int) -> None:
        """ALU operations."""

        if op == 'ADD':
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MLT":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception('Unsupported ALU operation')

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def increment_pc(self) -> int:
        value = self.pc
        self.pc += 1
        return value

    def read_registers(self, registers: int) -> Union[Tuple[()], Tuple[int], Tuple[int, int]]:
        return tuple(self.ram_read(self.increment_pc()) for _ in range(registers))

    def run(self) -> None:
        """Run the CPU."""

        while True:
            instruction = self.ram_read(self.increment_pc())

            try:
                registers, cb = instructions[instruction]
            except KeyError:
                print(f'Unknown instruction {instruction} at address {self.pc}')
                sys.exit()

            cb(self, *self.read_registers(registers))
