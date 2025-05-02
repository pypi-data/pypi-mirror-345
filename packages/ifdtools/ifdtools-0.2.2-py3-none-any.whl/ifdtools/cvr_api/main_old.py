import json
import pandas as pd
import requests
import keyring
from requests.auth import HTTPBasicAuth
from operator import itemgetter
from dataclasses import dataclass
from Levenshtein import ratio
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
# Egne klasser
from .cvr_response_class import CVRResponse
from .cvr_regnskab_class import Regnskab
from .cvrapi_functions.name_handler import run_name_handler

@dataclass
class CVRAPI:
    """Super rodet!"""
    
    def __post_init__(self):
        self._url = self._url_virk
        self.__test_setup()
        
    def __test_setup(self):
        self.__creds = keyring.get_credential("cvr_api", None)
        if self.__creds is None:
            raise ValueError("Du skal tilføje brugernavn og password til windows credentials kaldet cvr_api.")
        test_query = {"query": {"bool": {"must": [{"term": {"Vrvirksomhed.cvrNummer": "29035695"}}]}}}
        response = self._response(test_query)
        response.raise_for_status()
        print("Forbindelse til CVR etableret korrekt!")
        
    @property
    def _headers(self) -> dict:
        return {"content-type": "application/json", "cache-control": "no-cache"}
    
    @property
    def _url(self) -> str:
        return self._internal_url
    
    @_url.setter
    def _url(self, url: str):
        self._internal_url = url
    
    @property
    def _url_virk(self) -> str:
        return r"http://distribution.virk.dk/cvr-permanent/virksomhed/_search"

    @property
    def _url_penh(self) -> str:
        return r"http://distribution.virk.dk/cvr-permanent/produktionsenhed/_search"
    
    @property
    def _url_regnskab(self) -> str:
        return r"http://distribution.virk.dk/offentliggoerelser/_search"
    
    def __create_query(self) -> dict:
        query = { "query": { "match": {} } }
        query["query"]["match"] = { self.query_field: {"query": self.query_term, "operator": self.query_operator} }
        query["size"] = self.mqr
        return query

    def _response(self, payload: dict) -> requests.Response:
        resp = requests.request(
            method="POST",
            url=self._url,
            data=json.dumps(payload),
            headers=self._headers,
            auth=HTTPBasicAuth(self.__creds.username, self.__creds.password)
        )
        resp.raise_for_status()
        return resp
    
    def __parse_query(self, query: dict) -> json:
        response = self._response(query)
        return json.loads(response.content)
    
    def test_query(self, query: dict, url_virk: bool = True) -> json:
        """Funktion som anvendes til at teste nye queries inden indlejring i klassen"""
        self._url = self._url_virk if url_virk else self._url_penh
        response = self._response(query)
        json_cont = json.loads(response.content)
        print(json_cont)
        return self.__parse_responses(json_cont)
    
    def __parse_responses(self, json_cont: json) -> list:
        results = []
        if json_cont["hits"]["total"] == 0:
            return results
        for hit in json_cont["hits"]["hits"]:
            # Grim, grim, grim håndtering
            if r"/virksomhed/" in self._url:
                if hit["_source"]["Vrvirksomhed"]["virksomhedMetadata"]["nyesteNavn"] is None:
                    continue
                results.append(self.__parse_response(hit))
            else:
                results.append(self.__parse_response_penhed(hit))
        return results

    def __parse_response_penhed(self, hit: dict) -> dict:
        """
        NB! Samles med __parse_respose til én CVRResponse klasse        
        Trækker relevante informationer ud fra den returnerede json-streng. Bør nok håndteres anderledes, da 
        det er forskelligt hvilke info, som reelt er relevante. 
        Lav om til en "response klasse" som kan genanvendes andre steder."""
        result = {}
        if hit["_source"]["VrproduktionsEnhed"]["produktionsEnhedMetadata"]["nyesteNavn"] is None:
            return result
        result["name"] = hit["_source"]["VrproduktionsEnhed"]["produktionsEnhedMetadata"]["nyesteNavn"]["navn"]
        result["pnr"] = hit["_source"]["VrproduktionsEnhed"]["pNummer"]
        try:
            result["cvr"] = hit["_source"]["VrproduktionsEnhed"]["virksomhedsrelation"][0]["cvrNummer"]
        except IndexError:
            print(self.query_term)
            pass
        result["status"] = hit["_source"]["VrproduktionsEnhed"]["produktionsEnhedMetadata"]["sammensatStatus"]
        result["match_score"] = hit["_score"]
        return result
    
    def __parse_response(self, hit: dict) -> dict:
        """Trækker relevante informationer ud fra den returnerede json-streng. Bør nok håndteres anderledes, da 
        det er forskelligt hvilke info, som reelt er relevante. 
        Lav om til en "response klasse" som kan genanvendes andre steder."""
        result = {}
        if hit["_source"]["Vrvirksomhed"]["virksomhedMetadata"]["nyesteNavn"] is None:
            return result
        result["name"] = hit["_source"]["Vrvirksomhed"]["virksomhedMetadata"]["nyesteNavn"]["navn"]
        result["cvr"] = hit["_source"]["Vrvirksomhed"]["cvrNummer"]
        result["status"] = hit["_source"]["Vrvirksomhed"]["virksomhedMetadata"]["sammensatStatus"]
        result["match_score"] = hit["_score"]
        return result
    
    def __query_search_step(self, opr: str, field: str) -> list:
        """Omskrives til flere funktioner..."""
        self.query_operator = opr
        self.query_field = field
        query = self.__create_query()
        result = self.__parse_query(query)
        parsed_results = self.__parse_responses(result)
        if not parsed_results:
            return []  # Det samme som False
        for idx, pr in enumerate(parsed_results):
            temp_lratio = CVRNameComparator(self.query_term, parsed_results[idx]["name"]).lratio()
            if parsed_results[idx]["status"].lower() in ["aktiv", "normal"]:
                parsed_results[idx]["aktiv"] = 1
            else:
                parsed_results[idx]["aktiv"] = 0
            parsed_results[idx]["lratio"] = temp_lratio
            parsed_results[idx]["query_operator"] = self.query_operator
            parsed_results[idx]["query_field"] = self.query_field
            # Ualmindelig uelegant håndtering
            if opr == "AND" and len(self.query_term.split(" "))> 1 and field == "Vrvirksomhed.binavne.navn":
                parsed_results[idx]["lratio"] = 1
            
        # Oprydning - fjerner alle de hits med en lratio under grænseværdi. 
        reduced_results = [pr for pr in parsed_results if pr["lratio"] >= self.lrt]
        # Hvis der er to eller flere hits med lratio=1, så fjerne lratio=1 and aktiv=0. Kan gøres mere elegant...
        lratio_aktiv = sum(i["lratio"] for i in reduced_results if i["lratio"]==1 and i["aktiv"]==1)
        lratio_inaktiv = sum(i["lratio"] for i in reduced_results if i["lratio"]==1 and i["aktiv"]==0)
        if lratio_aktiv > 0 and lratio_inaktiv > 0:
            reduced_results = [i for i in reduced_results if i["aktiv"]==1 and i["lratio"]==1]
        # Sorterer resultaterne desc på lratio
        sorted_results = sorted(reduced_results, key=itemgetter("lratio"), reverse=True)            
        return sorted_results

    def __run_search(self) -> list:
        self._url = self._url_virk
        """Logik som itererer igennem en række forskellige søgningstyper for at opnå det bedste match."""
        search_fields = [
            "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn",
            "Vrvirksomhed.binavne.navn",
        ]
        
        for opr in ["AND", "OR"]:
            for field in search_fields:
                step = self.__query_search_step(opr, field)
                if step and max([r["lratio"] for r in step])==1:
                    return step
        # Forsøg på at ramme virksomheder, hvor der af en eller anden årsag er angivet komma i navnet. Skal sikkert ikke implementeres generelt
        if "," in self.query_term:
            for i in self.query_term.split(","):
                self.query_term = i
                for opr in ["AND", "OR"]:
                    for field in search_fields:
                        step = self.__query_search_step(opr, field)
                        if step and max([r["lratio"] for r in step])==1:
                            return step
        # Ugh - omskrives
        search_fields_penhed = [
            "VrproduktionsEnhed.produktionsEnhedMetadata.nyesteNavn.navn",
            # "Vrvirksomhed.binavne.navn",
        ]        
        self._url = self._url_penh
        for opr in ["AND", "OR"]:
            for field in search_fields_penhed:
                step = self.__query_search_step(opr, field)
                if step and max([r["lratio"] for r in step])==1:
                    return step
        return step  # Fall back - sker, hvis der ikke findes præcise hits
    
    def __handle_name(self, search_term: str) -> str:
        return run_name_handler(search_term)

    def search_based_on_name(self, 
                             name: str, 
                             pnr: bool = False, 
                             max_returned_results: int = 20, 
                             max_query_results: int = 100, 
                             lratio_thres: float = 0.5
                             ) -> list:
        # Sætter parametre som klasse variable, så de kan refereres i andre funktioner uden at parse dem som argumenter.
        self.query_term = self.__handle_name(name)
        self.mrr = max_returned_results
        self.mqr = max_query_results  # Afgører hvor mange søgeresultater cvr maksimalt skal returnere
        self.pnr_search = pnr  # Afgører om der også skal søges på p-numre eller udelukkende cvr
        self.lrt = lratio_thres  # Grænseværdi for hvilke lratio værdier, som skal medtages
        exact_search_results = self.__run_search()
        return exact_search_results
    
    def __search_based_on_cvr(self, cvr: str) -> json:
        query = {"query": {"bool": {"must": [{"term": {"Vrvirksomhed.cvrNummer": cvr}}]}}}
        self._url = self._url_virk
        response = self._response(query)
        response.raise_for_status()
        return json.loads(response.content)

    def __search_based_on_cvrp(self, cvr: str) -> json:
        query = {"query": {"bool": {"must": [{"term": {"VrproduktionsEnhed.pNummer": cvr}}]}}}
        self._url = self._url_penh
        response = self._response(query)
        response.raise_for_status()
        return json.loads(response.content)
    
    def cvr_search(self, cvr: list[int]) -> list[CVRResponse]:
        if not isinstance(cvr, list):
            raise TypeError("Input skal være en liste med cvr numre")
        results = []
        for c in cvr:
            hits_from_cvr = self.__search_based_on_cvr(str(c))
            results.append(CVRResponse(hits_from_cvr["hits"]["hits"][0]))
        return results

    def cvr_search_to_df(self, cvr: list[int], latest: bool = True, measure: str = None) -> pd.DataFrame:
        """Grimt - skal skrives om. Midlertidig løsning for at inkludere historiske data for cvr-nummeret."""
        if not isinstance(cvr, list):
            raise TypeError("Input skal være en liste med cvr numre")
        print(f"Henter CVR data for {len(cvr)} cvr-numre")
        results = []
        for c in tqdm(cvr):
            hits_from_cvr = self.__search_based_on_cvr(str(c))
            if hits_from_cvr["hits"]["total"] > 0:
                if latest:
                    api_results = CVRResponse(hits_from_cvr["hits"]["hits"][0]).get_data()
                    api_results["hit_type"] = "cvr"
                    results.append(api_results)
                else:
                    api_results = CVRResponse(hits_from_cvr["hits"]["hits"][0]).get_data(all=True, unit = "aar")
                    results.extend(api_results)
            else:
                hits_pnr = self.__search_based_on_cvrp(str(c))
                if hits_pnr["hits"]["total"] > 0:
                    api_results = CVRResponse(hits_pnr["hits"]["hits"][0]).get_data()
                    api_results["hit_type"] = "pnr"
                    api_results["pnr"] = int(c)
                    results.append(api_results)
                else:
                    results.append({"cvr": int(c)})
        return pd.DataFrame.from_dict(results)
    
    def __search_financial_based_on_cvr(self, cvr: str) -> bytes:
        self._url = self._url_regnskab
        query = {"query": {"bool": {"must": [{"term": {"cvrNummer": cvr}}, { "term": { "dokumenter.dokumentMimeType": "application" } }, { "term": { "dokumenter.dokumentMimeType": "xml" } }]}}}
        response = self._response(query)
        response.raise_for_status()
        return json.loads(response.content)
    
    def cvr_financial_search_to_df(self, cvr: list[int], limit: int = 1) -> pd.DataFrame:
        if not isinstance(cvr, list):
            raise TypeError("Input skal være en liste med cvr numre")
        print(f"Henter CVR regnskabsdata for {len(cvr)} cvr-numre")        
        results = []
        for c in tqdm(cvr):
            hits = self.__search_financial_based_on_cvr(str(c))
            if hits["hits"]["total"] > 0:
                off_regnskaber = self.__extract_xblr_urls(hits)
                if off_regnskaber:
                    results_temp = self.__handle_xblr_documents(off_regnskaber, limit)
                    results.extend(results_temp)
                else:
                    results.append({"cvr": c, "tom_aarsag": "Hits, men ingen xblr regnskaber"})
                pass
            else:
                results.append({"cvr": c, "tom_aarsag": "Ingen hits"})
                
        return pd.DataFrame.from_dict(results)
    
    # def __handle_xblr_documents(self, documents: list[dict], limit: int) -> list[dict]:
    #     results = []
    #     documents_to_proces = documents[:limit]
    #     for doc in documents_to_proces:
    #         url = doc["dokument_url"]
    #         downloaded_doc = self.__download_xblr_document(url)
    #         parsed_doc = Regnskab(downloaded_doc, documents_to_proces["start_dato"], documents_to_proces["slut_dato"]).get_data_as_dict()
    #         results.append(parsed_doc)
    #     return results

    def __handle_xblr_documents(self, documents: list[dict], limit: int) -> list[dict]:
        results = []
        documents_to_process = documents[:limit]

        def process_doc(doc: dict):
            url = doc["dokument_url"]
            downloaded_doc = self.__download_xblr_document(url)
            parsed_doc = Regnskab(downloaded_doc, doc["cvr"], doc["start_dato"], doc["slut_dato"]).get_data_as_dict()
            return parsed_doc            

        with ThreadPoolExecutor(max_workers=None) as executor:  # Adjust the number of workers as needed
            # Submit tasks to the executor
            futures = [executor.submit(process_doc, doc) for doc in documents_to_process]
            
            # Collect results as they complete
            for future in as_completed(futures):
                results.append(future.result())  # Get the result from each completed future

        return results
                
    def __download_xblr_document(self, url: str) -> bytes:
        xblr_document = requests.request(
            method="GET",
            url=url,
            headers=self._headers,
            auth=HTTPBasicAuth(self.__creds.username, self.__creds.password)
            )
        xblr_document.raise_for_status()
        return xblr_document
    
    def __extract_xblr_urls(self, hits: bytes) -> list[dict]:
        regnskaber = [hit for hit in hits["hits"]["hits"] if hit["_source"]["offentliggoerelsestype"]]
        regnskaber_red = []
        for r in regnskaber:
            output = {}
            output["cvr"] = r["_source"]["cvrNummer"]            
            output["start_dato"] = r["_source"]["regnskab"]["regnskabsperiode"]["startDato"]
            output["slut_dato"] = r["_source"]["regnskab"]["regnskabsperiode"]["slutDato"]
            for dok in r["_source"]["dokumenter"]:
                if dok["dokumentMimeType"] == r"application/xml":
                    output["dokument_url"] = dok["dokumentUrl"]
            regnskaber_red.append(output)
        regnskaber_red.sort(key=lambda x: x["start_dato"], reverse=True)
        return regnskaber_red


@dataclass
class CVRNameComparator:
    """...
    t1: str   
    Input streng - navnet på virksomheden som skal tjekkes op imod output fra CVR søgning
    t2: str    
    Output streng fra cvr søgning"""
    t1: str
    t2: str
    
    def __post_init__(self):
        self.t1_cleaned, self.t2_cleaned = self.__prep_strings()
    
    def __prep_strings(self) -> list:
        temp_t1, temp_t2 = self.t1.lower().split(" "), self.t2.lower().split(" ")
        return temp_t1, temp_t2
    
    def __ratio_case_1(self) -> float:
        # Case 1 - der er i indtastningen udeladt virk.form, hvilket synes at være en relativt ofte forekommende udfordring
        virk_typer = ["a/s", "aps", "i/s", "s/i"]
        if not [o for o in self.t1_cleaned if o in virk_typer]:
            temp_t2_red = [o for o in self.t2_cleaned if o not in virk_typer]
            temp_lratio = ratio(self.t1_cleaned, temp_t2_red)
            if temp_lratio == 1:
                return temp_lratio
        return 0
   
    def __ratio_case_default(self) -> float:
        # Case 2 - generel case
        # Starter med at fjerne termer fra input og output som overlapper for på den måde udelukkende at beregne ratio på restmængden.
        temp_t1 = " ".join([i for i in self.t1_cleaned if i not in self.t2_cleaned])
        temp_t2 = " ".join([i for i in self.t2_cleaned if i not in self.t1_cleaned])
        return ratio(temp_t1, temp_t2)
    
    def lratio(self) -> float:
        temp_lratio = self.__ratio_case_1()
        if temp_lratio == 1:
            return temp_lratio
        # temp_lratio = self.__ratio_case_2()
        return self.__ratio_case_default()