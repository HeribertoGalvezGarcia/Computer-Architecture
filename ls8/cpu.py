from __future__ import annotations

"""CPU functionality."""

import sys
import datetime
from typing import List, Tuple, Union


def iret(cpu: CPU) -> None:
    for i in range(6, -1, -1):
        cpu.reg[i] = cpu.pop_stack()
    cpu.fl = cpu.pop_stack()
    cpu.pc = cpu.pop_stack()


instructions = {
    0b00000000: lambda cpu: ...,  # NOP
    0b00000001: lambda cpu: sys.exit(),  # HLT
    0b10000010: lambda cpu, reg1, reg2: cpu.reg.__setitem__(reg1, reg2),  # LDI
    0b10000011: lambda cpu, reg1, reg2: cpu.reg.__setitem__(reg1, cpu.ram[cpu.reg[reg2]]),  # LD
    0b10000100: lambda cpu, reg1, reg2: cpu.ram.__setitem__(cpu.reg[reg1], cpu.reg[reg2]),  # ST
    0b01000101: lambda cpu, reg1: cpu.push_stack(cpu.reg[reg1]),  # PUSH
    0b01000110: lambda cpu, reg1: cpu.reg.__setitem__(reg1, cpu.pop_stack()),  # POP
    0b01000111: lambda cpu, reg1: print(cpu.reg[reg1]),  # PRN
    0b01001000: lambda cpu, reg1: print(chr(cpu.reg[reg1])),  # PRA
    0b01010000: lambda cpu, reg1: (cpu.push_stack(cpu.pc), setattr(cpu, 'pc', cpu.reg[reg1])),  # CALL
    0b00010001: lambda cpu: setattr(cpu, 'pc', cpu.pop_stack()),  # RET
    # 0b01010010: lambda cpu, reg1: ...,  # INT
    0b00010011: iret,  # IRET
    0b01010100: lambda cpu, reg1: setattr(cpu, 'pc', cpu.reg[reg1]),  # JMP
    0b01010101: lambda cpu, reg1: setattr(cpu, 'pc', cpu.reg[reg1]) if cpu.fl == 1 else None,  # JEQ
    0b01010110: lambda cpu, reg1: setattr(cpu, 'pc', cpu.reg[reg1]) if cpu.fl != 1 else None,  # JNE
    0b01010111: lambda cpu, reg1: setattr(cpu, 'pc', cpu.reg[reg1]) if cpu.fl == 2 else None,  # JGT
    0b01011000: lambda cpu, reg1: setattr(cpu, 'pc', cpu.reg[reg1]) if cpu.fl == 4 else None,  # JLT
    0b01011001: lambda cpu, reg1: setattr(cpu, 'pc', cpu.reg[reg1]) if cpu.fl != 2 else None,  # JLE
    0b01011010: lambda cpu, reg1: setattr(cpu, 'pc', cpu.reg[reg1]) if cpu.fl != 4 else None,  # JGE
    0b10100000: lambda cpu, reg1, reg2: cpu.alu('ADD', reg1, reg2),  # ADD
    0b10100001: lambda cpu, reg1, reg2: cpu.alu('SUB', reg1, reg2),  # SUB
    0b10100010: lambda cpu, reg1, reg2: cpu.alu('MUL', reg1, reg2),  # MUL
    0b10100011: lambda cpu, reg1, reg2: cpu.alu('DIV', reg1, reg2),  # DIV
    0b10100100: lambda cpu, reg1, reg2: cpu.alu('MOD', reg1, reg2),  # MOD
    0b01100101: lambda cpu, reg1: cpu.alu('INC', reg1),  # INC
    0b01100110: lambda cpu, reg1: cpu.alu('DEC', reg1),  # DEC
    0b10100111: lambda cpu, reg1, reg2: cpu.alu('CMP', reg1, reg2),  # CMP
    0b10101000: lambda cpu, reg1, reg2: cpu.alu('AND', reg1, reg2),  # AND
    0b01101001: lambda cpu, reg1: cpu.alu('NOT', reg1),  # NOT
    0b10101010: lambda cpu, reg1, reg2: cpu.alu('OR', reg1, reg2),  # OR
    0b10101011: lambda cpu, reg1, reg2: cpu.alu('XOR', reg1, reg2),  # XOR
    0b10101100: lambda cpu, reg1, reg2: cpu.alu('SHL', reg1, reg2),  # SHL
    0b10101101: lambda cpu, reg1, reg2: cpu.alu('SHR', reg1, reg2),  # SHR
}


class CPU:
    """Main CPU class."""

    pc: int
    ram: List[int]
    reg: List[int]
    fl: int

    def __init__(self) -> None:
        """Construct a new CPU."""

        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 7 + [0xF4]
        self.fl = 0

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

    def alu(self, op: str, reg_a: int, reg_b: int = None) -> None:
        """ALU operations."""

        if op == 'ADD':
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'SUB':
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'DIV':
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == 'MOD':
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == 'INC':
            self.reg[reg_a] += 1
        elif op == 'DEC':
            self.reg[reg_a] -= 1
        elif op == 'CMP':
            a = self.reg[reg_a]
            b = self.reg[reg_b]
            self.fl = 0b100 if a < b else 0b10 if a > b else 1
        elif op == 'AND':
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == 'NOT':
            self.reg[reg_a] ^= 0b11111111
        elif op == 'OR':
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == 'XOR':
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == 'SHL':
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == 'SHR':
            self.reg[reg_a] >>= self.reg[reg_b]
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

        t1 = datetime.datetime.now()

        while True:
            if self.reg[5] and self.reg[6]:
                masked_interrupts = self.reg[5] & self.reg[6]

                for i in range(8):
                    if not ((masked_interrupts >> i) & 1):
                        continue

                    self.reg[6] &= ~(1 << i)
                    self.push_stack(self.pc)
                    self.push_stack(self.fl)
                    for j in range(7):
                        self.push_stack(self.reg[j])
                    self.pc = self.ram[i + 0xF8]
                    break

            t2 = datetime.datetime.now()
            if (t2 - t1).seconds >= 1:
                t1 = t2
                self.reg[6] |= 1

            instruction = self.ram_read(self.increment_pc())

            try:
                cb = instructions[instruction]
            except KeyError:
                print(f'Unknown instruction {instruction} at address {self.pc}')
                sys.exit()

            cb(self, *self.read_registers(instruction >> 6))
