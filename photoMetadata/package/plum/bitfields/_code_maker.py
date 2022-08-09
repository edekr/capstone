# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2021 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""BitFields __init__ and property methods generator."""

from enum import EnumMeta
from typing import Any, Dict, Generator, Tuple, ValuesView

from .._code_injector import CodeInjector
from ..enum import EnumX
from ._bitfield import BitField

INDENT = "    "


class CodeMaker:

    """BitFields method code generator."""

    bitfields: Tuple[BitField, ...]

    def __init__(
        self,
        bitfields: ValuesView[BitField],
        code_injector: CodeInjector,
    ) -> None:
        self.bitfields = tuple(bitfields)

        type_names = [
            code_injector.get_expression(bitfield.typ, f"{bitfield.name}.typ")
            for bitfield in bitfields
        ]

        self.arg_type_hints = {}
        for bitfield, type_name in zip(bitfields, type_names):
            if bitfield.typ is int:
                self.arg_type_hints[bitfield.name] = "int"
            else:
                self.arg_type_hints[bitfield.name] = f"Union[int, {type_name}]"

        self.getter_type_hints = {}
        for bitfield, expression in zip(bitfields, type_names):
            if isinstance(bitfield.typ, EnumX) and not bitfield.typ.strict:
                expression = f"Union[int, {expression}]"
            self.getter_type_hints[bitfield.name] = expression

        self.type_expressions = {}
        for bitfield, expression in zip(bitfields, type_names):
            if "." in expression:
                expression = f"type(self).{expression}"

            self.type_expressions[bitfield.name] = expression

    def iter_init_lines(self, default: int) -> Generator[str, None, None]:
        """Generate __init__ method lines."""
        parameters = []

        for bitfield in self.bitfields:

            parameter = f"{bitfield.name}: {self.arg_type_hints[bitfield.name]}"

            if bitfield.default is not None:
                parameter += f" = {bitfield.default}"

            parameters.append(parameter)

        args = ", ".join(parameters)

        if args:
            yield f"def __init__(self, *, {args}) -> None:"
        else:
            yield "def __init__(self) -> None:"
        yield INDENT + f"self.__value__ = {default}"

        for bitfield in self.bitfields:
            yield INDENT + f"self.{bitfield.name} = {bitfield.name}"

        yield ""

    def iter_getter_lines(self, bitfield: BitField):
        """Generate getter."""
        yield f"@{bitfield.name}.getter"
        yield f"def {bitfield.name}(self) -> {self.getter_type_hints[bitfield.name]}:"
        if bitfield.doc:
            yield INDENT + f'"""{bitfield.doc}"""'

        if bitfield.lsb:
            retval = f"(int(self) >> {bitfield.lsb}) & {bitfield.mask}"
        else:
            retval = f"int(self) & {bitfield.mask}"

        if bitfield.signed:
            yield INDENT + f"value = {retval}"
            yield INDENT + f"value = -((1 << {bitfield.size}) - value) if {bitfield.signbit} & value else value"
            retval = "value"

        if hasattr(bitfield.typ, "__fields__"):
            yield INDENT + f"value = {self.type_expressions[bitfield.name]}.from_int({retval})"
            yield INDENT + "try:"
            yield INDENT + "    bitoffset, store = self.__bitoffset_store__"
            yield INDENT + "except AttributeError:"
            yield INDENT + f"    bitoffset, store = {bitfield.lsb}, self"
            if bitfield.lsb:
                yield INDENT + "else:"
                yield INDENT + f"    bitoffset += {bitfield.lsb}"
            yield INDENT + "value.__bitoffset_store__ = bitoffset, store"
            retval = "value"

        elif bitfield.typ is not int:
            retval = f"{self.type_expressions[bitfield.name]}({retval})"

        yield INDENT + f"return {retval}"
        yield ""

    def iter_setter_lines(self, bitfield: BitField, nested: bool):
        """Generate setter."""
        typ = bitfield.typ
        typ_name = self.type_expressions[bitfield.name]

        yield f"@{bitfield.name}.setter"
        yield f"def {bitfield.name}(self, value: {self.arg_type_hints[bitfield.name]}) -> None:"
        if bitfield.doc:
            yield INDENT + f'"""{bitfield.doc}"""'

        if hasattr(bitfield.typ, "__fields__"):
            yield INDENT + f"value = int({typ_name}.from_int(value))"
        elif bitfield.typ is int:
            yield INDENT + "value = int(value)"
        else:
            yield INDENT + f"value = int({typ_name}(value))"

        if (
            not hasattr(typ, "__fields__")
            and not isinstance(typ, EnumMeta)
            and typ is not bool
        ):
            yield INDENT + f"if not ({bitfield.minvalue} <= value <= {bitfield.maxvalue}):"
            yield INDENT + f'    raise ValueError("bit field {bitfield.name!r} requires {bitfield.minvalue} <= number <= {bitfield.maxvalue}")'

        if nested:
            yield INDENT + "try:"
            yield INDENT + "    bitoffset, store = self.__bitoffset_store__"
            yield INDENT + "except AttributeError:"
            yield INDENT + f"    bitoffset, store = {bitfield.lsb}, self"
            if bitfield.lsb:
                yield INDENT + "else:"
                yield INDENT + f"    bitoffset += {bitfield.lsb}"
            yield INDENT + f"store.__value__ = (store.__value__ & ~({bitfield.mask} << bitoffset)) | ((value & {bitfield.mask}) << bitoffset)"
        elif bitfield.lsb:
            yield INDENT + f"self.__value__ = (self.__value__ & {~(bitfield.mask << bitfield.lsb)}) | ((value & {bitfield.mask}) << {bitfield.lsb})"
        else:
            yield INDENT + f"self.__value__ = (self.__value__ & {~bitfield.mask}) | (value & {bitfield.mask})"
        yield ""

    def iter_repr_lines(self) -> Generator[str, None, None]:
        """Bitfields __repr__ method generator."""
        arg_reprs = ", ".join(f.argrepr for f in self.bitfields if f.argrepr)
        class_name = "{type(self).__name__}"

        yield "def __repr__(self) -> str:"
        yield "    try:"
        yield f'        return f"{class_name}({arg_reprs})"'
        yield "    except Exception:"
        yield f'        return f"{class_name}()"'
        yield ""

    def iter_lines(
        self, namespace: Dict[str, Any], default: int, nested: bool
    ) -> Generator[str, None, None]:
        """Generate BitFields class method code lines."""
        if "__init__" not in namespace:
            yield from self.iter_init_lines(default)

        for bitfield in self.bitfields:
            if bitfield.fget is None:
                yield from self.iter_getter_lines(bitfield)
            if bitfield.fset is None and not bitfield.readonly:
                yield from self.iter_setter_lines(bitfield, nested)

        if "__repr__" not in namespace:
            yield from self.iter_repr_lines()
