from datetime import datetime
import re
import time
import lxml.etree as et
from dataclasses import dataclass
import io

import pandas as pd

@dataclass
class Regnskab:
    """
    """
    xlbr_response: io.BytesIO
    cvr: int
    start_date: str
    end_date: str
    translations: pd.DataFrame
    
    def __post_init__(self):
        self.__regnskab = et.parse(io.BytesIO(self.xlbr_response.content)).getroot()
        self.__namespaces: dict = self.__regnskab.nsmap
        self.__relevant_contexts = self.__extract_relevant_contexts
        self.__full_data = self.__load_full_data()
    
    def get_data_as_dict(self) -> dict:
        self.__result_dict = {
            "cvr": self.cvr,
            "start_date": self.__full_data["start_date"],
            "end_date": self.__full_data["end_date"]
            }
        self.__translations = self.__load_translations()
        for k in self.__translations.keys():
            result_var = self.__translations[k][0]
            self.__result_dict[k] = self.__full_data[result_var]
        self.__run_calculations()
        self.__run_validations()
        return self.__result_dict
   
    def __run_validations(self) -> None:
        """TODO: Funktion som validerer de beregnede værdier."""
        # Mimic beregningerne omkring bruttotest/bruttoresultat som ligger i linje 825+
        pass
    
    def __run_calculations(self) -> None:
        """Kører beregningslogik hvor tallene fra regnskabet ikke bare hentes én-til-én fra xlbr-data, men opkodes på den ene eller anden måde. 
        Oftest et spørgsmål om at centrale termer enten findes én-til-én eller opsplittet i regnskabsdata. 
        Overvej at splitte de enkelte beregninger ud i særskilte filer og dokumenter dem grundigt!"""
        self.__result_dict["afskrivninger"] = self.__afskrivninger
        self.__result_dict["vareBeholdning"] = self.__calculate_stat("varebeholdning_1", "vareBeholdning")
        self.__result_dict["anlaegsAktiver"] = self.__calculate_stat("anlaegsAktiver_1", "anlaegsAktiver")
        self.__result_dict["tilgodehavender"] = self.__calculate_stat("tilgodehavender_1", "tilgodehavender")
        self.__result_dict["personaleomkostninger"] = self.__calculate_stat("personaleOmkostninger_1", "personaleOmkostninger1")
        self.__result_dict["omsaetningsAktiver"] = self.__omsaetningsaktiver
        self.__result_dict["samletGaeld"] = self.__samlet_gaeld
        self.__result_dict["samletGaeld_test"] = self.__samlet_gaeld_test
        self.__result_dict["hensaettelser"] = self.__hensaettelser
        self.__result_dict["balance_test"] = self.__balance_test
        self.__result_dict["EBIT"] = self.__ebit
        self.__result_dict["ebitda_beregnet"] = self.__EBITDA
        self.__result_dict["brutto_tester"] = self.__brutto_test
        # self.__result_dict["ebit_test"] = self.__ebit_temp
        
    @property
    def __ebit(self) -> float:
        if "EBIT" in self.__result_dict:
            return self.__result_dict["EBIT"]
        return self.__ebit_temp

    @property
    def __EBITDA(self) -> float:
        if "EBITDA1" in self.__result_dict and self.__result_dict["EBITDA1"]:
            return self.__result_dict["EBITDA1"]
        if "EBIT" in self.__result_dict and self.__result_dict["EBIT"] and self.__result_dict['afskrivninger']:
            return self.__result_dict["EBIT"] + abs(self.__result_dict["afskrivninger"])
        return self.__result_dict["EBIT"]

    @property
    def __balance_test(self) -> float:
        hensaettelser = self.__result_dict["hensaettelser"] if self.__result_dict["hensaettelser"] else 0
        if "egenkapital" not in self.__result_dict:
            return None
        try:
            return sum([self.__samlet_gaeld_test, self.__result_dict["egenkapital"], hensaettelser])
        except TypeError:
            # print(self.cvr)
            return None

    @property
    def __hensaettelser(self) -> float:
        if "hensaettelser" in self.__result_dict:
            return self.__result_dict["hensaettelser"]
        if "hensaettelserSkat" in self.__result_dict:
            return self.__result_dict["hensaettelserSkat"]
        return None

    @property
    def __samlet_gaeld_status(self) -> bool:
        """
        Inkluderer lige nu ikke en grænse for hvor store afvigelser der accepteres.
        Hvis dette skal inkluderes, så kør noget i stil med abs(self.__samlet_gaeld-self.__samlet_gaeld_test) <= 2
        """
        return self.__samlet_gaeld == self.__samlet_gaeld_test

    @property
    def __samlet_gaeld(self) -> float:
        samlet_gaeld_vars = self.__indikator_variable("samletGaeld", recoded=True)
        if not samlet_gaeld_vars:
            try:
                return self.__result_dict["samletGaeld"]
            except KeyError:
                pass
        return sum([self.__result_dict[res] for res in samlet_gaeld_vars if res in self.__result_dict])

    @property
    def __samlet_gaeld_test(self) -> float:
        samlet_gaeld_test_vars = self.__indikator_variable("tjekGaeld", recoded=True)
        if not samlet_gaeld_test_vars:
            return None
        return sum([self.__result_dict[res] for res in samlet_gaeld_test_vars if res in self.__result_dict])

    @property
    def __ebit_temp(self) -> float:
        # EBITDA beregnes udelukkende hvis bruttoresultatet er angivet og bruttoresultat kan beregnes (__brutto_test) Ewwww
        if "bruttonResultat" not in self.__result_dict or not self.__result_dict["bruttoResultat"] or self.__result_dict["bruttoResultat"] != self.__brutto_test:
            return None
    
        resultatUdg_EBIT_beregning = ['afskrivninger_2', 'personaleomkostninger', 'distributionsOmkostninger', 'administrationsOmkostninger', 'andreDriftsOmkostninger']
    
        udgifter_foer_EBIT = sum([self.__result_dict[res] for res in resultatUdg_EBIT_beregning if res in self.__result_dict and self.__result_dict[res]])
        
        return self.__brutto_test - udgifter_foer_EBIT

    @property
    def __ebitda_unused(self) -> float:
        """Bruges ikke..."""

        self.__result_dict["EBIT"] = self.__ebit_temp if not self.__result_dict["EBIT"] else self.__result_dict["EBIT"]
        
        if not self.__result_dict["EBIT"]:
            return None
        
        if "afskrivninger_2" not in self.__result_dict:
            return self.__result_dict["EBIT"]
                
        return self.__result_dict["EBIT"] + self.__result_dict["afskrivninger_2"]

    @property
    def __brutto_test(self) -> float:
        """Mellemregning som tjekker hvorvidt bruttoResultat kan beregnes via andre parametre i regnskabet. Bruges så
        vidt vides til at afgøre om andre dele er fuld oplyst og dermed kan beregnes, ex. ebitda."""
        resultatInd = self.__indikator_variable("resultatInd", recoded=True)
        resultatUdg_1 = self.__indikator_variable("resultatUdg", recoded=True)
        # resultatUdg_2 = self.__indikator_variable("resultatUdg2", recoded=True)  # Udkommenteret indtil videre - synes ikke at blive anvendt.
        
        brutto_test = self.__result_dict["efterSkat"] if self.__result_dict["efterSkat"] else 0
        resultatInd_sum = sum([-self.__result_dict[res] for res in resultatInd if res in self.__result_dict])
        resultatUdg_sum = sum([self.__result_dict[res] for res in resultatUdg_1 if res in self.__result_dict and self.__result_dict[res]])
        
        return sum([brutto_test, resultatInd_sum, resultatUdg_sum])
    
    def __calculate_stat(self, stat: str, indikator: str) -> float:
        """Generel funktion, som på baggrund af et parameter returnerer enten parameteret, hvis dette findes én-til-én i regnskabet - alternativt en summeret indikator"""
        if stat in self.__result_dict:
            return self.__result_dict[stat]

        indikator_variable = self.__indikator_variable(indikator)
        
        if not indikator_variable:
            return None
            
        return sum([self.__full_data[self.__translations[var][0]] for var in indikator_variable if var in self.__full_data.keys()])
    
    @property
    def __omsaetningsaktiver(self) -> float:
        """Beregninger omsætningsaktiver. Returnerer xlbr stat hvis denne er angivet ellers forsøges den beregnet via to forskelligemodeller"""
        if "omsaetningsAktiver_1" in self.__result_dict:
            return self.__result_dict["omsaetningsAktiver_1"]
        
        omsakt_vars = ["vareBeholdning", "tilgodehavender", "likvider"]
        if all(k in self.__result_dict for k in omsakt_vars):
            return sum([self.__result_dict[var] for var in omsakt_vars if self.__result_dict[var] is not None])

        if all(k in self.__result_dict for k in ["aktiver", "anlaegsAktiver"]):
            omsaetningsaktiver1 = self.__result_dict["aktiver"] - 0 if not self.__result_dict["anlaegsAktiver"] else self.__result_dict["anlaegsAktiver"]
            rel_vars = ['varebeholdning', 'tilgodehavender', 'likvider', 'vaerdiPapirer']
            omsaetningsaktiver2 = sum([self.__result_dict[var] for var in rel_vars if var in self.__result_dict and self.__result_dict[var]])
            if abs(omsaetningsaktiver1-omsaetningsaktiver2) < 2:
                return omsaetningsaktiver2
            
        return None

    @property
    def __afskrivninger(self) -> float:
        """Funktion som beregner afskrivninger. Default return None - bør ikke nås. Tjek af dette indlejres i validations."""
        afskrivninger2 = self.__result_dict.get("afskrivninger_2", 0)
        
        if afskrivninger2 != 0:
            return afskrivninger2
        
        afskrivninger1 = self.__result_dict.get("afskrivninger_1", 0)
        tilbagefoerselAfAfskrivninger = self.__result_dict.get("tilbagefoerselAfAfskrivninger", 0)
        
        if afskrivninger1 != 0:
            return afskrivninger1 + tilbagefoerselAfAfskrivninger
            
        return None # Default state - denne bør ikke nås

    def __load_full_data(self) -> dict:
        """Danner en dict med samtlige resultater, som indeholdes i det downloadede xlbr regnskab"""
        full_results = {}
        full_results["cvr"] = self.cvr
        full_results["start_date"] = self.start_date
        full_results["end_date"] = self.end_date

        for elem in self.__relevant_tags:
            elem_name = re.sub(r"(\{.*\})", "", elem.tag)
            try:
                elem_value = float(elem.text)
            except TypeError:
                """Bypasser termer som er angivet i regnskabet, men uden angivelse"""
                continue
            except ValueError:
                elem_value = elem.text
            full_results[elem_name] = elem_value        
        
        return full_results
    
    def __indikator_variable(self, indikator: str, recoded: bool = False) -> float:
        return_column = "translated" if not recoded else "recoded_name"
        indikator_variable = self.__trans_df.loc[self.__trans_df[indikator] == 1, return_column].to_list()
        indikator_variable_renset = [var for var in indikator_variable if var in self.__result_dict]
        return list(set(indikator_variable_renset))
    
    def __load_translations(self) -> dict:
        self.__trans_df = self.translations
        trans_keys = self.__trans_df.translated.to_list()
        trans_values = self.__trans_df.key.to_list()
        full_data_keys = self.__full_data.keys()
       
        trans_dict = {}
        for k, v in zip(trans_keys, trans_values):
            if v not in full_data_keys:
                continue
            if k in trans_dict:
                trans_dict[k].append(v)
            else:
                trans_dict[k] = [v]   
        return trans_dict
   
    @property
    def __extract_relevant_contexts(self):
        """Funktion som udleder de relevate context id'er fra regnskabet og dermed hvilke parametre, som skal inkluderes.
        Lav løsning som laver et fallback på contextids, hvis der ikke er contexts uden "explitcitMember angivet. Se CVR øverst."""
        context_ids = []

        context_tags = [elem for elem in self.__regnskab.findall(r"{http://www.xbrl.org/2003/instance}context", self.__namespaces)]
        for context in context_tags:
            elem_names = [re.sub(r"(\{.*\})", "", elem.tag) for elem in context.iter()]
            if any(elem_name in ["explicitMember"] for elem_name in elem_names):
                    continue
            for elem in context.iter():
                if elem.text == self.end_date:
                    context_ids.append(context.get("id"))
                    continue
                if elem.text and elem.text.startswith(self.end_date[:4]):
                    # Denne håndtering er ikke umiddelbart ikke optimal. Er nødvendig da der i nogle tilfælde ikke kan testes på den fulde dato
                    # da afslutningsdatoen ikke fremgår af den enkelte context beskrivelse men datoen for godkendelse af regnskabet
                    # kan potentielt gøres mere robust ved at teste på startdatoen. 
                    context_ids.append(context.get("id"))
        # Nedenstående laver et fallback, hvis regnskabet ikke indeholder contexts, hvor "explicitMember" ikke er angivet. I EIFO scriptet håndteres dette
        # via koncern parameteret på get_regnskab() - hvis parameteret sættes til true, så anvendes explicitMember contexts. Nedenstående skal muligvis
        # udbygges så der angives en bit på det udtrukne regnskab ift. hvilken "model" for contexts, som er anvendt.
        # Er udbygget med et tjek af hvor der kun identificeres ét context id, hvorved listen udbygges. Dette er ikke en hensigtsmæssig håndtering!
        if not context_ids or len(list(set(context_ids))) < 2:
            context_tags = [elem for elem in self.__regnskab.findall(r"{http://www.xbrl.org/2003/instance}context", self.__namespaces)]
            for context in context_tags:
                elem_names = [re.sub(r"(\{.*\})", "", elem.tag) for elem in context.iter()]    
                for elem in context.iter():
                    if elem.text == self.end_date:
                        context_ids.append(context.get("id"))

        assert context_ids, f"Der blev ikke fundet context ids, hvilket er en fejl! CVR: {self.cvr}, slutdato: {self.end_date}"
        return context_ids
    
    @property
    def __relevant_tags(self):
        """Finder alle de tags i regnskabet med id'er fra de relevante contexter."""
        return [elem for elem in self.__regnskab.findall("{*}*", self.__namespaces) if elem.get("contextRef") in self.__relevant_contexts]