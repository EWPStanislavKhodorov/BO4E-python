import pytest
import json

from bo4e.bo.geschaeftspartner import Geschaeftspartner, GeschaeftspartnerSchema
from bo4e.com.adresse import Adresse
from bo4e.enum.anrede import Anrede
from bo4e.enum.botyp import BoTyp
from bo4e.enum.geschaeftspartnerrolle import Geschaeftspartnerrolle
from bo4e.enum.kontaktart import Kontaktart


class TestGeschaeftspartner:
    @pytest.mark.datafiles(
        "./tests/test_data/test_data_adresse/test_data_adresse_only_required_fields.json"
    )
    def test_serializable(self, datafiles):

        with open(
            datafiles / "test_data_adresse_only_required_fields.json", encoding="utf-8"
        ) as json_file:
            address_test_data = json.load(json_file)

        gp = Geschaeftspartner(
            anrede=Anrede.FRAU,
            name1="von Sinnen",
            name2="Helga",
            name3=None,
            gewerbekennzeichnung=True,
            hrnummer="HRB 254466",
            amtsgericht="Amtsgericht München",
            kontaktweg=Kontaktart.E_MAIL,
            umsatzsteuer_id="DE267311963",
            glaeubiger_id="DE98ZZZ09999999999",
            e_mail_adresse="test@bo4e.de",
            website="bo4e.de",
            geschaeftspartnerrolle=Geschaeftspartnerrolle.DIENSTLEISTER,
            partneradresse=Adresse(
                postleitzahl=address_test_data["postleitzahl"],
                ort=address_test_data["ort"],
                strasse=address_test_data["strasse"],
                hausnummer=address_test_data["hausnummer"],
            ),
        )

        # test default value for bo_typ in Geschaeftspartner
        assert gp.bo_typ == BoTyp.GESCHAEFTSPARTNER

        schema = GeschaeftspartnerSchema()

        gp_json = schema.dumps(gp, ensure_ascii=False)

        assert "Helga" in gp_json

        gp_deserialised = schema.loads(gp_json)

        assert gp_deserialised.bo_typ == gp.bo_typ
        assert type(gp_deserialised.partneradresse) == Adresse
