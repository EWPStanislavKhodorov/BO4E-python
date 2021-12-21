"""
Contains Zeitreihenwert class
and corresponding marshmallow schema for de-/serialization
"""
from datetime import datetime

import attr
from marshmallow import fields, post_load

from bo4e.com.zeitreihenwertkompakt import Zeitreihenwertkompakt, ZeitreihenwertkompaktSchema

# pylint: disable=too-few-public-methods
from bo4e.validators import check_bis_is_later_than_von


@attr.s(auto_attribs=True, kw_only=True)
class Zeitreihenwert(Zeitreihenwertkompakt):
    """
    Abbildung eines Zeitreihenwertes bestehend aus Zeitraum, Wert und Statusinformationen.
    """

    # required attributes
    datum_uhrzeit_von: datetime = attr.ib(
        validator=[attr.validators.instance_of(datetime), check_bis_is_later_than_von]
    )  #: Datum Uhrzeit mit Auflösung Sekunden an dem das Messintervall begonnen wurde (inklusiv)
    datum_uhrzeit_bis: datetime = attr.ib(
        validator=[attr.validators.instance_of(datetime), check_bis_is_later_than_von]
    )  #: Datum Uhrzeit mit Auflösung Sekunden an dem das Messintervall endet (exklusiv)

    def get_inclusive_start(self) -> datetime:
        """
        return the inclusive start (used in the validator)
        """
        return self.datum_uhrzeit_von

    def get_exclusive_end(self) -> datetime:
        """return the exclusive end (used in the validator)"""
        return self.datum_uhrzeit_bis


class ZeitreihenwertSchema(ZeitreihenwertkompaktSchema):
    """
    Schema for de-/serialization of Zeitreihenwert.
    """

    # required attributes
    datum_uhrzeit_von = fields.DateTime()
    datum_uhrzeit_bis = fields.DateTime()

    # pylint: disable=no-self-use, unused-argument
    @post_load
    def deserialize(self, data, **kwargs) -> Zeitreihenwert:
        """Deserialize JSON to Zeitreihenwert object"""
        return Zeitreihenwert(**data)