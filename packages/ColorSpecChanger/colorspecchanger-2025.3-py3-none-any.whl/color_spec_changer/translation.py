"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2025
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

import numpy as nmpy
from color_spec_changer.analysis import CSCFormat
from color_spec_changer.constant import (
    HEX_SOURCE_FORMAT_PREFIX,
    HEX_TARGET_FORMAT_PREFIX,
)
from color_spec_changer.format_ import format_t
from color_spec_changer.reference import ReferenceFromSource, TargetFromReference

array_t = nmpy.ndarray

target_outer_type_h = h.Literal["same"] | type[tuple] | type[list] | type[array_t]
target_inner_type_h = target_outer_type_h
index_or_reduction_h = (
    int | h.Literal["min", "mean", "median", "max"] | h.Callable | None
)

_TRUE_SEQUENCE_TYPES = (tuple, list, array_t)  # True=not str.


def TargetMatchesSource(target: str, source: str, /) -> bool:
    """"""
    if target == source:
        return True

    if (
        (target == HEX_TARGET_FORMAT_PREFIX)
        and (source == f"{HEX_SOURCE_FORMAT_PREFIX}6")
    ) or (
        (target == f"{HEX_TARGET_FORMAT_PREFIX}a")
        and (source == f"{HEX_SOURCE_FORMAT_PREFIX}6a")
    ):
        return True

    return False


def NewTranslatedColor(
    color: h.Any,
    target_format: str,
    /,
    *,
    target_outer_type: target_outer_type_h = "same",
    target_inner_type: target_inner_type_h = "same",
    index_or_reduction: index_or_reduction_h = None,
) -> h.Any | tuple[h.Any, int | float | tuple[int | float]]:
    """
    target_outer_type: Type of the container if several colors. "same"=same as input
    colors.
    target_inner_type: Type of the (individual) color(s). "same"=same as input color(s)
        except if target_format corresponds to an str-typed color specification, in
        which case target_inner_type is forced to str.

    If target_inner_type is str and target_outer_type is array_t, then target_outer_type
    is forced to tuple.

    If several colors and target_outer_type is array_t, then target_inner_type is forced
    to array_y.

    target_outer_type, index_or_reduction: Ignored if only one color.
    """
    format_ = CSCFormat(color)
    n_colors = format_.n_colors
    target_format = format_t.NewFromTargetName(target_format)

    if target_outer_type == "same":
        target_outer_type = format_.outer_type
    if target_inner_type == "same":
        target_inner_type = format_.inner_type

    if target_outer_type is array_t:
        target_inner_type = array_t

    if TargetMatchesSource(target_format.name, format_.name):
        out_color = color
        if target_format.has_opacity:  # So does format_/color.
            out_opacity = None
        else:
            default_opacity = format_.component_type(format_.max_component_value)
            if n_colors > 1:
                # Neither format has opacity.
                out_opacity = n_colors * (default_opacity,)
            else:
                # Neither format has opacity.
                out_opacity = default_opacity
    elif n_colors > 1:
        colors = color
        if isinstance(index_or_reduction, int):
            reference = ReferenceFromSource(colors[index_or_reduction])
            output = TargetFromReference(reference, target_format.name)
            if output[-1]:
                out_color, out_opacity = output[0], output[1]
            else:
                out_color, out_opacity = output[0], None
            n_colors = 1
        else:
            out_color, out_opacity = [], []

            for color in colors:
                reference = ReferenceFromSource(color)
                local = TargetFromReference(reference, target_format.name)
                out_color.append(local[0])
                if local[-1]:
                    out_opacity.append(local[1])

            if index_or_reduction is None:
                if out_opacity.__len__() == 0:
                    out_opacity = None
            else:
                if isinstance(index_or_reduction, str):
                    index_or_reduction = getattr(nmpy, index_or_reduction)
                    out_color = index_or_reduction(out_color, axis=0)
                else:
                    out_color = index_or_reduction(out_color)
                if out_opacity.__len__() > 0:
                    out_opacity = index_or_reduction(out_opacity)
                else:
                    out_opacity = None
                n_colors = 1
    else:
        reference = ReferenceFromSource(color)
        output = TargetFromReference(reference, target_format.name)
        if output[-1]:
            out_color, out_opacity = output[0], output[1]
        else:
            out_color, out_opacity = output[0], None

    if n_colors > 1:
        color_type = type(out_color[0])
        if (
            (not issubclass(color_type, target_inner_type))
            and (color_type in _TRUE_SEQUENCE_TYPES)
            and (target_inner_type in _TRUE_SEQUENCE_TYPES)
        ):
            if target_inner_type is array_t:
                target_inner_type = nmpy.array
            if target_outer_type is array_t:
                target_outer_type = nmpy.array
            out_color = target_outer_type(
                tuple(target_inner_type(_) for _ in out_color)
            )
        elif not issubclass(type(out_color), target_outer_type):
            if target_outer_type is array_t:
                target_outer_type = nmpy.array
            out_color = target_outer_type(out_color)
    else:
        color_type = type(out_color)
        if (
            (not issubclass(color_type, target_inner_type))
            and (color_type in _TRUE_SEQUENCE_TYPES)
            and (target_inner_type in _TRUE_SEQUENCE_TYPES)
        ):
            if target_inner_type is array_t:
                target_inner_type = nmpy.array
            out_color = target_inner_type(out_color)

    if out_opacity is None:
        return out_color

    if n_colors > 1:
        return out_color, tuple(out_opacity)

    return out_color, out_opacity


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
