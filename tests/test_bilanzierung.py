from datetime import datetime, timezone
from typing import Any, Dict, Tuple

import pytest
from _decimal import Decimal
from pydantic import ValidationError

from bo4e.bo.bilanzierung import Bilanzierung
from bo4e.com.lastprofil import Lastprofil
from bo4e.com.menge import Menge
from bo4e.com.tagesparameter import Tagesparameter
from bo4e.enum.aggregationsverantwortung import Aggregationsverantwortung
from bo4e.enum.botyp import BoTyp
from bo4e.enum.fallgruppenzuordnung import Fallgruppenzuordnung
from bo4e.enum.mengeneinheit import Mengeneinheit
from bo4e.enum.profilart import Profilart
from bo4e.enum.profiltyp import Profiltyp
from bo4e.enum.profilverfahren import Profilverfahren
from bo4e.enum.prognosegrundlage import Prognosegrundlage
from bo4e.enum.wahlrechtprognosegrundlage import WahlrechtPrognosegrundlage
from bo4e.enum.zeitreihentyp import Zeitreihentyp
from tests.serialization_helper import assert_serialization_roundtrip

#:  full example
example_bilanzierung = Bilanzierung(
    marktlokations_id="51238696781",
    lastprofil=[
        Lastprofil(
            bezeichnung="foo",
            profilschar="foo2",
            verfahren=Profilverfahren.SYNTHETISCH,
            einspeisung=True,
            tagesparameter=Tagesparameter(
                klimazone="7624q",
                temperaturmessstelle="1234x",
                dienstanbieter="ZT1",
                herausgeber="BDEW",
            ),
            profilart=Profilart.ART_LASTPROFIL,
            herausgeber="BDEW",
        )
    ],
    bilanzierungsbeginn=datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    bilanzierungsende=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    bilanzkreis="foo",
    jahresverbrauchsprognose=Menge(wert=Decimal(3.41), einheit=Mengeneinheit.MWH),
    temperatur_arbeit=Menge(wert=Decimal(3.41), einheit=Mengeneinheit.MWH),
    # todo: check einheiten
    kundenwert=Menge(wert=Decimal(3.41), einheit=Mengeneinheit.MWH),
    verbrauchsaufteilung=1.5,
    zeitreihentyp=Zeitreihentyp.EGS,
    aggregationsverantwortung=Aggregationsverantwortung.VNB,
    prognosegrundlage=Prognosegrundlage.WERTE,
    details_prognosegrundlage=[Profiltyp.SLP_SEP],
    wahlrecht_prognosegrundlage=WahlrechtPrognosegrundlage.DURCH_LF,
    fallgruppenzuordnung=Fallgruppenzuordnung.GABI_RLMmT,
    prioritaet=1,
    grund_wahlrecht_prognosegrundlage=WahlrechtPrognosegrundlage.DURCH_LF_NICHT_GEGEBEN,
)


class TestBilanzierung:
    @pytest.mark.parametrize(
        "bilanzierung, expected_json_dict",
        [
            pytest.param(
                example_bilanzierung,
                {
                    # todo: cf. alias_generator=camelize in geschaeftsobjekte.py
                    "versionstruktur": "2",
                    "boTyp": BoTyp.BILANZIERUNG,
                    "externeReferenzen": [],
                    "marktlokationsId": "51238696781",
                    "lastprofil": [
                        {
                            "bezeichnung": "foo",
                            "profilschar": "foo2",
                            "verfahren": Profilverfahren.SYNTHETISCH,
                            "einspeisung": True,
                            "tagesparameter": {
                                "klimazone": "7624q",
                                "temperaturmessstelle": "1234x",
                                "dienstanbieter": "ZT1",
                                "herausgeber": "BDEW",
                            },
                            "profilart": Profilart.ART_LASTPROFIL,
                            "herausgeber": "BDEW",
                        }
                    ],
                    "bilanzierungsbeginn": datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                    "bilanzierungsende": datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                    "bilanzkreis": "foo",
                    "jahresverbrauchsprognose": {
                        "wert": 3.41,
                        "einheit": Mengeneinheit.MWH,
                    },
                    "temperaturArbeit": {
                        "wert": 3.41,
                        "einheit": Mengeneinheit.MWH,
                    },
                    "kundenwert": {
                        "wert": 3.41,
                        "einheit": Mengeneinheit.MWH,
                    },
                    "verbrauchsaufteilung": 1.5,
                    "zeitreihentyp": Zeitreihentyp.EGS,
                    "aggregationsverantwortung": Aggregationsverantwortung.VNB,
                    "prognosegrundlage": Prognosegrundlage.WERTE,
                    "detailsPrognosegrundlage": [Profiltyp.SLP_SEP],
                    "wahlrechtPrognosegrundlage": WahlrechtPrognosegrundlage.DURCH_LF,
                    "fallgruppenzuordnung": Fallgruppenzuordnung.GABI_RLMmT,
                    "prioritaet": 1,
                    "grundWahlrechtPrognosegrundlage": WahlrechtPrognosegrundlage.DURCH_LF_NICHT_GEGEBEN,
                },
                id="full example",
            ),
            pytest.param(
                Bilanzierung(),
                {
                    # todo: cf. alias_generator=camelize in geschaeftsobjekte.py
                    "versionstruktur": "2",
                    "boTyp": BoTyp.BILANZIERUNG,
                    "externeReferenzen": [],
                    "marktlokationsId": None,
                    "lastprofil": [],
                    "bilanzierungsbeginn": None,
                    "bilanzierungsende": None,
                    "bilanzkreis": None,
                    "jahresverbrauchsprognose": None,
                    "temperaturArbeit": None,
                    "kundenwert": None,
                    "verbrauchsaufteilung": None,
                    "zeitreihentyp": None,
                    "aggregationsverantwortung": None,
                    "prognosegrundlage": None,
                    "detailsPrognosegrundlage": [],
                    "wahlrechtPrognosegrundlage": None,
                    "fallgruppenzuordnung": None,
                    "prioritaet": None,
                    "grundWahlrechtPrognosegrundlage": None,
                },
                id="min example",
            ),
        ],
    )
    def test_serialization_roundtrip(self, bilanzierung: Bilanzierung, expected_json_dict: Dict[str, Any]) -> None:
        """
        Test de-/serialisation of Bilanzierung with minimal attributes.
        """
        assert_serialization_roundtrip(bilanzierung, expected_json_dict)

    @pytest.mark.parametrize(
        "malo_id_valid",
        [
            ("51238696781", True),
            ("41373559241", True),
            ("56789012345", True),
            ("52935155442", True),
            ("12345678910", False),  # Prüfsumme falsch
            ("529351554422", False),  # zu lang
            ("5293515544", False),  # zu kurz
            ("5293v15a442", False),  # Mix aus Zahlen und Buchstaben
            ("asdasd", False),
            ("   ", False),
            ("  asdasdasd ", False),
            (None, True),  # malo_id not required
            ("", False),
        ],
    )
    def test_id_validation(self, malo_id_valid: Tuple[str, bool]) -> None:
        """
        Test different MaLos.
        Field optional -> None values are allowed
        """

        def _instantiate_malo(malo_id: str) -> None:
            _ = Bilanzierung(
                marktlokations_id=malo_id,
            )

        if not malo_id_valid[1]:
            with pytest.raises(ValidationError):
                _instantiate_malo(malo_id_valid[0])
        else:
            _instantiate_malo(malo_id_valid[0])
