import unittest
from riscvlib.instruction import (Instruction, translate_pseudo_instruction, parse_riscv_instruction_line,
                                  IInstruction, CSRInstruction, RInstruction, BInstruction)


class TestBaseInstructions(unittest.TestCase):
    """
    Test known good bit patterns
    https://luplab.gitlab.io/rvcodecjs/#q=sub+x1,+x15,+x7&abi=false&isa=AUTO
    """
    def test_R_instructions(self):
        # sub
        i = Instruction.from_line("sub x1, x15, x7")
        self.assertEqual("01000000011101111000000010110011", i.to_bitstring())

        # and
        i = Instruction.from_line("and x1, a0, x5")
        self.assertEqual("00000000010101010111000010110011", i.to_bitstring())

        i = Instruction.from_line("sll x1, x2, x3")
        self.assertEqual("00000000001100010001000010110011", i.to_bitstring())

    def test_I_instructions(self):
        # Immediate type instructions

        i = Instruction.from_line("addi a0, a1, 42")
        self.assertEqual("00000010101001011000010100010011", i.to_bitstring())

        # overflow
        i = Instruction.from_line("addi a0, a1, 0xffff")
        self.assertEqual("11111111111101011000010100010011", i.to_bitstring())

        # neg immediate
        i = Instruction.from_line("andi a0, a1, -13")
        self.assertEqual("11111111001101011111010100010011", i.to_bitstring())

        i = Instruction.from_line("ori x9, x13, 1893")
        self.assertEqual("01110110010101101110010010010011", i.to_bitstring())

        # hex immediate also neg
        i = Instruction.from_line("ori s0, x12, 0xFED")
        self.assertEqual("11111110110101100110010000010011", i.to_bitstring())

        # I with 5 bit immed and func7
        i = Instruction.from_line("srai x1, x3, 31")
        self.assertEqual("01000001111100011101000010010011", i.to_bitstring())

        # test 12 bit overflow (signed)
        i = Instruction.from_line("addi x1, x2, -2200")
        self.assertEqual("01110110100000010000000010010011", i.to_bitstring())



    def test_IL_instructions(self):
        # type IL in the assembler, loads

        i = Instruction.from_line("lw s0, 0(t1)")
        self.assertEqual("00000000000000110010010000000011", i.to_bitstring())

        # overflow immed val
        i = Instruction.from_line("lw s0, 999999(t1)")
        self.assertEqual("11110100001000110010010000000011", i.to_bitstring())
        self.assertEqual(32,len(i.to_bitstring()))  # 32 bits

        # neg offset
        i = Instruction.from_line("lw s0, -12(t1)")
        self.assertEqual("11111111010000110010010000000011", i.to_bitstring())

        i = Instruction.from_line("lb s0, 10(t1)")
        self.assertEqual("00000000101000110000010000000011", i.to_bitstring())

        i = Instruction.from_line("lbu s0, 300(t1)")
        self.assertEqual("00010010110000110100010000000011", i.to_bitstring())

        i = Instruction.from_line("lhu s0, 2047(t1)")
        self.assertEqual("01111111111100110101010000000011", i.to_bitstring())

    def test_U_type_instructions(self):
        # U type  immediate is 20 bits (1,048,576)
        i = Instruction.from_line("lui x9, 21042")  # load upper immediate
        self.assertEqual("00000101001000110010010010110111", i.to_bitstring())

        # negative looking  hex number (treated as unsigned)
        i = Instruction.from_line("lui s0, 0xFADCE")  # load upper immediate
        self.assertEqual("11111010110111001110010000110111", i.to_bitstring())

        # int
        i = Instruction.from_line("auipc x1, 400")
        self.assertEqual("00000000000110010000000010010111", i.to_bitstring())

        # neg int
        i = Instruction.from_line("lui s0, 434999")  # load upper immediate
        self.assertEqual("01101010001100110111010000110111", i.to_bitstring())

    def test_S_type_instructions(self):

        # store word store contents of x8 into mem addr given by x4 -6
        i = Instruction.from_line("sw x8, -6(x4)")
        self.assertEqual("11111110100000100010110100100011", i.to_bitstring())

        # test __str__
        self.assertEqual("sw x8, -6(x4)", f"{i}")

        i = Instruction.from_line("sw x9, 12(x3)")
        self.assertEqual("00000000100100011010011000100011", i.to_bitstring())

        i = Instruction.from_line("sb x10, 64(x7)")
        self.assertEqual("00000100101000111000000000100011", i.to_bitstring())

    def test_B_instructions(self):
        # control flow
        i = BInstruction("beq", 3,4, -4096)
        self.assertEqual("10000000010000011000000001100011", i.to_bitstring())

        i = Instruction.from_line("beq x3, x4, 4094")
        self.assertEqual("01111110010000011000111111100011", i.to_bitstring())

        # neg
        i = Instruction.from_line("beq a0, a1, -66")
        self.assertEqual("11111010101101010000111111100011", i.to_bitstring())

        i = Instruction.from_line("beq a0, a1, 2")
        self.assertEqual("00000000101101010000000101100011", i.to_bitstring())

        i = Instruction.from_line("beq a0, a1, -2")
        self.assertEqual("11111110101101010000111111100011", i.to_bitstring())

        i = Instruction.from_line("bge a0, a1, -20")
        self.assertEqual("11111110101101010101011011100011", i.to_bitstring())

        i = Instruction.from_line("blt a0, a1, -20")
        self.assertEqual("11111110101101010100011011100011", i.to_bitstring())

        i = Instruction.from_line("bne x13, x12, 2046")
        self.assertEqual("01111110110001101001111101100011", i.to_bitstring())
        # test __str__
        self.assertEqual("bne x13, x12, 2046", f"{i}")

    def test_uj_Instructions(self):
        i = Instruction.from_line("jal ra, 2")  # Jump and link, compressed
        self.assertEqual("00000000001000000000000011101111", i.to_bitstring())

        i = Instruction.from_line("jal ra,5000")  # Jump and link
        self.assertEqual("00111000100000000001000011101111", i.to_bitstring())
        # neg
        i = Instruction.from_line("jal x0, -64")  # backwards as in 'j .loop_start'
        self.assertEqual("11111100000111111111000001101111", i.to_bitstring())
        # neg
        i = Instruction.from_line("jal x0, -1000000")  # back wards as in 'j .way_back'
        self.assertEqual("11011100000100001011000001101111", i.to_bitstring())

    def test_ecall_ebreak(self):
        i = Instruction.from_line("ecall")  #
        self.assertEqual("00000000000000000000000001110011", i.to_bitstring())

        i = Instruction.from_line("ebreak")  #
        self.assertEqual("00000000000100000000000001110011", i.to_bitstring())


class TestPseudoInstructions(unittest.TestCase):

    def test_selection(self):
        test_data = [
            ("li x1, 55", ["addi x1, x0, 55"]),
            ("mv a0, x3", ["addi a0, x3, 0"]),
            ("nop", ["addi x0, x0, 0"]),
            ("not x3, x4", ["xori x3, x4, -1"]),
            ("neg x5, x7", ["sub x5, x0, x7"]),
            ("j -40", ["jal x0, -40"]),
            ("ret", ["jalr x0, x1, 0"]),
            ("call 4000", ["jal x1, 4000"]),
            ("bnez x5, -60", ["bne x5, x0, -60"]),
            ("ble x1, x2, 44", ["bge x2, x1, 44"]),
            ("bgt x1, x2, 60", ["blt x2, x1, 60"]),
            ("bgtu x1, x2, 64", ["bltu x2, x1, 64"]),
            ("bleu x1, x2, -68", ["bgeu x2, x1, -68"]),
        ]

        for tup in test_data:
            m, args = parse_riscv_instruction_line(tup[0])
            out = translate_pseudo_instruction(m, *args)
            self.assertEqual(tup[1], out, f"Pseudo Failed on '{tup[0]}'")

    def test_pseudo_expands_multiple_instructs(self):
        # 'la' expands to 2 instructions
        out = translate_pseudo_instruction("la", "x3", "4000")
        self.assertEqual(2, len(out))


class TestBExtension(unittest.TestCase):

    def test_R_B_instructions(self):
        i = Instruction.from_line("andn x1, x2, x3")
        self.assertEqual("01000000001100010111000010110011", i.to_bitstring())

    def test_I_B_instructions(self):
        # Immediate type instructions
        i = Instruction.from_line("clz x1, x3")
        self.assertEqual("01100000000000011001000010010011", i.to_bitstring())

        # no immd value
        i2 = IInstruction('clz', 'x1', 3, None)
        self.assertEqual("01100000000000011001000010010011", i2.to_bitstring())


class TestFExtension(unittest.TestCase):

    def test_F_instructions(self):
        i = Instruction.from_line("fadd.s f1, f5, f6")  # R type instruction
        # note: RM encoded for nearest by default
        self.assertEqual("00000000011000101000000011010011", i.to_bitstring())

        i = Instruction.from_line("fsgnj.s f1, ft2, f5")  # R type instruction
        # note: RM encoded for nearest by default
        self.assertEqual("00100000010100010000000011010011", i.to_bitstring())

    def test_F_pseudo(self):
        out = translate_pseudo_instruction("fmv.s", "f1", "ft2")
        self.assertEqual('fsgnj.s f1, ft2, ft2', out[0])

        out = translate_pseudo_instruction("fsrm", "x1")
        self.assertEqual('csrrw x0, 2, x1', out[0])

        out = translate_pseudo_instruction("fsflags", "x1")
        self.assertEqual('csrrw x0, 1, x1', out[0])

        out = translate_pseudo_instruction("frrm", "x1")
        self.assertEqual('csrrs x1, 2, x0', out[0])

    def test_F_R4_instructions(self):
        i = Instruction.from_line("fmadd.s f1, f5, f6, f7")  # R type instruction
        # note: RM encoded for nearest by default
        self.assertEqual("00111000011000101000000011000011", i.to_bitstring())

        i = Instruction.from_line("fnmadd.s f1, f5, f6, f7")  # R type instruction
        # note: RM encoded for nearest by default
        self.assertEqual("00111000011000101000000011001111", i.to_bitstring())

        # using R instruction class
        i2 = RInstruction('fnmadd.s', 'f1', 'f5', 'f6', rs3='f7')
        self.assertEqual("00111000011000101000000011001111", i2.to_bitstring())


class Test_CSR_Extension(unittest.TestCase):

    def test_csrrw(self):

        i = Instruction.from_line("csrrw x1, mie, x5")
        self.assertEqual("00110000010000101001000011110011", i.to_bitstring())

        i = CSRInstruction('csrrw', 'x1', 'mie', 'x5')
        self.assertEqual("00110000010000101001000011110011", i.to_bitstring())

    def test_csrrs(self):
        i = Instruction.from_line("csrrs x10, 0x300, x11")  # Read mcycle, store in x10, and set IE in mie
        self.assertEqual("00110000000001011010010101110011", i.to_bitstring())

        i = CSRInstruction('csrrs', 'x10', 0x300, 'x11')
        self.assertEqual("00110000000001011010010101110011", i.to_bitstring())

    def test_csrrwi(self):
        i = Instruction.from_line("csrrwi a0, mcycle, 0x0f")
        self.assertEqual("10110000000001111101010101110011", i.to_bitstring())
