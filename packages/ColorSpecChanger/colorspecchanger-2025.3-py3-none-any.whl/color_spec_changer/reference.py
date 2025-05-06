"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2025
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

from color_spec_changer.analysis import CSCFormat
from color_spec_changer.constant import (
    FORMAT_G_RGB_COMPILED_COMPONENT,
    FORMAT_G_RGB_COMPILED_FUNCTION,
    FUNCTION_FORMAT_PREFIX,
    FUNCTION_FORMAT_PREFIX_LENGTH,
    HEX_SOURCE_FORMAT_PREFIX,
    HEX_SOURCE_FORMAT_PREFIX_LENGTH,
    HEX_TARGET_FORMAT_PREFIX,
    NAME_FORMAT,
    OPACITY_MARKER,
    SPEC_G,
    SPEC_GA,
    SPEC_MAX_1,
    SPEC_RGB,
)


def ReferenceFromSource(color: h.Any, /) -> int | tuple[int, ...]:
    """
    color: Single color.
    """
    format_ = CSCFormat(color)

    if format_.name == NAME_FORMAT:
        # TODO: See
        #     https://github.com/ubernostrum/webcolors
        #     https://github.com/vaab/colour
        #     https://pypi.org/project/colour-science/
        raise NotImplementedError

    if format_.name.startswith(HEX_SOURCE_FORMAT_PREFIX):
        color = color.lower()
        # The 2 conditions could be handled with the same code with a component length
        # (1 or 2) and a factor (2 or 1). But is it worth it?
        if format_.name[HEX_SOURCE_FORMAT_PREFIX_LENGTH] == "3":
            red, green, blue = 2 * color[1], 2 * color[2], 2 * color[3]
            if format_.has_opacity:
                opacity = 2 * color[4]
            else:
                opacity = None
        else:  # format_.name[HEX_SOURCE_FORMAT_PREFIX_LENGTH] == "6"
            red, green, blue = color[1:3], color[3:5], color[5:7]
            if format_.has_opacity:
                opacity = color[7:9]
            else:
                opacity = None
        # The following could also be implemented with a loop/map-on-sequence. But is it
        # worth it?
        red = int(red, 16)
        green = int(green, 16)
        blue = int(blue, 16)
        if format_.has_opacity:
            opacity = int(opacity, 16)
            return red, green, blue, opacity
        return red, green, blue

    if format_.name.startswith(FUNCTION_FORMAT_PREFIX):
        match = FORMAT_G_RGB_COMPILED_FUNCTION.match(
            format_.name[FUNCTION_FORMAT_PREFIX_LENGTH:]
        )
        format_name, source_max = match.group(1), match.group(2)
        # +1/-1: For the opening/closing parenthesis; No need to strip the elements.
        output = color[(format_name.__len__() + 1) : -1].split(",")
        if source_max == SPEC_MAX_1:
            return tuple(map(lambda _: round(255.0 * float(_)), output))
        return tuple(map(int, output))

    match = FORMAT_G_RGB_COMPILED_COMPONENT.match(format_.name)
    format_name, source_max = match.group(1), match.group(2)
    if format_name == SPEC_G:
        if source_max == SPEC_MAX_1:
            return round(255.0 * color)
        return color

    if source_max == SPEC_MAX_1:
        return tuple(map(lambda _: round(255.0 * _), color))
    return tuple(color)


def TargetFromReference(
    color: int | tuple[int, ...], target_format: str, /
) -> tuple[h.Any, bool] | tuple[h.Any, int | float, bool]:
    """
    If target_format wants opacity, then only the converted color is returned, with a
    default full opacity if not present in color.
    If target_format does not want opacity, then the opacity is returned as a second term
    of type int | float. If color does not have an opacity, then the default value is
    1.0 or 255 depending on the target_format specification.

    Last returned value: Whether opacity is returned outside the color specification.
    """
    if isinstance(color, int):
        return TargetFromReference((color, color, color), target_format)

    n_components = color.__len__()

    if target_format == NAME_FORMAT:
        # TODO: See
        #     https://github.com/ubernostrum/webcolors
        #     https://github.com/vaab/colour
        #     https://pypi.org/project/colour-science/
        raise NotImplementedError

    if target_format.startswith(HEX_TARGET_FORMAT_PREFIX):
        if target_format[-1] == OPACITY_MARKER:
            if n_components == 2:  # ga.
                gray = f"{color[0]:02X}"
                return f"#{gray}{gray}{gray}{color[1]:02X}", False
            if n_components == 3:  # rgb.
                return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}FF", False
            # n_components == 4  # rgba.
            return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}{color[3]:02X}", False

        if n_components == 2:  # ga.
            gray = f"{color[0]:02X}"
            return f"#{gray}{gray}{gray}", color[1], True
        if n_components == 3:  # rgb.
            return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}", 255, True
        # n_components == 4  # rgba.
        return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}", color[3], True

    is_actually_gray = (n_components >= 3) and (color[0] == color[1] == color[2])
    if target_format[-1] == SPEC_MAX_1:
        color = tuple(map(lambda _: _ / 255.0, color))
        default_opacity = 1.0
        target_format = target_format[:-1]
    else:  # Ends with "255".
        default_opacity = 255
        target_format = target_format[:-3]

    if target_format.startswith(FUNCTION_FORMAT_PREFIX):
        target_format = target_format[FUNCTION_FORMAT_PREFIX_LENGTH:]
        output = _AlmostTargetAndOptionalOpacityFromTuple(
            color, n_components, is_actually_gray, target_format, default_opacity
        )
        if output[-1]:
            color, opacity = output[0], output[1]
        else:
            color, opacity = output[0], None
        color = f"{target_format}({', '.join(map(str, color))})"

        if opacity is None:
            return color, False
        return color, opacity, True

    return _AlmostTargetAndOptionalOpacityFromTuple(
        color, n_components, is_actually_gray, target_format, default_opacity
    )


def _AlmostTargetAndOptionalOpacityFromTuple(
    color: tuple[int | float, ...],
    n_components: int,
    is_actually_gray: bool,
    target_format: str,
    default_opacity: int | float,
    /,
) -> (
    tuple[int | float | tuple[int | float, ...], bool]
    | tuple[int | float | tuple[int | float, ...], int | float, bool]
):
    """"""
    if target_format in (SPEC_G, SPEC_GA):
        if n_components == 3:  # i.e. rgb.
            opacity = default_opacity
        else:  # n_components in (2, 4), i.e. ga or rgba.
            opacity = color[-1]

        if (n_components == 2) or is_actually_gray:
            gray = color[0]
        else:
            # See https://en.wikipedia.org/wiki/Grayscale.
            gray = (299 * color[0] + 587 * color[1] + 114 * color[2]) / 1000.0
            if isinstance(opacity, int):
                gray = round(gray)

        if target_format == SPEC_G:
            return gray, opacity, True
        return (gray, opacity), False

    if target_format == SPEC_RGB:
        if n_components == 2:
            gray = color[0]
            return (gray, gray, gray), color[1], True
        if n_components == 3:
            return color, default_opacity, True
        # n_components == 4.
        return color[:3], color[3], True

    # target_format == "rgba".
    if n_components == 2:
        gray = color[0]
        return (gray, gray, gray, color[1]), False
    if n_components == 3:
        return color + (default_opacity,), False
    # n_components == 4.
    return color, False


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
