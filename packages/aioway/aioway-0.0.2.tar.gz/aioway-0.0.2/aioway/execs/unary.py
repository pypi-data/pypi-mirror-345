# Copyright (c) RenChu Wang - All Rights Reserved

import abc
import dataclasses as dcls
import typing
from abc import ABC
from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray
from sympy import Expr

from aioway.attrs import AttrSet
from aioway.blocks import Block
from aioway.errors import AiowayError

from .execs import Exec

__all__ = ["UnaryExec", "FilterPredExec", "FilterExprExec", "RenameExec", "ProjectExec"]


@dcls.dataclass
class UnaryExec(Exec, ABC):
    """
    ``UnaryExec`` is a base class for all unary operations.
    """

    exe: Exec
    """
    The input ``Exec`` of the current ``Exec``.
    """

    @typing.override
    @abc.abstractmethod
    def __next__(self) -> Block: ...

    @property
    @typing.override
    @abc.abstractmethod
    def attrs(self) -> AttrSet: ...

    @property
    @typing.override
    def children(self) -> tuple[Exec]:
        return (self.exe,)


@typing.final
@dcls.dataclass
class FilterPredExec(UnaryExec, key="FILTER_PRED"):
    predicate: Callable[[Block], NDArray]
    """
    The batched prediction of which rows to keep for the inputs.
    """

    @typing.override
    def __next__(self) -> Block:
        item = next(self.exe)
        pred = self.predicate(item)

        # Just to be extra fault tolerant.
        pred = np.array(pred)

        # Convert to int indices.
        if np.isdtype(pred.dtype, "bool"):
            if len(item) != len(pred):
                raise FilterBatchSizeError(
                    f"The output length of {self.predicate=} does not match the input, "
                    "even though a boolean array is returned."
                )
            pred = np.arange(len(item))[pred]

        # Must be integer array for indices.
        if not np.isdtype(pred.dtype, "integral"):
            raise FitlerPredicateDTypeError(
                f"Output of {self.predicate=} should be an integer array."
            )

        return item[pred]

    @property
    @typing.override
    def attrs(self) -> AttrSet:
        return self.exe.attrs


@typing.final
@dcls.dataclass
class FilterExprExec(UnaryExec, key="FILTER_EXPR"):
    expr: str | Expr
    """
    The expression of the frame.
    """

    @typing.override
    def __next__(self) -> Block:
        item = next(self.exe)
        return item.filter(self.expr)

    @property
    @typing.override
    def attrs(self) -> AttrSet:
        return self.exe.attrs


@typing.final
@dcls.dataclass
class ProjectExec(UnaryExec, key="PROJECT"):
    """
    Select a subset of the columns.
    """

    subset: list[str] | None = None
    """
    The subset to use. If not give, the ``ProjectStream`` would be a null operation.
    """

    def __post_init__(self) -> None:
        subs = self.subset

        if subs is None:
            return

        if not isinstance(subs, list) and all(isinstance(c, str) for c in subs):
            raise ProjectColumnTypeError("Column must be a list of strings.")

    @typing.override
    def __next__(self) -> Block:
        item = next(self.exe)
        return item if self.subset is None else item[self.subset]

    @property
    @typing.override
    def attrs(self) -> AttrSet:
        schema = self.exe.attrs

        if self.subset is None:
            return schema

        return schema.project(*self.subset)


@typing.final
@dcls.dataclass(init=False)
class RenameExec(UnaryExec, key="RENAME"):
    """
    Rename a couple of columns.
    """

    renames: dict[str, str] = dcls.field(default_factory=dict)
    """
    The mapping dictionary names.
    """

    def __init__(self, __exe: Exec, /, **renames: str) -> None:
        # This constructor is provideds.t. `RenameStream`'s renames can be specified as **kwargs,
        # which means they will be variable names, consistent with what `TensorDict` provides.
        #
        # Even though I'm using a Python version with positional only argument,
        # since ``Exec`` is common, using ``__exe`` to avoid name collision (in keys).
        self.exe = __exe
        self.renames = renames

    @typing.override
    def __next__(self) -> Block:
        item = next(self.exe)
        return item.rename(**self.renames)

    @property
    @typing.override
    def attrs(self) -> AttrSet:
        return self.exe.attrs.rename(**self.renames)


class FilterBatchSizeError(AiowayError, ValueError): ...


class FitlerPredicateDTypeError(AiowayError, ValueError): ...


class ProjectColumnTypeError(AiowayError, TypeError): ...
