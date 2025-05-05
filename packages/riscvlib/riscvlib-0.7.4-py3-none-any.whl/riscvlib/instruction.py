import re
from riscvlib.riscvdata import REGISTER_MAP, PSEUDO_INSTRUCTION_MAP, INSTRUCTION_MAP, CSR_REG_LOOKUP
from riscvlib.utils import extend_bitstr, twos_complement


def translate_pseudo_instruction(mnemonic, *args):
    """
    Convert a pseudo instruction into one or more standard instructions and apply args
    :param mnemonic: str - the instruction mnemonic
    :param args: list - array of string args
    :return: list - strings; riscv isa instructions
    """
    actual_instructs = PSEUDO_INSTRUCTION_MAP[mnemonic]

    out = []
    # insert args
    for instr_str in actual_instructs:
        for i, arg in enumerate(args):
            # replace placeholder operands in the new instruction with real args
            instr_str = instr_str.replace(f"%arg{i}", arg)
        out.append(instr_str)
    return out


class Instruction:
    """
    Abstract instruction
    """
    mnemonic = None
    opcode = None
    func3 = None
    func7 = None
    _bits = None

    @staticmethod
    def from_line(text: str):
        """
        Create an instruction object from a line of text.
        :param text: string - the instruction i.e add x22, sp, x13
        :return: Instruction
        """
        def to_int(str_or_int):
            try:
                return int(str_or_int)
            except ValueError:
                return int(str_or_int, 16)

        mnemonic, args = parse_riscv_instruction_line(text)
        subtype = INSTRUCTION_MAP[mnemonic][7]

        if subtype == "R":
            return RInstruction(mnemonic, *args)
        elif subtype == "R4":
            return R4Instruction(mnemonic, *args)
        elif subtype == "CSR":  # Zicsr instructions
            return CSRInstruction(mnemonic, args[0], args[1], args[2])
        elif subtype == "CSRI":  # Zicsr immd instructions
            return CSRImmdInstruction(mnemonic, args[0], args[1], to_int(args[2]))
        elif subtype == "ENV":  # Zicsr environ calls
            return EnvInstruction(mnemonic)
        elif subtype == "I":
            return IInstruction(mnemonic, args[0], args[1], to_int(args[2]) if len(args) == 3 else 0)
        elif subtype == "IL":
            return ILInstruction(mnemonic, args[0], args[1], to_int(args[2]))
        elif subtype == "S":
            return SInstruction(mnemonic, args[0], args[1], to_int(args[2]))
        elif subtype == "UJ":
            return UJInstruction(mnemonic, args[0], to_int(args[1]))
        elif subtype == "U":
            return UInstruction(mnemonic, args[0], to_int(args[1]))
        elif subtype == "B":
            return BInstruction(mnemonic, args[0], args[1], to_int(args[2]))
        else:
            raise ValueError(f"Unknown mnemonic '{mnemonic}'")

    def to_bitstring(self):
        """
        Output value as a bitstring
        :return: str - the bit string
        """
        self._build()
        return self._bits

    def to_bytes(self):
        """
        :return: bytes - little endian order
        """
        instr_int = self.to_int()
        return instr_int.to_bytes(4, byteorder='little', signed=False)

    def to_int(self) -> int:
        """
        Convert instruction into an integer
        :return: int
        """
        self._build()
        return int(self._bits, 2)

    def _build(self):
        # do all the real work
        raise NotImplementedError("Implement in derived class")

    @staticmethod
    def _get_csr(csr):
        try:  # special case "0x300" instead of 0x300
            csr = int(csr, 16)
        except (ValueError, TypeError):
            pass
        return csr if isinstance(csr, int) else CSR_REG_LOOKUP[csr]

    @staticmethod
    def _get_reg(reg):
        return reg if isinstance(reg, int) else REGISTER_MAP[reg][1]

    @staticmethod
    def _imm2bits(imd:int, bit_len=12):
        # convert int --> bitstring of length bit_len, if neg perform 2's complement

        if imd < 0:
            # neg offsets get 2's comp sign extended
            val = twos_complement(abs(imd), bit_len)
            return f"{val:0{bit_len}b}"
        else:
            return f"{imd:0{bit_len}b}"

    def __repr__(self):
        return f"{self.__class__.__name__} '{self.mnemonic}'"


def parse_riscv_instruction_line(instruction):
    """
    Define a regular expression pattern to match RISC-V instructions
    :param instruction: string - The instruction in the form 'add rd,r1,r2' or 'sw RD, offset(r1)'
    :return: tuple - (mnemonic, *args)
    """
    pattern = r"^\s*([a-z\.]+)\s*(.*)$"

    # Match the instruction against the pattern
    match = re.match(pattern, instruction)
    if match:
        mnemonic, operands_str = match.groups()
        operands = [op.strip() for op in operands_str.split(",")]

        # fix for offset style args i.e. 'sw rd, -66(r1)' ignore funct calls
        if len(operands) > 1 and "(" in operands[1] and "%" not in operands[1]:
            r1 = operands[1].split("(")[1].strip(")")
            immd = operands[1].split("(")[0]
            operands = [operands[0], r1, immd]
        return mnemonic, operands
    else:
        raise ValueError(f"Invalid Instruction: '{instruction}'")


class RInstruction(Instruction):
    """
    Regular instruction i.e add x1, x3, x5
    """
    def __init__(self, mnemonic:str, rd, rs1, rs2, rs3=None):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rd, self.rs1, self.rs2 = rd, rs1, rs2
        self.rs3 = rs3

    def _build(self):
        rd = Instruction._get_reg(self.rd)
        rs1 = Instruction._get_reg(self.rs1)
        rs2 = Instruction._get_reg(self.rs2)

        if self.rs3 is not None:
            # R4 instruction used with instructions such as fmadd.s
            rs3 = Instruction._get_reg(self.rs3)
            self._bits = f"{rs3:05b}00{rs2:05b}{rs1:05b}{self.func3}{rd:05b}{self.opcode}"
        else:
            # normal R instruction
            self._bits = f"{self.func7}{rs2:05b}{rs1:05b}{self.func3}{rd:05b}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rd}, {self.rs1}, {self.rs2}"


class R4Instruction(Instruction):
    # R4 instruction subtype, used in f/d extension

    def __init__(self, mnemonic:str, rd, rs1, rs2, rs3):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rd, self.rs1, self.rs2, self.rs3 = rd, rs1, rs2, rs3

    def _build(self):
        rd = Instruction._get_reg(self.rd)
        rs1 = Instruction._get_reg(self.rs1)
        rs2 = Instruction._get_reg(self.rs2)
        rs3 = Instruction._get_reg(self.rs3)

        # R4 instruction used with instructions such as fmadd.s
        self._bits = f"{rs3:05b}00{rs2:05b}{rs1:05b}{self.func3}{rd:05b}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rd}, {self.rs1}, {self.rs2}, {self.rs3}"


class EnvInstruction(Instruction):
    # ecall, ebreak instructions
    def __init__(self, mnemonic: str, ):
        self.mnemonic = mnemonic

        self.func12 = "0"*11
        self.func12 += "1" if self.mnemonic == "ebreak" else "0"
        self.opcode, self.func3 = INSTRUCTION_MAP[self.mnemonic][1:3]

    def _build(self):
        self._bits = f"{self.func12}00000{self.func3}00000{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic}"


class IInstruction(Instruction):
    # Type I instruction
    # note: immed is limited to 5 bits for several instructions so that func7 can be encoded

    def __init__(self, mnemonic:str, rd:int|str, rs1:int|str, imm5_12:int):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rd, self.rs1 = rd, rs1
        # Some instructions (B ext) do not have an immed, support passing in None for positional imm arg
        self.imm5_12 = imm5_12 if imm5_12 is not None else 0

    def _build(self):
        rd = Instruction._get_reg(self.rd)
        rs1 = Instruction._get_reg(self.rs1)

        if self.func7 is not None:
            # some I type have a funct7 which needs to be encoded at the expense of the immediate val.
            immd5_signed_bin = Instruction._imm2bits(self.imm5_12, bit_len=5)
            self._bits = f"{self.func7}{immd5_signed_bin}{rs1:05b}{self.func3}{rd:05b}{self.opcode}"
        else:
            # Normal I type with 12 bit immediate
            immd12_signed_bin = Instruction._imm2bits(self.imm5_12)
            self._bits = f"{immd12_signed_bin[:12]}{rs1:05b}{self.func3}{rd:05b}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rd}, {self.rs1}, {self.imm5_12}"


class CSRImmdInstruction(Instruction):
    """CSRI (immediate) variant of 'I' instruction type
    """
    def __init__(self, mnemonic:str, rd:int|str, csr_reg:int|str, uimm5:int):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rd, self.csr, self.uimm5 = rd, csr_reg, uimm5

    def _build(self):
        rd = Instruction._get_reg(self.rd)
        csr = Instruction._get_csr(self.csr)
        # encode unsigned immd to 5 bits, discard excess bits
        uimmd5_bin = extend_bitstr(bin(self.uimm5)[2:], bit_len=5)[:5]
        self._bits = f"{csr:012b}{uimmd5_bin}{self.func3}{rd:05b}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rd}, {self.csr}, {self.uimm5}"


class CSRInstruction(Instruction):
    # CSR variant of 'I' instruction type
    def __init__(self, mnemonic:str, rd:int|str, csr_reg:int|str, rs1:int|str):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rd, self.rs1, self.csr = rd, rs1, csr_reg

    def _build(self):
        rd = Instruction._get_reg(self.rd)
        rs1 = Instruction._get_reg(self.rs1)
        csr = Instruction._get_csr(self.csr)
        # extended 12 bit unsigned
        csr_bin_12 = extend_bitstr(bin(csr)[2:], bit_len=12)
        self._bits = f"{csr_bin_12}{rs1:05b}{self.func3}{rd:05b}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rd}, {self.csr}, {self.rs1}"


class ILInstruction(Instruction):
    """
    covers load type IL instructions with the pattern:  inst rd, offset(r1)
    similar to S instruction
    "lb", "lw", "ld", "lbu", "lhu", "lwu",
    """
    def __init__(self, mnemonic:str, rd:int|str, rs1:int|str, imm12:int):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rd, self.rs1, self.imm12 = rd, rs1, imm12

    def _build(self):
        rd = Instruction._get_reg(self.rd)
        rs1 = Instruction._get_reg(self.rs1)  # holds target address that may be offset
        offset_bin = Instruction._imm2bits(self.imm12)
        self._bits = f"{offset_bin[:12]}{rs1:05b}{self.func3}{rd:05b}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rd}, {self.imm12}({self.rs1})"


class SInstruction(Instruction):
    """
    imm[11:5] rs2 rs1 funct3 imm[4:0] opcode     S-type
    i.e. sw rs2,+-offset(rs1)
    The SW, SH, and SB instructions store 32-bit, 16-bit, and 8-bit values from the low
    bits of register rs2 to memory.
    i.e. sw s0,24(sp)
    "sw", "sb", "sh", "sd"
    """
    def __init__(self, mnemonic:str, rs2:int|str, rs1:int|str, imm12:int):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rs2, self.rs1, self.imm12 = rs2, rs1, imm12

    def _build(self):
        rs2 = Instruction._get_reg(self.rs2)  # value to store
        rs1 = Instruction._get_reg(self.rs1)  # holds target address offset by immed

        # offset val for rs1 --> sign extended 12 bits
        imm12 = Instruction._imm2bits(self.imm12)
        self._bits = f"{imm12[0:7]}{rs2:05b}{rs1:05b}{self.func3}{imm12[7:12]}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rs2}, {self.imm12}({self.rs1})"


class UInstruction(Instruction):
    """
    i.e. LUI x2, 0xfffff000
    """
    def __init__(self, mnemonic:str, rd:int|str, imm20:int):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rd, self.imm20 = rd, imm20

    def _build(self):
        rd = Instruction._get_reg(self.rd)
        immd20_bin = Instruction._imm2bits(self.imm20, bit_len=20)
        self._bits = f"{immd20_bin[:20]}{rd:05b}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rd}, {self.imm20}"


class UJInstruction(Instruction):
    """
     21-bit value in the range of [−1048576..1048574] [-0x100000..0x0ffffe]1561
     representing a pc-relative offset to the target address
     jal x0, -8
    """
    def __init__(self, mnemonic:str, rd:int|str, imm20:int):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rd, self.imm20 = rd, imm20

    def _build(self):
        rd = Instruction._get_reg(self.rd)
        # valid immediate range(-2^20 to  2^20 - 1)

        # dropping the lsb; only even numbers; getting 21 bits
        immd21_bin = Instruction._imm2bits(self.imm20, bit_len=21)

        sign_bit = immd21_bin[0]
        low_10 = immd21_bin[10:20]  # this is where the lsb dies
        bit_11 = immd21_bin[10]
        hi_8 = immd21_bin[1:9]

        encoded_imm20 = f"{sign_bit}{low_10}{bit_11}{hi_8}"
        self._bits = f"{encoded_imm20[:20]}{rd:05b}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rd}, {self.imm20}"


class BInstruction(Instruction):
    """
    Branching instructions
    i.e. beq x3, x0, 33
    beq rs1, rs2, imm
    -4097 > immd < 4096   13 bits toss the lsb, always even so zero assumed
    """
    def __init__(self, mnemonic:str, rs1:int|str, rs2:int|str, imm12:int):
        self.mnemonic = mnemonic
        self.opcode, self.func3, self.func7 = INSTRUCTION_MAP[self.mnemonic][1:4]
        self.rs1, self.rs2, self.imm12 = rs1, rs2, imm12

    def _build(self):
        # imm7 rs2 rs1 func3 imm5 opcode
        rs1 = Instruction._get_reg(self.rs1)
        rs2 = Instruction._get_reg(self.rs2)
        ib13 = Instruction._imm2bits(self.imm12, bit_len=13)  # bit 13 will be dropped
        self._bits = f"{ib13[0]}{ib13[2:8]}{rs2:05b}{rs1:05b}{self.func3}{ib13[8:12]}{ib13[1]}{self.opcode}"

    def __str__(self):
        return f"{self.mnemonic} {self.rs1}, {self.rs2}, {self.imm12}"
