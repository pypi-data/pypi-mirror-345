from dataclasses import dataclass
from datetime import datetime
from .nace_map.nace_koder_map import nace_kode_map
from .nace_map.db25_til_db7 import konverter_db25_til_db7


@dataclass
class CVRResponse:
    """Klasse som håndteret et respons fra CVR

    OBS! Skal skrives om - alt for megen redundans omkring hvilke parametre som returneres.
    NB! Det antages at der tages udgangspunkt i det fulde response som input - altså uden selektering i output via query."""

    response: dict

    def __post_init__(self):
        if self.__invalid_input():
            raise TypeError("response er ikke en dict med det forventede format")
        self.__resp_type = self.__extract_resp_type()
        self.__meta_data = self.__extract_meta_data()

    def __invalid_input(self) -> bool:
        """Udestår"""
        return False

    def __extract_resp_type(self) -> str:
        """Udleder hvorvidt reponse er på cvr- eller p-nummer."""
        return "cvr" if self.response["_source"].get("Vrvirksomhed") else "pnr"

    def __extract_meta_data(self) -> dict:
        if self.__resp_type == "cvr":
            return self.response["_source"]["Vrvirksomhed"]["virksomhedMetadata"]
        else:
            return self.response["_source"]["VrproduktionsEnhed"][
                "produktionsEnhedMetadata"
            ]

    def get_data(self, all: bool = False, unit: str = "mdr") -> dict | list[dict]:
        self.__hoejvaekst_virk()
        if not all:
            return self.__get_latest()
        return self.__get_all(unit)

    def __get_latest(self) -> dict:
        results = self.__standard_info
        distinct_info = {
            "ant_ansatte": self.ant_ansatte,
            "ant_aarsvaerk": self.ant_aarsvaerk,
            "ant_ansatte_yyyymm": self.ant_ansatte_yyyymm,
        }
        full_results = results | distinct_info
        return full_results

    def __get_all(self, unit: str) -> list[dict]:
        results = []
        hist_results_ant_ans = self.__get_hist_data()
        if hist_results_ant_ans:
            for k in hist_results_ant_ans:
                temp_res = self.__standard_info
                distinct_info = {
                    "ant_ansatte": hist_results_ant_ans[k]["antalAnsatte"],
                    "ant_aarsvaerk": hist_results_ant_ans[k]["antalAarsvaerk"],
                    "ts_aar": hist_results_ant_ans[k]["aar"],
                    "ts_mdr": hist_results_ant_ans[k]["maaned"],
                }
                results.append(temp_res | distinct_info)
        else:
            temp_res = self.__standard_info
            results.append(temp_res)

        if unit == "mdr":
            return results
        reduced_result = self.__reduce_hist_results(results, unit)
        return reduced_result

    def __reduce_hist_results(self, complete_results: list[dict], unit: str) -> list[dict]:
        # Sikrer sortering
        ensure_sorted = sorted(complete_results, key=lambda k: (k["ts_aar"], k["ts_mdr"]), reverse=True)
        finale_res = []
        handled = []
        for k in ensure_sorted:
            if k["ts_aar"] not in handled:
                handled.append(k["ts_aar"])
                finale_res.append(k)
        return finale_res
    
    def __hoejvaekst_virk(self, year: int = None) -> int:
        """Funktion som koder hvorvidt virksomheden er en højvækst virksomhed eller ej. Definitionen følger DST's, som kan ses her: 
        https://www.dst.dk/da/Statistik/dokumentation/statistikdokumentation/hoejvaekstvirksomheder-i-danmark/indhold
        Ovenstående definerer "nye vækstvirksomheder" hvor vi kører med to - nye og eksisterende.        
        """
        # max_year: int = 2023  # Skal bare tage now() aar minus 1
        # year_list: list = [202312, 202212, 202112]
        # year_t_minus = [[year-(t*100) for t in range(0,4)] for year in year_list]
        
        # for case in year_t_minus
        pass
        

    def __get_hist_data(self) -> list[dict]:
        """Funktion som finder samtlige oplysninger om antal ansatte på tværs af måned, kvartal og årsregistreringer. Alle registreringer kodes på YYYY-MM, hvor
        tal opgjort på årsbasis placeres i måned 12, kvartal placeres i sidste måned i kvartalet.
        NB! Det er lidt forskelligt, hvad der er registreret på de forskellige typer. Antal ansatte var ex. ikke en del af kvartalstallene før 2014-07, hvorfor årstal
        prioriteres ved overlap - ex. 201312. 
        """
        hist_data = {}
        if self.__extract_mdr_data():
            mdr_data = self.__extract_mdr_data()
            hist_data = hist_data | mdr_data
        if self.__extract_aar_data():
            aar_data = self.__extract_aar_data()
            for aarmdr in aar_data:
                if int(aarmdr) not in hist_data.keys():
                    hist_data[aarmdr] = aar_data[aarmdr]
        if self.__extract_kvartal_data():
            kvartal_data = self.__extract_kvartal_data()
            for aarmdr in kvartal_data:
                if int(aarmdr) not in hist_data.keys():
                    hist_data[aarmdr] = kvartal_data[aarmdr]
        # Reducerer dict til kun at holde records og dermed ikke identifiers
        # hist_data_list = [hist_data[reg] for reg in hist_data]
        return hist_data
    
    def __extract_mdr_data(self) -> list[dict]:
        maaneddata_kodet = []
        try:
            maaneddata_kodet: list = (
                self.response["_source"]["Vrvirksomhed"]["maanedsbeskaeftigelse"]
                + self.response["_source"]["Vrvirksomhed"]["erstMaanedsbeskaeftigelse"]
            )
        except KeyError:
            maaneddata_kodet: list = self.response["_source"]["Vrvirksomhed"]["maanedsbeskaeftigelse"]
        # Opkoder data til en dict struktur
        data = {}
        if maaneddata_kodet:
            for mdr in maaneddata_kodet:
                data[int(mdr["aar"]*100+mdr["maaned"])] = {
                        "aar": mdr["aar"],
                        "maaned": mdr["maaned"],
                        "antalAarsvaerk": mdr["antalAarsvaerk"],
                        "antalAnsatte": mdr["antalAnsatte"],
                    }
        return data

    def __extract_aar_data(self) -> list[dict]:
        data = {}
        if "aarsbeskaeftigelse" in self.response["_source"]["Vrvirksomhed"]:
            for aar in self.response["_source"]["Vrvirksomhed"]["aarsbeskaeftigelse"]:
                data[(int(aar["aar"])*100)+12] = {
                        "aar": aar["aar"],
                        "maaned": 12,
                        "antalAarsvaerk": aar["antalAarsvaerk"],
                        "antalAnsatte": aar["antalAnsatte"],
                    }
        return data

    def __extract_kvartal_data(self) -> list[dict]:
        data = {}
        # Kvartalstal sammen kodes
        if "kvartalsbeskaeftigelse" in self.response["_source"]["Vrvirksomhed"]:
            for kvartal in self.response["_source"]["Vrvirksomhed"]["kvartalsbeskaeftigelse"]:
                data[int(kvartal["aar"]*100)+int(kvartal["kvartal"])*3] = {
                        "aar": kvartal["aar"],
                        "maaned": int(kvartal["kvartal"]) * 3,
                        "antalAarsvaerk": kvartal["antalAarsvaerk"],
                        "antalAnsatte": kvartal["antalAnsatte"],
                    }
        return data

    @property
    def __standard_info(self) -> dict:
        """
        Reference til de standard informationer fra CVR som bruges på tværs af forskellige funktioner.
        Lavet for at gøre det lettere at tilføje nye informationer, idet de dermed kun skal angives ét sted.
        """
        std_info = {
            "hit_type": self.__resp_type,
            "cvr": self.cvr,
            "cvr_str": str(self.cvr),
            "pnr": self.pnr,
            "name": self.name,
            "kommunekode": self.kommunekode,
            "stiftelsesdato": self.stiftelses_dato,
            "ophoersdato": self.ophoers_dato,
            "h_branche": self.hbranche,
            "h_branche_db07": self.hbranche_DB7,
            "h_branche_tekst": self.hbranche_tekst,
            "nace_grp10kode": self.nace_grp10kode,
            "nace_grp10afd": self.nace_grp10afd,
            "nace_grp19kode": self.nace_grp19kode,
            "nace_grp19afd": self.nace_grp19afd,
            "nace_grp36kode": self.nace_grp36kode,
            "nace_grp36afd": self.nace_grp36afd,
            "nace_grp127kode": self.nace_grp127kode,
            "nace_grp127afd": self.nace_grp127afd,
            "virkform_kode": self.virkform,
            "virkform": self.virkform_str,
            "status": self.status,
            "status_dato": self.status_dato,
            "aktiv": self.aktiv,
            "aktiv_2": self.aktiv_2,
            "sidst_opdateret": self.sidst_opdateret
        }
        return std_info

    @property
    def cvr(self) -> int:
        if self.__resp_type == "cvr":
            return self.response["_source"]["Vrvirksomhed"]["cvrNummer"]
        else:
            try:
                return self.response["_source"]["VrproduktionsEnhed"]["virksomhedsrelation"][0]["cvrNummer"]
            except IndexError:
                return None
            
    @property
    def pnr(self) -> int:
        if self.__resp_type == "cvr":
            return None
        else:
            return self.response["_source"]["VrproduktionsEnhed"]["pNummer"]

    @property
    def hbranche(self) -> int:
        if not self.__parameter_exists("nyesteHovedbranche", "branchekode"):
            return None
        return int(self.__meta_data["nyesteHovedbranche"]["branchekode"])

    @property
    def hbranche_DB7(self) -> int:
        """
        Konverterer DB25 koder, som ikke eksisterer i DB07 til DB07 koder
        Hele flowet omkring hovedbranche skal opdateres til at køre DB25, når den endelig opkodning foreligger
        https://www.dst.dk/da/Statistik/dokumentation/dansk-branchekode-opdateres
        """
        if self.hbranche not in nace_kode_map and self.hbranche not in konverter_db25_til_db7:
            branchekode = 999999
        else:
            branchekode = self.hbranche
        return konverter_db25_til_db7[branchekode] if branchekode not in nace_kode_map else branchekode

    @property
    def hbranche_tekst(self) -> int:
        if not self.__parameter_exists("nyesteHovedbranche", "branchetekst"):
            return None
        return self.__meta_data["nyesteHovedbranche"]["branchetekst"]
    
    @property
    def nace_grp10afd(self) -> str:
        return nace_kode_map[self.hbranche_DB7]["grp10hovedafdeling"]

    @property
    def nace_grp10kode(self) -> int:
        return int(nace_kode_map[self.hbranche_DB7]["grp10kode"])
    
    @property
    def nace_grp19afd(self) -> str:
        return nace_kode_map[self.hbranche_DB7]["grp19hovedafdeling"]

    @property
    def nace_grp19kode(self) -> str:
        return nace_kode_map[self.hbranche_DB7]["grp19kode"]
    
    @property
    def nace_grp36afd(self) -> str:
        return nace_kode_map[self.hbranche_DB7]["grp36hovedafdeling"]

    @property
    def nace_grp36kode(self) -> str:
        return nace_kode_map[self.hbranche_DB7]["grp36kode"]
    
    @property
    def nace_grp127afd(self) -> str:
        return nace_kode_map[self.hbranche_DB7]["grp127hovedafdeling"]

    @property
    def nace_grp127kode(self) -> int:
        return int(nace_kode_map[self.hbranche_DB7]["grp127kode"])

    @property
    def name(self) -> str:
        if not self.__parameter_exists("nyesteNavn", "navn"):
            return None
        return self.__meta_data["nyesteNavn"]["navn"]

    @property
    def status(self) -> str:
        if not self.__parameter_exists("sammensatStatus"):
            return None
        return self.__meta_data["sammensatStatus"]
    
    @property
    def status_dato(self) -> datetime.date:
        if not self.__parameter_exists("nyesteStatus", "periode", "gyldigFra"):
            return None
        status_dato = self.__meta_data["nyesteStatus"]["periode"]["gyldigFra"]
        return datetime.strptime(status_dato, "%Y-%m-%d").date() if status_dato else None

    @property
    def virkform_str(self) -> str:
        if not self.__parameter_exists("nyesteVirksomhedsform", "langBeskrivelse"):
            return None
        return self.__meta_data["nyesteVirksomhedsform"]["langBeskrivelse"]

    @property
    def virkform(self) -> int:
        if not self.__parameter_exists("nyesteVirksomhedsform", "virksomhedsformkode"):
            return None
        return self.__meta_data["nyesteVirksomhedsform"]["virksomhedsformkode"]

    @property
    def ant_ansatte(self) -> int:
        if not self.__parameter_exists("nyesteErstMaanedsbeskaeftigelse", "antalAnsatte"):
            return None
        return self.__meta_data["nyesteErstMaanedsbeskaeftigelse"]["antalAnsatte"]

    @property
    def ant_aarsvaerk(self) -> float:
        if not self.__parameter_exists("nyesteErstMaanedsbeskaeftigelse", "antalAarsvaerk"):
            return None
        return self.__meta_data["nyesteErstMaanedsbeskaeftigelse"]["antalAarsvaerk"]

    @property
    def ant_ansatte_yyyymm(self) -> int:
        if not self.__parameter_exists("nyesteErstMaanedsbeskaeftigelse", "aar"):
            return None
        if not self.__parameter_exists("nyesteErstMaanedsbeskaeftigelse", "maaned"):
            return None
        aar = self.__meta_data["nyesteErstMaanedsbeskaeftigelse"]["aar"]
        mdr = self.__meta_data["nyesteErstMaanedsbeskaeftigelse"]["maaned"]
        result = f"{(aar*100)+mdr:02d}"
        return int(result)

    @property
    def kommunekode(self) -> int:
        if not self.__parameter_exists("nyesteBeliggenhedsadresse", "kommune", "kommuneKode"):
            return None
        return int(self.__meta_data["nyesteBeliggenhedsadresse"]["kommune"]["kommuneKode"])

    @property
    def stiftelses_dato(self) -> str:
        if self.__resp_type == "cvr":
            stiftelsesdato = self.response["_source"]["Vrvirksomhed"]["livsforloeb"][0]["periode"]["gyldigFra"]
        else:
            stiftelsesdato = self.response["_source"]["VrproduktionsEnhed"]["livsforloeb"][0]["periode"]["gyldigFra"]
        return datetime.strptime(stiftelsesdato, "%Y-%m-%d").date() if stiftelsesdato else None

    @property
    def ophoers_dato(self) -> str:
        if self.__resp_type == "cvr":
            ophoersdato = self.response["_source"]["Vrvirksomhed"]["livsforloeb"][0]["periode"]["gyldigTil"]
        else:
            ophoersdato = self.response["_source"]["VrproduktionsEnhed"]["livsforloeb"][0]["periode"]["gyldigTil"]
        return datetime.strptime(ophoersdato, "%Y-%m-%d").date() if ophoersdato else None
    
    @property
    def sidst_opdateret(self) -> datetime.date:
        if self.__resp_type == "cvr":
            sidst_opdateret = self.response["_source"]["Vrvirksomhed"]["sidstOpdateret"][:10]
        else:
            sidst_opdateret = self.response["_source"]["VrproduktionsEnhed"]["sidstOpdateret"][:10]
        return datetime.strptime(sidst_opdateret, "%Y-%m-%d").date()

    @property
    def __kendte_statusudfald(self) -> dict:
        """Dict med de statuskoder, som på nuværende tidspunkt er kendte og kategoriseret i udfald på aktiv eller ej."""
        return {
            "aktiv": 1,
            "normal": 1,
            "ophørt": 0,
            "opløsteftererklæring": 0,
            "opløstefterfrivilliglikvidation": 0,
            "opløsteftergrænseoverskridendefusion": 0,
            "opløstefterfusion": 0,
            "opløstefterkonkurs": 0,
            "opløstefterspaltning": 0,
            "slettet": 0,
            "tvangsopløst": 0,
            "underfrivilliglikvidation": 0,
            "underkonkurs": 0,
            "underreassumering": 0,
            "underrekonstruktion": 0,
            "undertvangsopløsning": 0,
        }

    @property
    def aktiv(self) -> int:
        """
        Kodning af hvorvidt virksomheden er aktiv eller ej. Dette gøres på baggrund af virksomhedens status.
        Vi er i tvivl om, hvordan virksomheder som er opløste efter fusion skal betragtes. Derfor findes der et alternativ til denne
        kodning, hvor opløst efter fusion udelades fra populationen.
        """
        if self.status.lower() not in self.__kendte_statusudfald:
            print(f"Statusudfaldet: {self.status} er ikke kodet i aktiv/ikke aktiv. Skal opdateres, CVR: {self.cvr}")
        return int(self.__kendte_statusudfald[self.status.lower()])

    @property
    def aktiv_2(self) -> int:
        """Alternativ aktiv variabel som udelader opløstefterfusion fra populationen"""
        return None if self.status.lower() == "opløstefterfusion" else self.aktiv
    
    def __parameter_exists(self, *parameters) -> bool:
        """
        Hjælpe funktion til at tjekke om et parameter er i CVR response
        Parameters tager en eller flere strenge som input og returnerer True hvis parameteret er i self.__meta_data
        """
        _element = self.__meta_data
        for parameter in parameters:
            if _element is None or parameter not in _element:
                return False
            _element = _element[parameter]
        return _element is not None