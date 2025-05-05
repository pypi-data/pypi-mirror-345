import dataclasses
from xctype import *


def test():
    a = U32()
    print(a, a.size())
    a.val = 32
    print(a, a.size())
    if a > 32:
        raise RuntimeError()
    if a < 32:
        raise RuntimeError()
    if a != 32:
        raise RuntimeError()
    if a == 32:
        pass
    else:
        raise RuntimeError()
    b = U16()
    print(b, b.size())
    b.val = 16
    print(b, b.size())

    s_type = make_struct('only_primitive_struct_auto', a=U32(), b=U16())
    s = s_type()
    print(s, s.size())
    ba = bytearray()
    ba += a.to_bytes()
    ba += b.to_bytes()
    s.from_bytes(ba)
    print(s, s.size())
    s.m_a = 0xAA
    print(s)
    s.m_a = 0x10203040
    print(s)
    s_zeroes = s_type()
    s_zeroes.fill(0)
    s3 = s & s_zeroes
    if s3 != s_zeroes:
        raise RuntimeError()
    s_ones = ~s_zeroes
    s5 = s & s_ones
    if s5 != s:
        raise RuntimeError()
    s6 = s | s_ones
    if s6 != s_ones:
        raise RuntimeError()

    # exit()

    array = Array(elem_class=U16, num_elem=3)
    print(array, array.size())
    array.from_bytes(ba)
    print(array, array.size())
    array.fill(0)
    print(array, array.size())
    print(array[0])
    array[0] = 1
    print(array[0])
    for a in array:
        print(a)
    for i in range(0, len(array)):
        print(array[i])

    s = make_struct('struct_with_array_auto', a=U16(), b=Array(elem_class=U16, num_elem=2))()
    print(s, s.size())
    print(s.to_str(deep=True))
    s.from_bytes(ba)
    print(s, s.size())
    print(s.to_str(deep=True))

    asize = symbols('asize')
    array = Array(elem_class=U16, num_elem=asize)
    print(array, array.size())

    members_t = make_array(elem_cls=U16, n_elem=int_symbol('size', granularity=2) / 2)
    struct_with_var_len_array_auto_class = make_struct(
        'struct_with_var_len_array_auto', size=U16(), members=members_t()
    )
    s = struct_with_var_len_array_auto_class()
    ssize = s.size()
    print(s, s.size())
    print(s.to_str(deep=True))
    ba = bytearray()
    size = U16(8)
    ba += size.to_bytes()
    for i in range(0, size // 2):
        e = U16()
        e.val = i
        ba += e.to_bytes()
    s.from_bytes(ba)
    print(s, s.size())
    print(s.to_str(deep=True))
    print(s.m_size)
    print(s.m_size.size())
    print(s.m_members)

    print(s, s.offsets)

    s = struct_with_var_len_array_auto_class()
    s.m_size = 4
    m = bytes(4)
    s.m_members.from_bytes(m)
    s.to_bytes()

    higher_level_var_len = make_struct(
        'higher_level_var_len', a=U32(), b=struct_with_var_len_array_auto_class(), c=U32()
    )
    a = higher_level_var_len()
    a.m_a.val = 1
    a.m_c.val = 2
    print(a)
    print(s)
    a.m_b.copy(s)
    if not isinstance(a.size(), int):
        raise RuntimeError('size should be int')

    a = U8(1)
    print(type(a), a)
    test = [1 + a, a + 1, 1 - a, a - 1, a - 2, a - 256, a - 257, a - 258, 0 - a, 256 - a]
    for e in test:
        print(type(e), e)

    struct_bit_size = make_struct('struct_bit_size', flag0=Bool(), flag1=Bool())
    s = struct_bit_size()
    print(s, s.bit_size(), s.size())
    c = U64()
    print(c, c.bit_size(), c.size())

    s = struct_with_var_len_array_auto_class()
    print(s.to_c_typedef(tab='    '))
    print(s.gen_check_against_c())
    print(s.m_members.__class__)
    with open('main.c', 'w') as f:
        print(gen_check_against_c_main([struct_with_var_len_array_auto_class], tab='    '), file=f)

    m_t = make_array(elem_cls=U64, n_elem=2)
    e_t = make_array(elem_cls=U64, n_elem=3)

    @dataclass
    class ME:
        m: ... = dataclasses.field(default_factory=m_t)  # ugly boiler plate code
        e: ... = dataclasses.field(default_factory=e_t)

    me_t = make_struct('me_t', packed=True, **vars(ME()))

    me = me_t()
    print(me.to_c_typedef())

    me2_t = make_struct('me_t', packed=True, **{'m': m_t(), 'e': e_t()})

    me = me2_t(fill_byte=0)
    print(me.to_c_typedef())
    print(me)
    me = me2_t(fill_byte=0xFF)
    print(me)
    me = me2_t(fill_byte=0x55)
    print(me)

    bitfields_t = make_struct(
        'bitfields_t', packed=True, **{'a': BitField32(), 'b': BitField32(), 'c': BitField32(size=32 - 2)}
    )

    a = bitfields_t(fill_byte=0)
    b = bitfields_t(fill_byte=0)
    a.m_a = 1
    b.m_b = 1
    ab = a & b
    zeroes = bitfields_t(fill_byte=0)
    if ab != zeroes:
        raise RuntimeError()
    print(ab)
    ones = bitfields_t(fill_byte=0)
    ones.m_a = 1
    ones.m_b = 1
    ab = a | b
    print(ab)
    print(ones)
    if ab != ones:
        raise RuntimeError()
    if ab.m_c != 0:
        raise RuntimeError()
    c = bitfields_t(fill_byte=0)
    print(c)
    d = bitfields_t(fill_byte=0xFF)
    c.copy(d)
    print(c)
    if c != 0xFFFFFFFF:
        raise RuntimeError()

    array = Array(elem_class=me2_t, num_elem=3)
    print(array, array.size())
    array.fill(0)
    print(array, array.size())
    print(array.hexdump())

    me = me2_t()
    me.m_m = m_t(fill_byte=0)
    me.m_e = e_t(fill_byte=0)
    try:
        me.m_not_a_member = None
        raise RuntimeError('TypeError shall have been raised')
    except TypeError:
        pass
