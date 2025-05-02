from dataclasses import dataclass


@dataclass
class CVROwner:
    response: dict
    cvr: int
    
    def __post_init__(self):
        self.__har_reelle_ejere = self.__extract_har_reelle_ejere()
    
    def get_data(self) -> dict | list[dict]:
        """Funktion som henter reelle ejere for et givent cvr response"""
        if not self.__deltager_relationer:
            return {
                    "cvr" : self.cvr,
                    "api_status": "Ingen deltager relationer angivet",
            }
        result_list = []
        for person in self.__personer:
            result = self.__extract_personal_info(person)
            result_list.append(result)
        return result_list
            
    def __extract_personal_info(self, p_dict: dict) -> dict:
        temp_result = {
            "cvr": self.cvr,
            "api_status":  "Deltager relationer fundet",
            "navn": p_dict["deltager"]["navne"][0]["navn"],
            "enhedsnummer": int(p_dict["deltager"]["enhedsNummer"]),
        }
        org_info = self.__extract_org_info(p_dict["organisationer"])
        return temp_result | org_info
        
    def __extract_org_info(self, org_dict: dict) -> dict:
        roller = []
        gyldig_til_datoer = []
        for org in org_dict:
            medlemsdata = org["medlemsData"][0]["attributter"]
            for v in medlemsdata:
                roller.extend(rolle["vaerdi"].lower() for rolle in v["vaerdier"] if not rolle["periode"]["gyldigTil"])
                gyldig_til_datoer.extend([m["periode"]["gyldigTil"] for m in v["vaerdier"]])
        reel_ejer = 0
        for rolle in roller:
            if "reel ejer" in rolle:
                reel_ejer = 1
            if not self.__har_reelle_ejere:
                if rolle in ["adm. dir.", "bestyrelsesmedlem", "formand", "næstformand"]:
                    reel_ejer = 2
        aktiv = 1 if not all(gyldig_til_datoer) else 0
        return {
            "reel_ejer": reel_ejer,
            "aktiv": aktiv,
            "roller": roller
        }

    @property
    def __virksomheder(self) -> list[dict]:
        return [p for p in self.__deltager_relationer if p["deltager"]["enhedstype"]=="VIRKSOMHED"]

    @property
    def __personer(self) -> list[dict]:
        return [p for p in self.__deltager_relationer if p["deltager"]["enhedstype"]!="VIRKSOMHED" if p["deltager"]]
    
    @property
    def __deltager_relationer(self) -> list[dict]:
        return [deltager for deltager in self.response["_source"]["Vrvirksomhed"]["deltagerRelation"] if deltager["deltager"]]
    
    def __extract_har_reelle_ejere(self) -> bool:
        """Grimt"""
        for delt in self.response["_source"]["Vrvirksomhed"]["deltagerRelation"]:
            for org in delt["organisationer"]:
                if org["organisationsNavn"][0]["navn"] == "Reelle ejere":
                    return False if not org["medlemsData"] else True