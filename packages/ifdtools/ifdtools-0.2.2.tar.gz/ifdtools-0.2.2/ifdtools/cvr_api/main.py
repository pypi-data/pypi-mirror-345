from datetime import datetime
import json
from pathlib import Path
import pandas as pd
import requests
import keyring
import functools
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
# Egne klasser
from .cvr_response_class import CVRResponse
from .cvr_regnskab_class import Regnskab
from .cvr_response_owner_class import CVROwner

@dataclass
class CVRAPI:
    """
    Klasse som trækker data fra cvr registret. Det er muligt at hente cvr data (antal ansatte, branche etc.)
    og regnskabsdata.
    
    Adgangen til CVRs api antager at credentials er tilføjet windows credentials. Se https://support.microsoft.com/en-us/windows/accessing-credential-manager-1b5c916a-6a16-889f-8581-fc16e8165ac0
    Det antages at de tiføjede credentials er navngivet cvr_api
    
    Skal opsplittes - alternativt skal funktionerne som tilhører de forskellige funktioner flyttes ud af klassen.
    
    """
   
    def __post_init__(self):
        self._url = self._url_virk
        self.__request_session = requests.Session()
        self.__test_setup()

    def __with_session(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.__request_session = requests.Session()
            try:
                return func(self, *args, **kwargs)
            finally:
                self.__request_session.close()
        return wrapper        
    
    @__with_session    
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
    
    def _response(self, payload: dict) -> requests.Response:
        resp = self.__request_session.request(
            method="POST",
            url=self._url,
            data=json.dumps(payload),
            headers=self._headers,
            auth=HTTPBasicAuth(self.__creds.username, self.__creds.password)
        )
        resp.raise_for_status()
        return resp

    @__with_session
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
    
    @__with_session
    def cvr_response_raw(self, cvr: int) -> dict:
        t_validate = self.__type_validate(cvr)
        if t_validate is None:
            raise ValueError("CVR/Pnr er ikke gyldigt")
        response = self.__search_based_on_cvr(str(cvr)) if t_validate == "cvr" else self.__search_based_on_cvrp(str(cvr))
        print(f"{t_validate}: {response}")
        return response
    
    @__with_session
    def cvr_search(self, cvr: list[int]) -> list[CVRResponse]:
        if not isinstance(cvr, list):
            raise TypeError("Input skal være en liste med cvr numre")
        if not all(isinstance(c, int) for c in cvr):
            raise ValueError("CVR skal være angivet som int")
        results = []
        for c in cvr:
            hits_from_cvr = self.__search_based_on_cvr(str(c))
            results.append(CVRResponse(hits_from_cvr["hits"]["hits"][0]))
        return results

    @__with_session    
    def cvr_search_owners_to_df(self, cvr: list[int], only_active: bool = True) -> pd.DataFrame:
        if not isinstance(cvr, list):
            raise TypeError("Input skal være en liste med cvr numre")
        if not all(isinstance(c, int) for c in cvr):
            raise ValueError("CVR skal være angivet som int")
                
        print(f"Henter CVR data (ejere) for {len(cvr)} cvr-numre")
        
        results = []
                
        def process_single_cvr(c):
            api_results = []
            hits_from_cvr = self.__search_based_on_cvr(str(c))
            if hits_from_cvr["hits"]["total"] > 0:
                api_results = CVROwner(hits_from_cvr["hits"]["hits"][0], c).get_data()
                return api_results
            else:
                return {
                    "cvr": c,
                    "fejl": "Opslaget gav ingen hits",
                }

        with ThreadPoolExecutor() as executor:
            future_to_cvr = {executor.submit(process_single_cvr, c): c for c in cvr}

            for future in tqdm(as_completed(future_to_cvr), total=len(cvr)):
                result = future.result()

                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)

        return pd.DataFrame.from_dict(results) if not only_active else pd.DataFrame.from_dict(results).query(r"aktiv==1")

    @__with_session    
    def cvr_search_to_df(self, cvr: list[int], latest: bool = True, measure: str = None) -> pd.DataFrame:
        """Grimt - skal skrives om. Midlertidig løsning for at inkludere historiske data for cvr-nummeret."""

        if not isinstance(cvr, list):
            raise TypeError("Input skal være en liste med cvr numre")
        
        print(f"Henter CVR data for {len(cvr)} cvr-numre")
        results = []
        
        def process_single_cvr(c):
            t_validate = self.__type_validate(c)

            if t_validate is None:
                return {"cvr": int(c), "tom_aarsag": "Det pågældende cvr/pnr er ikke gyldigt."}

            hits_from_cvr = self.__search_based_on_cvr(str(c)) if t_validate == "cvr" else self.__search_based_on_cvrp(str(c))
            
            if hits_from_cvr["hits"]["total"] == 0:
                return {"cvr": int(c), "tom_aarsag": "CVR/Pnr blev ikke fundet ved opslag i cvr-registeret."}
            
            if latest:
                api_results = CVRResponse(hits_from_cvr["hits"]["hits"][0]).get_data()
                api_results["hit_type"] = t_validate
                return api_results
            else:
                api_results = CVRResponse(hits_from_cvr["hits"]["hits"][0]).get_data(all=True, unit=measure)
                return api_results

        with ThreadPoolExecutor() as executor:
            future_to_cvr = {executor.submit(process_single_cvr, c): c for c in cvr}

            for future in tqdm(as_completed(future_to_cvr), total=len(cvr)):
                result = future.result()

                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
        
        return pd.DataFrame.from_dict(results)
    
    def __type_validate(self, cvr: int) -> str:
        """
        Validerer cvr som reelt både kan være cvr og pnr. 
        Udover validering returneres "typen".
        """
        if not isinstance(cvr, int):
            return None
        if len(str(cvr)) != 8 and len(str(cvr)) != 10:
            return None
        return "cvr" if len(str(cvr)) == 8 else "pnr"
        
    def __search_financial_based_on_cvr(self, cvr: str) -> bytes:
        self._url = self._url_regnskab
        query = {"query": {"bool": {"must": [{"term": {"cvrNummer": cvr}}, { "term": { "dokumenter.dokumentMimeType": "application" } }]}}, "size": 50}
        response = self._response(query)
        response.raise_for_status()
        return json.loads(response.content)
    
    @__with_session
    def cvr_financial_search_to_df(self, cvr: list[int], limit: int = 1, year: int = None) -> pd.DataFrame:
        
        if not isinstance(cvr, list):
            raise TypeError("Input skal være en liste med cvr numre")
        print(f"Henter CVR regnskabsdata for {len(cvr)} cvr-numre")
        # Henter oversættelsesfil ind som df
        translations_df = self.__load_translations_file()
        results = []
        
        def process_single_cvr(c: int) -> dict:
            hits = self.__search_financial_based_on_cvr(str(c))
            if hits["hits"]["total"] > 0:
                off_regnskaber = self.__extract_xblr_urls(hits, year)
                if off_regnskaber:
                    results_temp = self.__handle_xblr_documents(off_regnskaber, translations_df, limit if not year else 1)
                    return results_temp
                else:
                    return {"cvr": c, "tom_aarsag": "Hits, men ingen xblr regnskaber"}
            else:
                return {"cvr": c, "tom_aarsag": "Ingen hits"}

        with ThreadPoolExecutor() as executor:
            future_to_cvr = {executor.submit(process_single_cvr, c): c for c in cvr}
            
            for future in tqdm(as_completed(future_to_cvr), total=len(cvr)):
                result = future.result()
                
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)                
        
        return pd.DataFrame.from_dict(results)
    
    def __load_translations_file(self) -> pd.DataFrame:
        translations_file = Path(Path(__file__).parent, "xbrl", "ressources", "general", "general_translations.xlsx")
        assert translations_file.exists(), f"Filen {translations_file} findes ikke."
        return pd.read_excel(translations_file)

    def __handle_xblr_documents(self, documents: list[dict], translations_df: pd.DataFrame, limit: int) -> list[dict]:
        results = []
        documents_to_proces = documents[:limit]
        for doc in documents_to_proces:
            url = doc["dokument_url"]
            downloaded_doc = self.__download_xblr_document(url)
            parsed_doc = Regnskab(downloaded_doc, doc["cvr"], doc["start_dato"], doc["slut_dato"], translations_df).get_data_as_dict()
            results.append(parsed_doc)
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
    
    def __extract_xblr_urls(self, hits: bytes, year: int = None) -> list[dict]:
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
            # For regnskaber som ikke følger kalenderår, så følges nedenståede logik for at placere regnskabet i et aarstal
            if output["start_dato"][:4] != output["slut_dato"][:4]:
                start_of_end_year = datetime.strptime(f"{output["slut_dato"][:4]}-01-01", "%Y-%m-%d")
                diff_start = start_of_end_year - datetime.strptime(output["start_dato"], "%Y-%m-%d")
                diff_end = datetime.strptime(output["slut_dato"], "%Y-%m-%d") - start_of_end_year
                output["aarstal_afledt"] = int(output["start_dato"][:4]) if diff_start >= diff_end else int(output["slut_dato"][:4])
            else:
                output["aarstal_afledt"] = int(output["slut_dato"][:4])
            
            regnskaber_red.append(output)
            
        regnskaber_red = [dok for dok in regnskaber_red if "dokument_url" in dok]            
        regnskaber_red.sort(key=lambda x: x["start_dato"], reverse=True)
        if year:
            return [r for r in regnskaber_red if year == r["aarstal_afledt"]]
        return regnskaber_red