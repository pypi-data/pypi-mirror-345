"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2025
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

import numpy as nmpy
from color_spec_changer.constant import (
    FORMAT_FROM_N_COMPONENTS,
    FUNCTION_FORMAT_PREFIX,
    FUNCTION_SPEC_COMPILED,
    HAS_OPACITY_FROM_N_COMPONENTS,
    HEX_LENGTHS_WITH_OPACITY,
    HEX_SOURCE_FORMAT_PREFIX,
    NAME_FORMAT,
    OPACITY_MARKER,
    SPEC_MAX_1,
    SPEC_MAX_255,
    SPECS_WITH_OPACITY,
)
from color_spec_changer.format_ import format_t

array_t = nmpy.ndarray


_COMPONENT_DETAILS_1 = (float, SPEC_MAX_1)
_COMPONENT_DETAILS_255 = (int, SPEC_MAX_255)


def CSCFormat(color: h.Any, /) -> format_t:
    """
    bool: Does the color include an opacity.
    type: Inner (color) type.
    type | None: Outer (container) type if several colors, or None.
    """
    if isinstance(color, str):
        if color[0] == "#":
            length = color.__len__()
            if length < 6:
                rgb_length = 3
            else:
                rgb_length = 6
            if length in HEX_LENGTHS_WITH_OPACITY:
                opacity = OPACITY_MARKER
                has_opacity = True
            else:
                opacity = ""
                has_opacity = False
            name = f"{HEX_SOURCE_FORMAT_PREFIX}{rgb_length}{opacity}"
            component_type, format_max = _COMPONENT_DETAILS_255
        elif (match := FUNCTION_SPEC_COMPILED.match(color)) is None:
            name = NAME_FORMAT
            has_opacity = False
            component_type = format_max = None
        else:
            if "." in color:
                component_type, format_max = _COMPONENT_DETAILS_1
            else:
                component_type, format_max = _COMPONENT_DETAILS_255
            match = match.group(0)[:-1]  # Remove opening parenthesis.
            name = f"{FUNCTION_FORMAT_PREFIX}{match}{format_max}"
            has_opacity = match in SPECS_WITH_OPACITY
        return format_t(
            name=name,
            has_opacity=has_opacity,
            component_type=component_type,
            max_component_value=format_max,
            inner_type=str,
        )

    if isinstance(color, int | float):
        if isinstance(color, int):
            component_type, format_max = _COMPONENT_DETAILS_255
        else:
            component_type, format_max = _COMPONENT_DETAILS_1
        return format_t(
            name=f"{FORMAT_FROM_N_COMPONENTS[1]}{format_max}",
            has_opacity=False,
            component_type=component_type,
            max_component_value=format_max,
            inner_type=type(color),
        )

    # Note: array_t's are not typing sequences, i.e., h.Sequence can be used in place of
    # tuple | list, also because str has been dealt with above. However, using
    # tuple | list anyway for explicitness.
    if isinstance(color, tuple | list):
        first_color = color[0]  # or first component of color if just one.

        if isinstance(first_color, str | tuple | list | array_t):
            format_ = CSCFormat(first_color)
            return format_t(
                name=format_.name,
                has_opacity=format_.has_opacity,
                component_type=format_.component_type,
                max_component_value=format_.max_component_value,
                inner_type=format_.inner_type,
                n_colors=color.__len__(),
                outer_type=type(color),
            )

        n_components = color.__len__()
        if isinstance(first_color, int):
            component_type, format_max = _COMPONENT_DETAILS_255
        else:
            component_type, format_max = _COMPONENT_DETAILS_1
        return format_t(
            name=f"{FORMAT_FROM_N_COMPONENTS[n_components]}{format_max}",
            has_opacity=HAS_OPACITY_FROM_N_COMPONENTS[n_components],
            component_type=component_type,
            max_component_value=format_max,
            inner_type=type(color),
        )

    if isinstance(color, array_t):
        if color.ndim == 1:
            n_components = color.size
            if nmpy.issubdtype(color.dtype, nmpy.integer):
                component_type, format_max = _COMPONENT_DETAILS_255
            else:
                component_type, format_max = _COMPONENT_DETAILS_1
            return format_t(
                name=f"{FORMAT_FROM_N_COMPONENTS[n_components]}{format_max}",
                has_opacity=HAS_OPACITY_FROM_N_COMPONENTS[n_components],
                component_type=component_type,
                max_component_value=format_max,
                inner_type=array_t,
            )

        assert color.ndim == 2, color.ndim

        format_ = CSCFormat(color[0, :])
        return format_t(
            name=format_.name,
            has_opacity=format_.has_opacity,
            component_type=format_.component_type,
            max_component_value=format_.max_component_value,
            inner_type=format_.inner_type,
            n_colors=color.shape[0],
            outer_type=array_t,
        )

    raise ValueError(f"Unknown color format {color}.")


def CSCFormatDescription(format_: format_t, /) -> str:
    """"""
    descriptions = (
        "Format",
        "With opacity",
        "Component type (None if component-less format)",
        "Max. component value (None if component-less format)",
        "Inner (color) type",
        "Number of colors",
        "Outer (container) type (None if single color)",
    )
    return "\n".join(f"{_dsc}: {_vle}" for _dsc, _vle in zip(descriptions, format_))


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
