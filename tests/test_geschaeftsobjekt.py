import pytest

from bo4e.bo.geschaeftsobjekt import Geschaeftsobjekt, GeschaeftsobjektSchema
from bo4e.enum.botyp import BoTyp
from bo4e.com.externereferenz import ExterneReferenz


class TestGeschaeftsobjet:
    @pytest.mark.parametrize(
        "bo_typ, versionstruktur, externe_referenzen",
        [
            (
                BoTyp.ENERGIEMENGE,
                2,
                [
                    ExterneReferenz(
                        ex_ref_name="HOCHFREQUENZ_HFSAP_100", ex_ref_wert="12345"
                    ),
                    ExterneReferenz(
                        ex_ref_name="Schufa-ID", ex_ref_wert="aksdlakoeuhn"
                    ),
                ],
            ),
            (
                BoTyp.ENERGIEMENGE,
                2,
                [
                    ExterneReferenz(
                        ex_ref_name="HOCHFREQUENZ_HFSAP_100", ex_ref_wert="12345"
                    )
                ],
            ),
            (BoTyp.ENERGIEMENGE, 2, []),
        ],
    )
    def test_serialisation(
        self, bo_typ: BoTyp, versionstruktur: int, externe_referenzen: ExterneReferenz
    ):
        go = Geschaeftsobjekt(
            bo_typ=bo_typ,
            versionstruktur=versionstruktur,
            externe_referenzen=externe_referenzen,
        )
        assert isinstance(go, Geschaeftsobjekt)

        schema = GeschaeftsobjektSchema()

        go_json = schema.dumps(go, ensure_ascii=False)

        assert str(versionstruktur) in go_json

        go_deserialised = schema.loads(go_json)

        assert go_deserialised.bo_typ is bo_typ
        assert go_deserialised.versionstruktur == versionstruktur
        assert go_deserialised.externe_referenzen == externe_referenzen

    def test_initialization_with_minimal_attributs(self):
        go = Geschaeftsobjekt(bo_typ=BoTyp.ANSPRECHPARTNER)

        assert go.externe_referenzen == []
        assert go.versionstruktur == "2"

    def test_no_list_in_externen_referenzen(self):
        with pytest.raises(TypeError) as excinfo:
            _ = Geschaeftsobjekt(
                bo_typ=BoTyp.ENERGIEMENGE,
                externe_referenzen=ExterneReferenz(
                    ex_ref_name="Schufa-ID", ex_ref_wert="aksdlakoeuhn"
                ),
            )
        assert "must be typing.List" in str(excinfo.value)
