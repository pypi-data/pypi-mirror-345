

def extend_bitstr(bit_str:str, ext_bit:str='0', bit_len:int=12) -> str:
    # Extend a bitstring to 'bit_len' length using 'extend_bit' as the extra padding
    return (ext_bit * (bit_len - len(bit_str))) + bit_str


def twos_complement(value:int, bit_width:int) -> int:
    # 2's complement on an int with a given bit length result
    return ((1 << bit_width) - value) & ((1 << bit_width) - 1)


def twos_complement_str(bit_str:str) -> str:
    """
    convert a bitstring -> 2's complement of bitstring
    :param bit_str: str - bitstring
    :return: str - 2's complement of input string
    """
    return format(twos_complement(int(bit_str, 2),len(bit_str)), f"0{len(bit_str)}b")
