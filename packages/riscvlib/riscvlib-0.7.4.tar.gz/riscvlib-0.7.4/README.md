# riscvlib  
  
Resources for working with RISC-V assembly in Python. 
Supporting instruction creation, pseudo instruction translation and register lookup for extenions: 
- I Base Instruction Set
- M Multiply and Divide
- F Single precision floating point
- B (Zba, Zbb, Zbc, Zbs) bit manipulation
- Zifencei  ebreak and ecall 
- Zicsr Control Status Register instructions

  
# Installation  
The package can be installed using pip:  
  
	 $ pip install riscvlib  
 
# Examples  
  
## Instruction, Static creation from a string
``` python
>> from riscvlib.instruction import Instruction  

>> i = Instruction.from_line("add x1, x2, x3")
>> print(i) 
add x1, x2, x3  
>> i.to_bytes() 
b'\xb3\x001\x00'  
>> i  
RInstruction 'add' ['x1', 'x2', 'x3']
```

## Specific Instruction Type
``` python
>> from riscvlib.instruction import RInstruction, IInstruction

>> r_instr = RInstruction("add", "x1", "x2", "a2")
>> print(r_instr)
add x1, x2, a2

>> i_instr = IInstruction("andi", "a0", "a1", -13)
>> print(i_instr)
andi a0, a1, -13
>> i_instr.to_bytes()  # note: bytes are 'little endian' ordered
b'\x13\xf55\xff'

>> i = CSRInstruction('csrrw', 'x1', 'mie', 'x5')
>> i.to_bitstring()
"00110000010000101001000011110011"

```

## Pseudo Instruction Translation
``` python
>> from riscvlib.instruction import translate_pseudo_instruction

>> out_list = translate_pseudo_instruction("mv", "a0", "x30")
>> print(out_list)
['addi a0, x30, 0']

>> out_list = translate_pseudo_instruction("la", "a0", "400")
>> print(out_list)
['lui a0, %hi(400)', 'addi a0, a0, %lo(400)']
```

## Instruction Data
``` python
>> from riscvlib.risvdata import INSTRUCTION_MAP

>> INSTRUCTION_MAP['mul']
('MUL', '0110011', '000', '0000001', 'R', 'm', '32/64')
# (name, opcode, func3, func7, itype, extension, rv32/rv64)

oppcode, func3, func7 = INSTRUCTION_MAP['fmadd.s'][1:4]
```

# Project Intent
The project has reached the MVP(Minimum Viable Product) state. It does what I want it to do, and I am
reasonably sure that no major bugs exist. I built this to use in my own projects
after I found Python Risc-v tools somewhat lacking. I will fix bugs as they crop
up. I will add features as I need them, or as they are requested.

This is not an industrial strength library and is targeted at 
hobbyists/educational use. I've made readability, ease of use and
simplicity priorities.

No warranties either stated or implied are associated with this project.

Use the code, or just copy the data that I've compiled from
multiple sources, often conflicting with each other on the exact details.

# Limitations
 - F extension Rounding Modes hardcoded to 'Nearest'(000)

# Future
 - A, C and D extensions



