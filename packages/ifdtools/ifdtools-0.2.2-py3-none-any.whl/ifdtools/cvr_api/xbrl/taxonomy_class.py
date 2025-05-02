# %%

from pathlib import Path
import lxml.etree as et
import pandas as pd
from dataclasses import dataclass

@dataclass
class XBRLTaxonomy:
    type: str
    
    def __post_init__(self):
        self.__validate_setup()
        
    def __validate_setup(self):
        assert self.type in ["fsa", "ifrs"], f"Den angivne taksonomi type er ikke kendt: {self.type}"
        assert self.__def_file.exists(), f"Filen {self.__def_file} findes ikke."
        assert self.__labels_file.exists(), f"Filen {self.__labels_file} findes ikke."
        
    def generate_taxo_df(self) -> pd.DataFrame:
        
        pass
        
    @property
    def __def_file(self):
        return Path(Path(__file__).parent, "ressources", self.type, f"{self.type}.xsd")
    
    @property
    def __labels_file(self):
        return Path(Path(__file__).parent, "ressources", self.type, f"{self.type}_labels.xml")

    
# %%

tester = XBRLTaxonomy("fsa")

# %%

test = Path(r"c:\Users\B375192\python_projects\ifdtools\ifdtools\cvr_api\xbrl\ressources\fsa")

# %%


taxo_def = et.parse(r"C:\Users\B375192\python_projects\ifdtools\ifdtools\cvr_api\ressources\fsa\fsa.xsd").getroot()
taxo_label = et.parse(r"C:\Users\B375192\python_projects\ifdtools\ifdtools\cvr_api\ressources\fsa\fsa-lab-da.xml").getroot()
namespaces_def: dict = taxo_def.nsmap
namespaces_label: dict = taxo_label.nsmap

# %%

# Finder relevante elementer fra definitionen af taksonomien

rel_elems = []

for elem in taxo_def.findall("*"):
    if elem.tag.endswith(r"}element"):
        temp_dict = {}
        for attr in elem.attrib:
            temp_dict[attr] = elem.get(attr)
        rel_elems.append(temp_dict)

# %%

# Finder matchende labels

rel_labels = []

# What a fucking shit show

for elem in taxo_label.findall("*"):
    if elem.tag.endswith(r"}labelLink"):
        for sub_elem in elem:
            local_name = sub_elem.tag.split(r"}")[1]
            temp_dict = {}
            if local_name == "loc":
                for attr in sub_elem.attrib:
                    if "}" in attr:
                        attr_local_name = attr.split(r"}")[1]
                        temp_dict[attr_local_name] = sub_elem.get(attr)
                        continue
                    temp_dict[attr] = sub_elem.get(attr)
                label_elem = sub_elem.getnext()
                temp_dict["label"] = label_elem.text
            if temp_dict:
                rel_labels.append(temp_dict)

# %%

taxo_defs = pd.DataFrame.from_dict(rel_elems)
taxo_labels = pd.DataFrame.from_dict(rel_labels)

# %%

# Opkoder labels til én række pr unik identifier

# Danner columns input

taxo_labels["nb"] = taxo_labels.groupby(["href"]).cumcount() + 1
taxo_labels["nb_str"] = "label_" + taxo_labels["nb"].astype(str)

# %%

taxo_labels_pivot = taxo_labels.pivot_table(
    index="href",
    columns="nb_str",
    values="label",
    aggfunc="first"
).reset_index()

# %%

# Merger de to dataframe

temp_col = taxo_labels_pivot.href.str.split(r"#", expand=True)
taxo_labels_pivot["merge_key"] = temp_col[1]
taxo_defs = taxo_defs.merge(taxo_labels_pivot, how="left", left_on="id", right_on="merge_key", suffixes=("", "_labels"))

# %%

taxo_defs.to_csv(r"c:\users\b375192\desktop\fsa_taxo_defs.csv", encoding="utf-8-sig", sep=";", decimal=",")
taxo_labels_pivot.to_csv(r"c:\users\b375192\desktop\fsa_taxo_labels.csv", encoding="utf-8-sig", sep=";", decimal=",")
# %%


test = XBRLTaxonomy("fsa")
# %%
