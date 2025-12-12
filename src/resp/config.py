from replan2eplus.ezcase.ez import AnalysisPeriod
from resp.paths import DynamicPaths, InputCampaignNames, OutputCampaignNames


ROOM_HEIGHT = 10  # feet assumed, TODO: verify!
WEATHER_FILE = DynamicPaths.weather_pa2024
ANALYSIS_PERIOD = AnalysisPeriod("summer_cooling_season", 6, 10, 1, 31)
INPUT_CAMPAIGN_NAME: InputCampaignNames = "plus_subsurf"
OUTPUT_CAMPAIGN_NAME: OutputCampaignNames = "251211_plus_subsurf"
