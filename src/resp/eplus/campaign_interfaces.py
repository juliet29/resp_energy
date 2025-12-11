from dataclasses import dataclass

from utils4plans.io import read_toml
from resp.paths import OutputCampaignNames, DynamicPaths, Constants
from pathlib import Path
from replan2eplus.results.sql import get_sql_results
from replan2eplus.ezcase.ez import EZ


@dataclass
class Experiment:
    path: Path

    @property
    def metadata(self):
        return read_toml(self.path, Constants.metadata)

    @property
    def case_name(self):
        return self.metadata["case"]

    @property
    def modifications(self):
        return self.metadata["modifications"]

    @property
    def category(self):
        # assuming only one for now..
        if self.modifications:
            return list(self.modifications.keys())[0]
        return ""

    @property
    def option(self):
        # assuming only one for now..
        if self.modifications:
            return list(self.modifications.values())[0]
        return ""

    def ezcase(self) -> EZ:
        case = EZ(idf_path=self.path / Constants.idf_name)
        return case

    # @property
    def get_sql_results(self):
        try:
            return get_sql_results(self.path)
        except AssertionError:
            raise Exception(
                f"Could not find sql results for {self.path.parent.name} / {self.path.name}"
            )


@dataclass
class CampaignData:
    # c1019 = "20251019_"
    name: OutputCampaignNames

    @property
    def path(self):
        return DynamicPaths.campaigns / self.name

    @property
    def metadata(self):
        return read_toml(self.path, Constants.metadata)

    @property
    def defn(self):
        return read_toml(self.path, Constants.definition)

    @property
    def experiments(self):
        return [Experiment(i) for i in self.path.iterdir() if i.is_dir()]

    @property
    def modification_categories(self):
        return [i["name"] for i in self.defn["modifications"]]


# if __name__ == "__main__":
#     c = CampaignData("20251019_")
#     # print(c.defn)
