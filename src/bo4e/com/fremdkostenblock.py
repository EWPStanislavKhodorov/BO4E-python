"""
Contains Fremdkostenblock class
"""

from typing import TYPE_CHECKING, Annotated, Literal, Optional

from pydantic import Field

from ..enum.comtyp import ComTyp
from ..utils import postprocess_docstring
from .com import COM

if TYPE_CHECKING:

    from .betrag import Betrag
    from .fremdkostenposition import Fremdkostenposition

# pylint: disable=too-few-public-methods


@postprocess_docstring
class Fremdkostenblock(COM):
    """
    Komponente zur Abbildung eines Kostenblocks in den Fremdkosten

    .. raw:: html

        <object data="../_static/images/bo4e/com/Fremdkostenblock.svg" type="image/svg+xml"></object>

    .. HINT::
        `Fremdkostenblock JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/{__gh_version__}/src/bo4e_schemas/com/Fremdkostenblock.json>`_

    """

    typ: Annotated[Literal[ComTyp.FREMDKOSTENBLOCK], Field(alias="_typ")] = ComTyp.FREMDKOSTENBLOCK

    kostenblockbezeichnung: Optional[str] = None
    """Bezeichnung für einen Kostenblock. Z.B. Netzkosten, Messkosten, Umlagen, etc."""

    kostenpositionen: Optional[list["Fremdkostenposition"]] = None
    """
    Hier sind die Details zu einer Kostenposition aufgeführt. Z.B.:
    Alliander Netz Heinsberg GmbH, 2018-02-01, 2019-01-01, Arbeitspreis HT, 3.660 kWh,
    5,8200 ct/kWh, 213,01 €
    """

    summe_kostenblock: Optional["Betrag"] = None
    """Die Summe aller Kostenpositionen dieses Blocks"""
    # todo: write validator fo this sum, see https://github.com/Hochfrequenz/BO4E-python/issues/324
