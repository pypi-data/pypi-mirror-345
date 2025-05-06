"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2025
SEE COPYRIGHT NOTICE BELOW
"""

import re as r

# Color specifications.
# --- Components.
OPACITY_MARKER = "a"  # /!\\ Must be a single character.

SPEC_G = "g"
SPEC_GA = f"g{OPACITY_MARKER}"
SPEC_RGB = "rgb"
SPEC_RGBA = f"rgb{OPACITY_MARKER}"
SPEC_MAX_1 = "1"
SPEC_MAX_255 = "255"

# --- Specification.
SPECS_WITHOUT_OPACITY = (SPEC_G, SPEC_RGB)
SPECS_WITH_OPACITY = (SPEC_GA, SPEC_RGBA)
FUNCTION_SPEC_PATTERN = rf"^({SPEC_GA}|{SPEC_RGB}|{SPEC_RGBA})\("

# Format source names.
HEX_SOURCE_FORMAT_PREFIX = "hex_"
HEX_LENGTHS_WITH_OPACITY = (5, 9)

FORMAT_FROM_N_COMPONENTS = {1: SPEC_G, 2: SPEC_GA, 3: SPEC_RGB, 4: SPEC_RGBA}
HAS_OPACITY_FROM_N_COMPONENTS = {1: False, 2: True, 3: False, 4: True}
FORMAT_PATTERN_G_RGB_COMPONENT = (
    rf"^({SPEC_G}|{SPEC_GA}|{SPEC_RGB}|{SPEC_RGBA})({SPEC_MAX_1}|{SPEC_MAX_255})"
)

FORMAT_PATTERN_G_RGB_FUNCTION = (
    rf"^({SPEC_GA}|{SPEC_RGB}|{SPEC_RGBA})({SPEC_MAX_1}|{SPEC_MAX_255})"
)

# Format source and target names.
NAME_FORMAT = "name"
FUNCTION_FORMAT_PREFIX = "function_"

# Format target names.
HEX_TARGET_FORMAT_PREFIX = "hex"

# Lengths and compiled patterns.
HEX_SOURCE_FORMAT_PREFIX_LENGTH = HEX_SOURCE_FORMAT_PREFIX.__len__()
FUNCTION_FORMAT_PREFIX_LENGTH = FUNCTION_FORMAT_PREFIX.__len__()

FORMAT_G_RGB_COMPILED_COMPONENT = r.compile(FORMAT_PATTERN_G_RGB_COMPONENT)
FORMAT_G_RGB_COMPILED_FUNCTION = r.compile(FORMAT_PATTERN_G_RGB_FUNCTION)
FUNCTION_SPEC_COMPILED = r.compile(FUNCTION_SPEC_PATTERN, r.IGNORECASE)


# Catalogs (used for documentation).
def _AllSourceFormats() -> tuple[str, ...]:
    """"""
    output = [NAME_FORMAT]

    for length in (3, 6):
        for opacity in ("", OPACITY_MARKER):
            output.append(f"{HEX_SOURCE_FORMAT_PREFIX}{length}{opacity}")

    for prefix in ("", FUNCTION_FORMAT_PREFIX):
        should_exclude_gray = prefix == FUNCTION_FORMAT_PREFIX
        for spec in SPECS_WITHOUT_OPACITY + SPECS_WITH_OPACITY:
            if should_exclude_gray and (spec == SPEC_G):
                continue

            for max_ in (SPEC_MAX_1, SPEC_MAX_255):
                output.append(f"{prefix}{spec}{max_}")

    return tuple(output)


def _AllTargetFormatsWithOpacity() -> tuple[str, ...]:
    """"""
    output = [f"{HEX_TARGET_FORMAT_PREFIX}{OPACITY_MARKER}"]

    for prefix in ("", FUNCTION_FORMAT_PREFIX):
        for spec in SPECS_WITH_OPACITY:
            for max_ in (SPEC_MAX_1, SPEC_MAX_255):
                output.append(f"{prefix}{spec}{max_}")

    return tuple(output)


def _AllTargetFormats(with_opacity: tuple[str, ...], /) -> tuple[str, ...]:
    """"""
    output = [NAME_FORMAT, HEX_TARGET_FORMAT_PREFIX]

    for prefix in ("", FUNCTION_FORMAT_PREFIX):
        should_exclude_gray = prefix == FUNCTION_FORMAT_PREFIX
        for spec in SPECS_WITHOUT_OPACITY:
            if should_exclude_gray and (spec == SPEC_G):
                continue

            for max_ in (SPEC_MAX_1, SPEC_MAX_255):
                output.append(f"{prefix}{spec}{max_}")

    return tuple(output) + with_opacity


SOURCE_FORMATS = _AllSourceFormats()
TARGET_FORMATS_WITH_OPACITY = _AllTargetFormatsWithOpacity()
TARGET_FORMATS = _AllTargetFormats(TARGET_FORMATS_WITH_OPACITY)

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
