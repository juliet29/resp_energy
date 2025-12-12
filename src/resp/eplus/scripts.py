from resp.eplus.generate import generate_experiments
from pathlib import Path

from replan2eplus.ezcase.ez import EZ
from rich import print

from resp.paths import OutputCampaignNames, Constants
from resp.eplus.campaign_interfaces import CampaignData
from resp.eplus.campaign import campaign_defn

from resp.config import OUTPUT_CAMPAIGN_NAME, WEATHER_FILE, ANALYSIS_PERIOD


def run_generate_experiments():
    print("Preparing to generate experimens. Campaign defn=")
    print(campaign_defn)
    generate_experiments([], Path(""))


def run_execute_experiments(campaign_name: OutputCampaignNames = OUTPUT_CAMPAIGN_NAME):
    meta_data_of_failures = []

    for exp in CampaignData(campaign_name).experiments:
        try:
            case = EZ(exp.path / Constants.idf_name, read_existing=False)
            # TODO: read_existing -> read_objects / read_run_settings, then use run_settings..
            # TODO: this should be part of replan..
            case.save_and_run(
                output_path=exp.path,
                epw_path=WEATHER_FILE,
                run=True,
                analysis_period=ANALYSIS_PERIOD,
                save=False,
            )  # TODO think this should also have a default weather

        except Exception as e:
            print(e)
            print(f"Running idf at {exp.path.name} failed!")
            meta_data_of_failures.append(exp.metadata)

        if len(meta_data_of_failures) >= 3:
            raise Exception(f"Too many failures.. stopping: {meta_data_of_failures}")

    print("Metadata of failed experiments:")
    print(meta_data_of_failures)


if __name__ == "__main__":
    # run_generate_experiments()
    run_execute_experiments()
