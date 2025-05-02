import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectConfig:
    config_file: Path

    def __post_init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    @property
    def api_user(self) -> str:
        return str(self.config["CVRAPI"]["User"])

    @property
    def api_pw(self) -> str:
        return str(self.config["CVRAPI"]["Password"])

    @property
    def input_folder(self) -> Path:
        return Path(self.config["FOLDERS"]["InputFolder"])

    @property
    def output_folder(self) -> Path:
        return Path(self.config["FOLDERS"]["OutputFolder"])
