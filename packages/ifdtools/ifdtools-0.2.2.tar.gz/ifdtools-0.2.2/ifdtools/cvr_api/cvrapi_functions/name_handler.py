translations = {
    "municipality": "kommune",
    # "university": "universitet",
}

one_to_one = {
    "au": "aarhus universitet",
    "dtu": "danmarks tekniske universitet",
    "dti": "teknologisk institut",
    "sdu": "syddansk universitet (university of southern denmark)",
}

replacements = {
    "alexandra inst.": "alexandra instituttet",
    "university of copenhagen": "københavns universitet",
    "uni. copenhagen": "københavns universitet",
    "technical university of denmark": "danmarks tekniske universitet",
    "aarhus universitet": "aarhus universitet",
    "aarhus university": "aarhus universitet",
    "university of southern denmark": "syddansk universitet (university of southern denmark)",
    "syddansk universitet": "syddansk universitet (university of southern denmark)",
    "sdu,": "syddansk universitet (university of southern denmark)", 
    ", sdu": "syddansk universitet (university of southern denmark)", 
    "(sdu)": "syddansk universitet (university of southern denmark)", 
    "danish regions": "danske regioner",
    "(ouh)": "odense universitets hospital",
    "Odense University Hospital": "odense universitets hospital",
    "rigshospitalet": "rigshospitalet",
    "danish technological institute": "teknologisk institut",
    "roskilde university": "roskilde universitet",
    "aalborg university": "aalborg universitet",
    "uc absalon": "Professionshøjskolen Absalon S/I",
    "steno diabetes center": "steno diabetes center",
    "holbæk hospital": "Holbæk sygehus - Smedelundsgade",

    }

def run_name_handler(virk_navn: str) -> str:
    """Lidt dum funktion, som retter typiske engelske termer til dansk og erstatter bestemte termer. Google Translate kræver billing og vi vil sikkert kunne
    holde os under "limit", men på den korte bane tænker jeg at en tilpasning er fint
    
    På sigt bør replacements dict'en flyttes til en seperat fil, da den har relevans andre steder + potentielt som en tabel i dwh.
    """
    term_upd = virk_navn.lower()
    for uc, r in one_to_one.items():
        if uc == term_upd:
            return r
    for t, r in replacements.items():
            if t in term_upd:
                return r
    for en, da in translations.items():
        term_upd = term_upd.replace(en, da)

    return term_upd