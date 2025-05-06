"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2025
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

from color_spec_changer.constant import (
    FUNCTION_FORMAT_PREFIX,
    HEX_TARGET_FORMAT_PREFIX,
    NAME_FORMAT,
    SPEC_MAX_1,
    SPEC_MAX_255,
    TARGET_FORMATS_WITH_OPACITY,
)
from numpy import ndarray as array_t

true_sequences_h = type[tuple] | type[list] | type[array_t]  # True=not str.
inner_type_h = type[str] | type[int] | type[float] | true_sequences_h
outer_type_h = true_sequences_h | None


class format_t(h.NamedTuple):
    # Regarding the color itself.
    name: str
    has_opacity: bool
    component_type: type[int] | type[float] | None
    max_component_value: h.Literal["1", "255"] | None
    inner_type: inner_type_h
    # When several colors.
    n_colors: int = 1
    outer_type: outer_type_h = None

    @classmethod
    def NewFromTargetName(cls, name: str, /) -> h.Self:
        """
        The number of colors is not part of the format name, so assuming there is only
        one color.
        """
        has_opacity = name in TARGET_FORMATS_WITH_OPACITY
        if name == NAME_FORMAT:
            component_type = max_component_value = None
            inner_type = str
        elif (is_hex := name.startswith(HEX_TARGET_FORMAT_PREFIX)) or (
            SPEC_MAX_255 in name
        ):
            component_type, max_component_value = int, SPEC_MAX_255
            if is_hex or name.startswith(FUNCTION_FORMAT_PREFIX):
                inner_type = str
            else:
                inner_type = tuple  # "Arbitrary" true sequence type.
        else:
            component_type, max_component_value = int, SPEC_MAX_1
            if name.startswith(FUNCTION_FORMAT_PREFIX):
                inner_type = str
            else:
                inner_type = tuple  # "Arbitrary" true sequence type.

        return cls(
            name=name,
            has_opacity=has_opacity,
            component_type=component_type,
            max_component_value=max_component_value,
            inner_type=inner_type,
        )


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
