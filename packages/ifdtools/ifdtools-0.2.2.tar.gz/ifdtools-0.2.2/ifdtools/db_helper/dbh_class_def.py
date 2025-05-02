from dataclasses import dataclass
import pandas as pd
import sqlalchemy as sa
import urllib
import keyring

@dataclass
class DBHelper:
    server: str
    trusted: bool = True
    wincred: str = None
    
    def __post_init__(self):
        assert self.trusted or (not self.trusted and self.wincred), "Når du vælger trusted=False, så skal du angive wincred. Navnet på den credential, som du ønsker at anvende"
    
    def connect_engine(self, db: str, echo: bool = True) -> None:
        self.engine = self.__db_connect(db, echo)
        self.insp = sa.inspect(self.engine)

    def close(self) -> None:
        self.engine.dispose()
    
    def hent_data(self, db: str, query: str) -> pd.DataFrame:
        engine = self.connect_engine(db, echo=True)
        with open (query, "r") as q:
            df = pd.read_sql_query(q.read(), engine)
        return df    
    
    def __db_connect(self, db: str, echo: bool) -> sa.Engine:
        """
        Understøtter to muligheder for tilslutning til sql server
        Hvis trusted så anvendes den pågældende windows user, som kører scriptet
        Hvis ikke trused, så anvendes et sæt windows credentials til at logge på
        """
        if self.trusted:
            con_string = (
                f"DRIVER={{SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={db};"
                f"trusted_Connection={self.trusted}"
            )
            quoted_con_string = urllib.parse.quote_plus(con_string)
            db_engine = sa.create_engine(
                f"mssql+pyodbc:///?odbc_connect={quoted_con_string}", use_setinputsizes=False, echo=echo
            )
        else:
            db_engine = sa.create_engine(f"mssql+pymssql://{str(self.__credentials[0])}:{str(self.__credentials[1])}@{self.server}/{db}", echo=echo)
        return db_engine
    
    @property
    def __credentials(self) -> tuple[str, str]:
        creds = keyring.get_credential(self.wincred, None)
        if creds is None:
            raise ValueError(f"Den angivne credential {self.wincred} kan ikke findes i windows credentials")        
        return (str(creds.username), str(creds.password))
       
if __name__ == '__main__':
    source = DBHelper(server=r"C2100306\MSSQLSERVER01")
    try:
        source.connect_engine(r"1_PROD_COPY")
        print("Succes!")
    except sa.exc.ProgrammingError as err:
        print(err)
    source.close()
