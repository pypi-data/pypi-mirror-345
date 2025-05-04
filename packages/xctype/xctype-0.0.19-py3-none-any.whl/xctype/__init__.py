# from abc import ABC, abstractmethod
from sympy import symbols
from pysatl import Utils
from collections import OrderedDict
from ordered_set import OrderedSet
from io import BytesIO
from dataclasses import dataclass
from collections.abc import MutableMapping, MutableSequence, MutableSet
import copy
import logging


class NotInitializedError(RuntimeError):
    pass


def ceildiv(a, b):
    # return -(a // -b) # fast but confusing when it reach user doc due to var size members
    return (a + b - 1) // b


def hexdump(buf, offset=0):
    class Hexdump:
        header = 'Offset    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F\n'

        def __init__(self, buf, off=0):
            if isinstance(buf, str):
                self.buf = buf.encode()
            else:
                self.buf = buf
            self.off = off

        def __iter__(self):
            last_bs, last_line = None, None
            for i in range(0, len(self.buf), 16):
                bs = bytearray(self.buf[i : i + 16])
                line = '{:08x}  {:23}  {:23}  |{:16}|'.format(
                    self.off + i,
                    ' '.join(f'{x:02x}' for x in bs[:8]),
                    ' '.join(f'{x:02x}' for x in bs[8:]),
                    ''.join(chr(x) if 32 <= x < 127 else '.' for x in bs),
                )
                if bs == last_bs:
                    line = '*'
                if bs != last_bs or line != last_line:
                    yield line
                last_bs, last_line = bs, line
            yield f'{self.off + len(self.buf):08x}'

        def __str__(self):
            return Hexdump.header + '\n'.join(self)

        def __repr__(self):
            return Hexdump.header + '\n'.join(self)

    return Hexdump(buf, off=offset).__str__()


def first(s):
    """Return the first element from an ordered collection
    or an arbitrary element from an unordered collection.
    Raise StopIteration if the collection is empty.
    """
    return next(iter(s))


def last(s):
    return next(reversed(s))


def int_symbol(name, *, granularity=1):
    symbol = symbols(name, integer=True)
    if granularity > 1:
        symbol = (symbol // granularity) * granularity
    return symbol


def eval_expr(expr, context):
    variables = sorted(expr.free_symbols)
    expr_ctx = {}
    for var in variables:
        var_str = str(var)
        try:
            val = context[var_str]
            if val is not None:
                expr_ctx[var] = val
        except KeyError:
            pass
    evaluated = expr.subs(expr_ctx)
    # print(expr,expr_ctx,evaluated)
    return evaluated


def gen_check_against_c_main(classes, *, skip_illegal_struct=False, tab='  '):
    out = """
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <stdlib.h>
#define xstr(a) str(a)
#define str(a) #a
#define OFFSET(s,member) ((uintptr_t)&s.member - (uintptr_t)&s)
#define CHECK_EQUAL(a,b) do{if(a!=b){printf("ERROR: a=0x%lx, b=0x%lx\\n",(uint64_t)(a),(uint64_t)(b));exit(-1);}}while(0)
#define CHECK_MEMBER_OFFSET(s,member,offset) do{printf("  checking %s offset is 0x%lx\\n",xstr(member),(uint64_t)offset);CHECK_EQUAL(OFFSET(s,member),offset);}while(0)
"""
    all_classes = OrderedSet()
    for cls in classes:
        i = cls()
        all_classes |= i.get_classes()
    for cls in all_classes:
        i = cls()
        if skip_illegal_struct:
            if not i.legal_c_struct:
                continue
        typedef = i.to_c_typedef(tab=tab)
        if typedef:
            out += typedef + '\n'

    out += 'int main(){\n'

    for cls in all_classes:
        i = cls()
        code = i.gen_check_against_c(indent=tab, tab=tab)
        if code:
            out += code + '\n'

    out += f'{tab}return 0;\n'
    out += '}\n'

    return out


class XCType:

    @property
    def val(self):
        return self.to_bytes()

    @val.setter
    def val(self, value):
        self.from_bytes(value)

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def offsets(self):
        if self._offsets is None:
            self._compute_offsets()
        return self._offsets

    @property
    def gaps(self):
        if self._gaps is None:
            self._compute_offsets()
        return self._gaps

    @property
    def packed(self):
        return self._packed

    @property
    def legal_c_struct(self):
        if self._legal_c_struct is None:
            if self.is_primitive() or self.is_array():
                self._legal_c_struct = False
            else:
                self._legal_c_struct = True
                var_size_members = []
                for name in self._members:
                    m = self._members[name]
                    if m.is_packet():
                        logging.debug(f'{self._type_name} not legal struct because {m._type_name} is not legal struct')
                        self._legal_c_struct = False
                    if m.variable_size:
                        var_size_members.append(name)
                if len(var_size_members) > 1:
                    logging.debug(
                        f'{self._type_name} not legal struct because it contains {len(var_size_members)} variable size members'
                    )
                    self._legal_c_struct = False
                if len(var_size_members) == 1:
                    if var_size_members[0] != last(self._members):
                        logging.debug(
                            f'{self._type_name} not legal struct because variable size member is not the last one'
                        )
                        self._legal_c_struct = False
        return self._legal_c_struct

    @property
    def variable_size(self):
        if self._variable_size is None:
            self._variable_size = False
            for name in self._members:
                m = self._members[name]
                self._variable_size |= m.variable_size
        return self._variable_size

    def __init__(self, init=None, *, packed=False, fill_byte: int | None = None):
        self._type_name = None
        self._members = None
        self._value = None
        self._context = None
        self._offsets = None
        self._gaps = None
        self._packed = packed
        self._legal_c_struct = None
        self._variable_size = None
        if init is not None:
            self._do_init(init, fill_byte=fill_byte)

    def _do_init(self, init, *, fill_byte: int | None = None):
        if init is not None:
            if not isinstance(init, bytes):
                init = init.to_bytes()
            self._compute_offsets()
            self.from_bytes(init)
            self._offsets = None
            self._gaps = None
        elif fill_byte is not None:
            size = self.size()
            fill_bytes = bytearray([fill_byte] * size)
            self.from_bytes(fill_bytes)

    def copy(self, other):
        data = other.to_bytes()
        self.from_bytes(data)

    def set_member(self, name, value):
        self._members[name.lower()].val = value
        size = self.size()
        if not isinstance(size, int):
            expression = size
            variables = [str(x) for x in expression.free_symbols]
            variables = sorted(variables)
            if name in variables:
                self._offsets = None  # recompute to take the change into account
                self._gaps = None

    def set_member_from_bytes(self, name, dat):
        self._members[name.lower()].from_bytes(dat)
        size = self.size()
        if not isinstance(size, int):
            expression = size
            variables = [str(x) for x in expression.free_symbols]
            variables = sorted(variables)
            if name in variables:
                self._offsets = None  # recompute to take the change into account
                self._gaps = None
                # self._compute_offsets()

    def __str__(self):
        return self.to_str(deep=False)

    def __repr__(self):
        return self.to_str(deep=False)

    def to_str(self, *, deep=False, indent='', skip_long_data=False):
        if self._value is not None:
            # primitive type with concrete value
            return f'{indent}{self._value:#0{self.size()*2+2}x}'
        if self._members is None:
            # primitive type without concrete value
            return indent + self._type_name
        # struct
        out = f'{indent}{self._type_name} ({self.size_str()})\n'

        # return the value of each member
        indent += '  '
        for name in self._members:
            m = self._members[name]
            if deep:
                m_str = m.to_str(deep=True, indent=indent)
                out += f'{indent}{name}: {m_str}'
            else:
                out += f'{indent}{name}: {m._type_name} ({m.size_str()})'
                if m.is_initialized():
                    if m.is_primitive():
                        out += f' = {m}'
                    else:
                        out += f' = {Utils.hexstr(m.to_bytes(),skip_long_data=skip_long_data)}'
            out += '\n'
        return out

    @dataclass
    class VisitorState:
        parent: str = ''
        offset: int = 0
        offset_width: int = 0
        bit_offset: int = 0

    def _compute_offsets(self, *, state=None):
        out = {}
        gaps = {}
        state = self.VisitorState()
        if self.is_primitive() or self.is_array():
            pass  # nothing to do
        else:
            # struct
            # return the offset of each member
            last_alignement: int = 1024 * 1024 * 1024  # aligned with anything
            last_size_granularity: int = 1024 * 1024 * 1024  # aligned with anything
            for name in self._members:
                m = self._members[name]
                m._context = copy.deepcopy(self._context)
                full_name = f'{state.parent}{name}'
                if not m.has_bit_granularity():
                    if state.bit_offset > 0:
                        state.bit_offset = 0
                        state.offset += 1
                    if not self.packed:
                        alignement = m.alignement()
                        misalignement = state.offset % alignement
                        misalignement2 = 0
                        for i in [1, 2, last_size_granularity - 2, last_size_granularity - 1]:
                            misalignement3 = (last_alignement + last_size_granularity * i) % alignement
                            # print(misalignement2 , misalignement3)
                            # print(last_alignement , last_size_granularity)
                            if misalignement3 > misalignement2:
                                misalignement2 = misalignement3  # we assume the worst case
                        if not isinstance(misalignement, int):
                            # offset is symbolic
                            misalignement = misalignement2
                        if misalignement > misalignement2:  # check we computed indeed the worst case
                            raise RuntimeError()
                        if misalignement > 0:
                            gap_size = alignement - misalignement
                            gaps[full_name] = gap_size
                            state.offset += alignement - misalignement
                out[full_name] = state.offset, state.bit_offset
                if not m.is_primitive() and not m.is_array():
                    o = {}
                    g = copy.deepcopy(m.gaps)
                    for item in m.offsets.items():
                        key = f'{state.parent}{name}.{item[0]}'
                        val = item[1][0] + state.offset, item[1][1] + state.bit_offset
                        o[key] = val
                    out = out | o
                    gaps = gaps | g
                if m.has_bit_granularity():
                    total_bit_size = m.bit_size()
                    total_bit_offset = state.offset * 8 + state.bit_offset + total_bit_size
                    state.offset, state.bit_offset = divmod(total_bit_offset, 8)
                else:
                    # m._context = copy.deepcopy(self._context)
                    size = m.size()
                    if not isinstance(size, int):
                        free_symbols = size.free_symbols
                        expr_ctx = {}
                        for s in free_symbols:
                            ss = str(s)
                            if ss in self._context:
                                expr_ctx[ss] = self._context[ss]
                            else:
                                new_s = int_symbol(f'{state.parent}{name}.{ss}')
                                expr_ctx[ss] = new_s
                        size = size.subs(expr_ctx)
                    state.offset += size
                last_size_granularity = m.bit_granularity() // 8
                last_alignement = m.alignement()
                if self._context is not None and self._members[name]._value is not None:
                    self._context[name] = self._members[name]._value
        self._offsets = out
        self._gaps = gaps
        return out, gaps

    def offset(self, name):
        return self.offsets[name]

    class AsciidocVisitorState:
        def __init__(self, *, parent: str = '', offset_width: int = 0, offsets: dict = None, gaps: dict = None):
            if offsets is None:
                offsets = {}
            if gaps is None:
                gaps = {}
            self.parent = parent
            self.offset_width = offset_width
            self.offsets = copy.deepcopy(offsets)
            self.offsets[''] = (0, 0)
            self.gaps = gaps

    def to_asciidoc(self, *, deep=False, skip_long_data=True, title=None, values=False, state=None):
        top_level = state is None
        out = ''
        if top_level:
            if self.has_resolved_size():
                offset_width = 2 + ceildiv(self.size().bit_length(), 4)
            else:
                # size_str = str(self.size())
                # offset_width = len(size_str)
                offset_width = 4
            state = self.AsciidocVisitorState(offset_width=offset_width, offsets=self.offsets, gaps=self.gaps)
            if title is None:
                title = self._type_name
            out += '[%unbreakable]\n'
            out += f'.{title}'
            if values:
                out += """
[cols="<1,<3,<1,<5"]
[options="header",grid="all"]
|=======================
| Offset | Item | Size | Value
"""
            else:
                out += """
[cols="<1,<6,<1,<2"]
[options="header",grid="all"]
|=======================
| Offset | Item | Size | Type
"""

        def get_offset(s, full_name):
            nonlocal out
            o = state.offsets[full_name]
            offset, bit_offset = o
            if full_name in state.gaps:
                size = state.gaps[full_name]
                pad_offset = offset - size
                if isinstance(pad_offset, int):
                    pad_offset = f'{offset-size:#0{state.offset_width}x}'
                out += f'<| {pad_offset} <| - <| {size} <| PADDING\n'
            if isinstance(offset, int):
                offset_str = f'{offset:#0{state.offset_width}x}'
            else:
                offset_str = str(offset)
            if s.has_bit_granularity():
                offset_str = f'{offset_str}.{bit_offset}'
            return offset_str

        def output_offset_name_size(var, full_name):
            nonlocal out
            offset_str = get_offset(var, full_name)
            if var.has_bit_granularity():
                total_bit_size = var.bit_size()
                full_bytes, bits = divmod(total_bit_size, 8)
                out += f'<| {offset_str} <| {full_name} <| {full_bytes}.{bits} <|'
            else:
                size = var.size()
                size_str = str(size)
                if not isinstance(size, int):
                    grandparent = '.'.join(full_name.split('.')[0:-1])
                    if len(grandparent) > 0:
                        free_symbols = size.free_symbols
                        for s in free_symbols:
                            ss = str(s)
                            size_str = size_str.replace(ss, f'{grandparent}.{ss}')
                out += f'<| {offset_str} <| {full_name} <| {size_str} <|'

        if self.is_primitive() or self.is_array():
            output_offset_name_size(self, state.parent)
            if values:
                if self._value is None:
                    out += 'undefined'
                else:
                    # primitive type with concrete value
                    if self.is_array():
                        out += self.to_str(skip_long_data=skip_long_data)
                    else:
                        out += f'{self._value:#0{self.size()*2+2}x}'
            else:
                out += f'{self._type_name}'
            out += '\n'
        else:
            # struct
            if len(state.parent) > 0:
                state.parent += '.'
            # return the value of each member
            for name in self._members:
                m = self._members[name]
                if deep:
                    s = copy.deepcopy(state)
                    s.parent = f'{state.parent}{name}'
                    out += m.to_asciidoc(deep=True, skip_long_data=skip_long_data, values=values, state=s)
                else:
                    full_name = f'{state.parent}{name}'
                    output_offset_name_size(m, full_name)
                    out += ' '
                    if values:
                        if m.is_initialized():
                            if m.is_primitive() or m.is_array():
                                out += m.to_str(skip_long_data=skip_long_data)
                            else:
                                out += f'{Utils.hexstr(m.to_bytes(),skip_long_data=skip_long_data)}'
                        else:
                            out += 'undefined'
                    else:
                        out += f'{m._type_name}'
                    out += '\n'

        if top_level:
            out += '|=======================\n'
            # out += 'Offset and Size use "bytes.bits" notation.\n'
        return out

    def to_c_typedef(self, *, indent='', tab='  '):
        if not self.legal_c_struct:
            # TODO: remove
            return f'// Skipping {self._type_name} as it cannot be accurately defined as C struct'

        out = ''
        packed = ''
        if self.packed:
            packed = '__attribute__ ((__packed__))'
        out += indent + 'typedef struct ' + packed + '{\n'
        var_size_cnt = 0
        for name in self._members:
            m = self._members[name]
            if 0 == var_size_cnt and not m.variable_size:
                out += indent + tab + m.to_c_var(name) + '\n'
            else:
                if 0 == var_size_cnt:
                    if self.legal_c_struct:
                        out += indent + tab + m.to_c_var(name) + '\n'
                    else:
                        # TODO: create blob member
                        pass
            if m.variable_size:
                var_size_cnt += 1
        out += indent + '} ' + self._type_name + ';'
        return out

    def to_c_var(self, name):
        return self._type_name + ' ' + name + ';'

    def gen_check_against_c(self, *, indent='', tab='  '):
        if self.is_primitive() or self.is_array():
            return ''  # no offsets to check
        if not self.legal_c_struct:
            return f'// Skipping {self._type_name} as it cannot be accurately defined as C struct'
        out = indent + '{\n'
        out += indent + tab + self.to_c_var('s') + '\n'
        out += indent + tab + f'printf("Checking {self._type_name}\\n");\n'
        for name in self._members:
            m = self._members[name]
            if not isinstance(m, BaseBitField):
                out += indent + tab + f'CHECK_MEMBER_OFFSET(s,{name},{self.offset(name)[0]});\n'
        out += indent + '}'
        return out

    def get_types(self) -> OrderedSet:
        out = OrderedSet([self._type_name])
        if self._members:
            for name in self._members:
                m = self.member(name)
                out.add(m._type_name)
                out = m.get_types() | out
        return out

    def get_classes(self) -> OrderedSet:
        out = OrderedSet([self.__class__])
        if self._members:
            for name in self._members:
                m = self.member(name)
                out.add(m.__class__)
                out = m.get_classes() | out
        return out

    def member(self, path: str):
        names = path.split('.')
        m = self
        for name in names:
            m = m._members[name]
        return m

    def size(self, *, full_bytes_only=False):
        # primitive type shall override this
        bit_size = self.bit_size()
        if isinstance(bit_size, int):
            size, extra_bits = divmod(bit_size, 8)
            if extra_bits > 0:
                if full_bytes_only:
                    return 0
                size += 1
        else:
            # if it is an expression, we assume it is a full byte value
            size = bit_size / 8
        return size

    def bit_size(self):
        # primitive type shall override this
        offsets_updated = self._offsets is None
        last_path = last(self.offsets)
        last_offset, last_bit_offset = self.offsets[last_path]
        bit_size = self.member(last_path).bit_size()
        if not offsets_updated:
            if (
                not isinstance(bit_size, int)
                or not isinstance(last_offset, int)
                or not isinstance(last_bit_offset, int)
            ):
                self._compute_offsets()
                last_offset, last_bit_offset = self.offsets[last_path]
                bit_size = self.member(last_path).bit_size()
        return last_offset * 8 + last_bit_offset + bit_size

    def size_str(self):
        size_bytes = self.size(full_bytes_only=True)
        if not isinstance(size_bytes, int) or size_bytes > 0:
            return f'{size_bytes} bytes'
        else:
            return f'{self.bit_size()} bits'

    def bit_granularity(self):
        # class with no member shall override this
        return last(self._members.items())[1].bit_granularity()

    def has_bit_granularity(self):
        size_bytes = self.size(full_bytes_only=True)
        if not isinstance(size_bytes, int) or size_bytes > 0:
            return False
        return True

    def has_resolved_size(self):
        return isinstance(self.bit_size(), int)

    def alignement(self):
        # class with no member shall override this
        return first(self._members.items())[1].alignement()

    @staticmethod
    def is_primitive():
        return False

    @staticmethod
    def is_array():
        return False

    def is_struct(self):
        return self._legal_c_struct

    def is_packet(self):
        return not self.is_array() and not self.is_primitive() and not self.is_struct()

    def is_initialized(self):
        try:
            self.to_bytes()
            return True
        except NotInitializedError:
            return False

    def to_bytes(self) -> bytes:
        if self._members is None:
            if self._value is None:
                raise NotInitializedError()
            return self._value.to_bytes(self.size(), byteorder='little')
        out = 0  # we use int because we can shift by bit amounts
        self.bit_size() # make sure we resolve the size
        for name in self._members.keys():
            m = self._members[name]
            offset, bit_offset = self.offset(name)
            try:
                val = int(m)
            except:  # noqa: E722
                raise NotInitializedError()  # noqa: B904
            out |= val << (offset * 8 + bit_offset)
        return out.to_bytes(self.size(), byteorder='little')

    def hexdump(self) -> str:
        return hexdump(self.to_bytes())

    def _check_or_fix_size(self, data: bytes, *, pad_if_smaller=False, trunc_if_larger=False):
        size = self.size()
        if not isinstance(size, int):
            # we cannot check or fix. go on and hope for the best!
            return data
        data_size = len(data)
        if data_size < size and pad_if_smaller:
            data = bytearray(data) + bytes(size - data_size)
        if data_size > size and trunc_if_larger:
            data = data[:size]
        if len(data) != size:
            raise RuntimeError(f'size mismatch: {len(data)} vs {size}')
        return data

    def from_bytes(self, data: bytes, *, pad_if_smaller=False, trunc_if_larger=False):
        data = self._check_or_fix_size(data, pad_if_smaller=pad_if_smaller, trunc_if_larger=trunc_if_larger)
        if self._members is None:
            self._value = int.from_bytes(data, byteorder='little')
        else:
            for name in self._members:
                m = self._members[name]
                offset, bit_offset = self.offsets[name]
                bit_size = m.bit_size()
                mask = (1 << bit_size) - 1
                size = ceildiv(bit_size, 8)
                dat = data[offset : offset + size]
                dat_int = int.from_bytes(dat, byteorder='little')
                dat_int = dat_int >> bit_offset
                dat_int &= mask
                dat = dat_int.to_bytes(size, byteorder='little')
                # self._members[name].from_bytes(dat)
                self.set_member_from_bytes(name, dat)

    def fill(self, byte_val):
        if byte_val > 0xFF:
            raise OverflowError()
        val = bytearray([int(byte_val)] * int(self.size()))
        self.from_bytes(val)

    def _to_int(other):
        try:
            o = int(other)
        except:
            o = int.from_bytes(other, byteorder='little')
        return o 
    
    def __eq__(self, other):
        o = XCType._to_int(other)
        bit_size = self.bit_size()
        if o.bit_length() > bit_size:
            return False
        return int(self) == o

    def __ne__(self, other):
        return not self.__eq__(other)

    def __int__(self):
        self_bytes = self.to_bytes()
        return int.from_bytes(self_bytes, byteorder='little')

    def __index__(self):
        return self.__int__()

    def __bool__(self):
        return 0 != int(self)

    def __lshift__(self, other):
        size = self.size()
        return self.__class__(init=(int(self) << XCType._to_int(other)).to_bytes(size, byteorder='little'))

    def __rshift__(self, other):
        size = self.size()
        return self.__class__(init=(int(self) >> XCType._to_int(other)).to_bytes(size, byteorder='little'))

    def __and__(self, other):
        size = self.size()
        return self.__class__(init=(int(self) & XCType._to_int(other)).to_bytes(size, byteorder='little'))

    def __xor__(self, other):
        size = self.size()
        return self.__class__(init=(int(self) ^ XCType._to_int(other)).to_bytes(size, byteorder='little'))

    def __or__(self, other):
        size = self.size()
        return self.__class__(init=(int(self) | XCType._to_int(other)).to_bytes(size, byteorder='little'))

    def __rlshift__(self, other):
        return other << self.__int__()

    def __rrshift__(self, other):
        return other >> self.__int__()

    def __rand__(self, other):
        return self.__and__(other)

    def __rxor__(self, other):
        return self.__xor__(other)

    def __ror__(self, other):
        return self.__or__(other)

    def __neg__(self):
        size = self.size()
        init = -int(self)
        signed = init < 0
        return self.__class__(init=init.to_bytes(size, byteorder='little', signed=signed))

    def __pos__(self):
        return NotImplemented

    def __abs__(self):
        size = self.size()
        return self.__class__(init=abs(int(self)).to_bytes(size, byteorder='little'))

    def __invert__(self):
        size = self.size()
        init = ~int(self)
        signed = init < 0
        return self.__class__(init=init.to_bytes(size, byteorder='little', signed=signed))


class BasePrimitive(XCType):
    @property
    def val(self):
        return self._value

    @val.setter
    def val(self, value):
        v = int(value)
        if v > self._mask:
            raise OverflowError()
        self._value = v & self._mask

    def __add__(self, other):
        return self.__class__(init=self._value + XCType._to_int(other))

    def __sub__(self, other):
        return self.__class__(init=self._value - XCType._to_int(other))

    def __mul__(self, other):
        return self.__class__(init=self._value * XCType._to_int(other))

    def __matmul__(self, other):
        return NotImplemented

    def __truediv__(self, other):
        return self.__class__(init=self._value / XCType._to_int(other))

    def __floordiv__(self, other):
        return self.__class__(init=self._value // XCType._to_int(other))

    def __mod__(self, other):
        return self.__class__(init=self._value % XCType._to_int(other))

    def __divmod__(self, other):
        return self.__class__(init=self.__floordiv__(other)), self.__class__(init=self.__mod__(other))

    def __pow__(self, other, modulus=None):
        if modulus is None:
            return self.__class__(init=pow(self._value, XCType._to_int(other)))
        else:
            return self.__class__(init=pow(self._value, XCType._to_int(other)) % XCType._to_int(modulus))

    def __lshift__(self, other):
        return self.__class__(init=self._value << XCType._to_int(other))

    def __rshift__(self, other):
        return self.__class__(init=self._value >> XCType._to_int(other))

    def __and__(self, other):
        return self.__class__(init=self._value & XCType._to_int(other))

    def __xor__(self, other):
        return self.__class__(init=self._value ^ XCType._to_int(other))

    def __or__(self, other):
        return self.__class__(init=self._value | XCType._to_int(other))

    def __radd__(self, other):
        return self.__class__(init=self._value + XCType._to_int(other))

    def __rsub__(self, other):
        return self.__class__(init=XCType._to_int(other) - self._value)

    def __rmul__(self, other):
        return self.__class__(init=self._value * XCType._to_int(other))

    def __rmatmul__(self, other):
        return NotImplemented

    def __rtruediv__(self, other):
        return self.__class__(init=XCType._to_int(other) / self._value)

    def __rfloordiv__(self, other):
        return self.__class__(init=XCType._to_int(other) // self._value)

    def __rmod__(self, other):
        return self.__class__(init=XCType._to_int(other) % self._value)

    def __rdivmod__(self, other):
        return self.__class__(init=self.__rfloordiv__(other)), self.__class__(init=self.__rmod__(other))

    def __rpow__(self, other, modulus=None):
        if modulus is None:
            return self.__class__(init=pow(XCType._to_int(other), self._value))
        else:
            return self.__class__(init=pow(XCType._to_int(other), self._value) % XCType._to_int(modulus))

    def __rlshift__(self, other):
        return self.__class__(init=XCType._to_int(other) << self._value)

    def __rrshift__(self, other):
        return self.__class__(init=XCType._to_int(other) >> self._value)

    def __rand__(self, other):
        return self.__class__(init=self._value & XCType._to_int(other))

    def __rxor__(self, other):
        return self.__class__(init=self._value ^ XCType._to_int(other))

    def __ror__(self, other):
        return self.__class__(init=self._value | XCType._to_int(other))

    def __neg__(self):
        return self.__class__(init=-self._value & self._mask)

    def __pos__(self):
        return NotImplemented

    def __abs__(self):
        return self.__class__(init=abs(self._value))

    def __invert__(self):
        return self.__class__(init=~self._value)

    def __int__(self):
        return self._value

    def __index__(self):
        return self._value

    def __lt__(self, other):
        return int(self) < XCType._to_int(other)

    def __le__(self, other):
        return int(self) <= XCType._to_int(other)

    def __gt__(self, other):
        return int(self) > XCType._to_int(other)

    def __ge__(self, other):
        return int(self) >= XCType._to_int(other)

    @property
    def variable_size(self):
        return False

    def __init__(self, init=None, size=None, name=None, mask=None, alignement=None):
        super().__init__()
        self._type_size = size
        if mask:
            self._mask = int(mask)
        else:
            self._mask = (1 << (size * 8)) - 1
        if alignement:
            self._alignement = alignement
        else:
            self._alignement = self._type_size
        self._type_name = name
        self._members = None
        self._legal_c_struct = False
        if init is not None:
            self.val = int(init) & self._mask

    def from_bytes(self, data: bytes, *, pad_if_smaller=False, trunc_if_larger=False):
        data = self._check_or_fix_size(data, pad_if_smaller=pad_if_smaller, trunc_if_larger=trunc_if_larger)
        self._value = int.from_bytes(data, byteorder='little') & self._mask

    def size(self, *, full_bytes_only=False):
        return self._type_size

    def bit_size(self):
        return self._type_size * 8

    def bit_granularity(self):
        return self._type_size * 8

    def alignement(self):
        return self._alignement

    @staticmethod
    def is_primitive():
        return True

    def to_c_typedef(self, *, indent='', tab='  '):
        return ''


class Bool(BasePrimitive):
    def __init__(self, init=None):
        super().__init__(init=init, size=1, name='bool', mask=1)


class BasePrimitiveSizeInBits(BasePrimitive):
    def size(self, *, full_bytes_only=False):
        if full_bytes_only and 0 != self._type_size % 8:
            # size is not multiple of 8
            return 0
        return ceildiv(self._type_size, 8)

    def bit_size(self):
        return self._type_size

    def bit_granularity(self):
        return self._type_size

    def to_bytes(self) -> bytes:
        if self._value is None:
            raise NotInitializedError()
        return self._value.to_bytes(ceildiv(self._type_size, 8), byteorder='little')


class BaseBitField(BasePrimitiveSizeInBits):
    def __init__(self, init=None, size=1, storage_bits=32):
        mask = (1 << size) - 1
        if storage_bits not in [8, 16, 32, 64]:
            raise RuntimeError(f"""uint{storage_bits}_t don't exist""")
        if size > storage_bits:
            raise RuntimeError(f"""{size} bits don't fit in uint{storage_bits}_t""")
        alignement = storage_bits // 8
        # name=f'bitfield{storage_bits}_{size}_t'
        name = f'uint{storage_bits}_t:{size}'
        super().__init__(init=init, size=size, name=name, mask=mask, alignement=alignement)
        self._storage_bits = storage_bits

    def to_c_var(self, name):
        return f'uint{self._storage_bits}_t {name}:{self.bit_size()};'

    def gen_check_against_c(self, *, indent='', tab='  '):
        return f'// Skipping bitfield {self._type_name}, C does not allow to take the address of a bitfield'


class BitField8(BaseBitField):
    def __init__(self, init=None, size=1):
        super().__init__(init=init, size=size, storage_bits=8)


class BitField16(BaseBitField):
    def __init__(self, init=None, size=1):
        super().__init__(init=init, size=size, storage_bits=16)


class BitField32(BaseBitField):
    def __init__(self, init=None, size=1):
        super().__init__(init=init, size=size, storage_bits=32)


class BitField64(BaseBitField):
    def __init__(self, init=None, size=1):
        super().__init__(init=init, size=size, storage_bits=64)


class U8(BasePrimitive):
    def __init__(self, init=None):
        super().__init__(init=init, size=1, name='uint8_t')


class U16(BasePrimitive):
    def __init__(self, init=None):
        super().__init__(init=init, size=2, name='uint16_t')


class U32(BasePrimitive):
    def __init__(self, init=None):
        super().__init__(init=init, size=4, name='uint32_t')


class U64(BasePrimitive):
    def __init__(self, init=None):
        super().__init__(init=init, size=8, name='uint64_t')


class U128(BasePrimitive):
    def __init__(self, init=None):
        super().__init__(init=init, size=16, name='uint128_t')


def todo():
    # the math functions are most likely wrong for signed types, so we don't support them yet
    class S8(BasePrimitive):
        def __init__(self, init=None):
            super().__init__(init=init, size=1, name='int8_t')

    class S16(BasePrimitive):
        def __init__(self, init=None):
            super().__init__(init=init, size=2, name='int16_t')

    class S32(BasePrimitive):
        def __init__(self, init=None):
            super().__init__(init=init, size=4, name='int32_t')

    class S64(BasePrimitive):
        def __init__(self, init=None):
            super().__init__(init=init, size=8, name='int64_t')

    class S128(BasePrimitive):
        def __init__(self, init=None):
            super().__init__(init=init, size=16, name='int128_t')


class BaseStruct(XCType):
    def __init__(self, init=None, *, packed=False, fill_byte: int | None = None):
        super().__init__(packed=packed)
        self._members = OrderedDict()
        self._context = {}
        self._do_init(init, fill_byte=fill_byte)


class Array(XCType):

    @property
    def variable_size(self):
        if self._variable_size is None:
            bit_size = self.bit_size()
            self._variable_size = isinstance(bit_size,int)
        return self._variable_size

    def __init__(self, init=None, elem_class=None, num_elem=None):
        super().__init__()
        self._type_name = f'{elem_class()._type_name}[]'
        self._legal_c_struct = False
        self._context = {}
        self._num_elem_int = None
        self._num_elem_sym = None
        if init is not None:
            self._do_init(init)
        else:
            self._elem_class = elem_class
            if isinstance(num_elem, int):
                self._num_elem_int = num_elem
                # self._value = [elem_class() for i in range(num_elem)]
                self._type_name = f'{elem_class()._type_name}[{self._num_elem_int}]'
                self._variable_size = False
            else:
                self._num_elem_sym = num_elem
                self._variable_size = True
            if elem_class is None:
                raise RuntimeError('elem_class is mandatory when init is None')

    @staticmethod
    def is_array():
        return True

    def elem_size(self, *, full_bytes_only=False):
        return self._elem_class().size(full_bytes_only=full_bytes_only)  # we support only element types with fixed size

    def elem_bit_size(self):
        return self._elem_class().bit_size()  # we support only element types with fixed size

    def set_num_elem(self, num_elem: int):
        self._num_elem_int = int(num_elem)
        self._offsets = None
        self._gaps = None
        if self._value is None:
            self._value = [self._elem_class() for i in range(num_elem)]
        else:
            n = len(self._value)
            self._value = self.value[0:num_elem]
            for i in range(n,num_elem):
                self._value[i] = self._elem_class()

    def size(self, *, full_bytes_only=False):
        num_elem = self._num_elem_int
        if (self._num_elem_int is not None) and (not isinstance(self._num_elem_int, int)):
            raise RuntimeError(f'self._num_elem_int is not None nor an int. type: {type(self._num_elem_int)}')
        if num_elem is None:
            num_elem = self._num_elem_sym
            try:
                num_elem = eval_expr(num_elem, self._context)
                self._num_elem_int = int(num_elem)
                self._type_name = f'{self._elem_class()._type_name}[{self._num_elem_int}]'
                # self._value = [elem_class() for i in range(num_elem)]
            except Exception as e:
                logging.debug(e)
        return num_elem * self.elem_size()

    def bit_size(self):
        return self.size() * 8

    def bit_granularity(self):
        return self.elem_bit_size()

    def alignement(self):
        # class with no member shall override this
        return self._elem_class().alignement()

    def to_bytes(self) -> bytes:
        out = bytearray()
        if self._value is None:
            raise NotInitializedError()
        for m in self._value:
            out += m.to_bytes()
        return bytes(out)

    def from_bytes(self, data: bytes, *, pad_if_smaller=False, trunc_if_larger=False):
        elem_size = self.elem_size(full_bytes_only=True)
        data = self._check_or_fix_size(data, pad_if_smaller=pad_if_smaller, trunc_if_larger=trunc_if_larger)
        data_bytes = BytesIO(data)

        self._value = [self._elem_class() for i in range(self._num_elem_int)]
        for e in self._value:
            e.from_bytes(data_bytes.read(elem_size))

    def to_str(self, *, deep=False, skip_long_data=False, indent=''):
        if self.is_initialized():
            out = indent + '{'
            sep = ''

            def process_elem(e):
                nonlocal out, sep
                out += f'{sep}{e.to_str(deep=deep,skip_long_data=skip_long_data,indent='')}'
                sep = ', '

            if skip_long_data and len(self._value) > 3:
                process_elem(self._value[0])
                out += ', ...'
                process_elem(self._value[-1])
            else:
                for e in self._value:
                    process_elem(e)
            out += '}'
        else:
            num_elem = self._num_elem_int
            if num_elem is None:
                num_elem = self._num_elem_sym
            out = indent + '{' + self._elem_class()._type_name + '}*' + f'{num_elem}'
        return out

    def _get_num_elem_str(self):
        self.size()  # force evaluation of self._num_elem_int
        num_elem = self._num_elem_int
        if num_elem is None:
            num_elem_str = ''
        else:
            num_elem_str = str(num_elem)
        return num_elem_str

    def to_c_var(self, name):
        if issubclass(self._elem_class,Array):
            parent=self
            dimensions = []
            dimensions.append(self._get_num_elem_str())
            while issubclass(parent._elem_class,Array):
                parent = self[0]
                dimensions.append(parent._get_num_elem_str())
            out = parent._elem_class()._type_name + ' ' + name
            for d in dimensions:
                out += '[' + d + ']'
            out += ';'
            return out
        return self._elem_class()._type_name + ' ' + name + '[' + self._get_num_elem_str() + '];'

    def to_c_typedef(self, *, indent='', tab='  '):
        return ''
        # return indent+f'typedef {self._elem_class()._type_name}[{self._get_num_elem_str()}] {self._type_name}\n'

    def get_types(self) -> OrderedSet:
        return {self._elem_class()._type_name}

    def get_classes(self) -> OrderedSet:
        return {self.__class__, self._elem_class}

    def set_all(self, val):
        self._value = [self._elem_class(init=val) for i in range(self._num_elem_int)]

    def __getitem__(self, index):
        if self._value is None:
            self.set_num_elem(self._num_elem_int)
        if 0 <= index < self._num_elem_int:
            return self._value[index]
        else:
            raise IndexError(index)

    def __setitem__(self, key, value):
        if self._value is None:
            self.set_num_elem(self._num_elem_int)
        self._value[key] = value

    def __iter__(self):
        if self._value is None:
            self.set_num_elem(self._num_elem_int)
        return self._value.__iter__()

    def __next__(self):
        if self._value is None:
            self.set_num_elem(self._num_elem_int)
        return self._value.__next__()

    def __len__(self):
        return self._num_elem_int


MUTABLES = MutableMapping, MutableSequence, MutableSet  # Mutable containers


def prop_name(name):
    return 'm_' + name.lower()


def storage_name(name):
    return '_member_' + prop_name(name)


def managed_attribute(name):
    """Return a property that stores values under a private non-public name."""

    @property
    def prop(self):
        return self._members[name.lower()]

    @prop.setter
    def prop(self, value):
        # self._members[name.lower()].val = value
        if isinstance(value, bytes) or isinstance(value, bytearray):
            self.set_member(name.lower(), value)
        else:
            self.set_member(name.lower(), value)

    return prop


def make_struct(classname, *, packed=False, **options):
    """Return a class with the specified attributes implemented as properties."""

    class Class(BaseStruct):
        def __init__(self, init=None, *, fill_byte: int | None = None):
            """Initialize instance attribute storage name values."""
            super().__init__(packed=packed)
            self._type_name = classname
            for key, value in options.items():
                # if isinstance(value, MUTABLES):  # Mutable?
                value = copy.deepcopy(value)  # Avoid mutable default arg.
                name = key.lower()
                self._members[name] = value
            self._do_init(init, fill_byte=fill_byte)

    for key in options.keys():  # Create class' properties.
        setattr(Class, prop_name(key), managed_attribute(key))

    Class.__name__ = classname
    return Class


def make_array(elem_cls, n_elem=None, classname=None):
    """Return a class with the specified attributes implemented as properties."""

    class Class(Array):
        def __init__(self, init=None, elem_class=elem_cls, num_elem=n_elem):
            """Initialize instance attribute storage name values."""
            super().__init__(elem_class=elem_class, num_elem=num_elem)
            # self._type_name = classname
            self._do_init(init)

    if classname:
        Class.__name__ = classname
    return Class


# class decorator like dataclass --> not ideal because use may want member names like 'size' that may collide with our member functions
# def xcstruct(cls):
#    datacls = dataclass(cls)
