"""Placeholder values for the GUI."""

from roktracker.ui.status_frame import AdditionalInfoData, InfoValue

KINGDOM_STATS_PLACEHOLDER = [
    InfoValue(name="id", display_name="ID", value="12345678"),
    InfoValue(name="name", display_name="Name", value="Super Governor"),
    InfoValue(name="power", display_name="Power", value="100000000"),
    InfoValue(name="killpoints", display_name="Killpoints", value="3000000000"),
    InfoValue(name="acclaim", display_name="Acclaim", value="340000"),
    InfoValue(name="acclaim_max", display_name="Highest Acclaim", value="2000000"),
    InfoValue(name="t1_kills", display_name="T1 Kills", value="0"),
    InfoValue(name="t2_kills", display_name="T2 Kills", value="0"),
    InfoValue(name="t3_kills", display_name="T2 Kills", value="0"),
    InfoValue(name="t4_kills", display_name="T2 Kills", value="0"),
    InfoValue(name="t5_kills", display_name="T2 Kills", value="10000000"),
    InfoValue(name="t45_kills", display_name="T4+5 Kills", value="10000000"),
    InfoValue(name="total_kills", display_name="Total Kills", value="10000000"),
    InfoValue(name="ranged_points", display_name="Ranged", value="200000"),
    InfoValue(name="dead", display_name="Dead", value="1000000"),
    InfoValue(name="assistance", display_name="Assisted", value="9000000000"),
    InfoValue(name="gathered", display_name="Gathered", value="10000000000"),
    InfoValue(name="helps", display_name="Helps", value="90000"),
    InfoValue(name="alliance", display_name="Alliance", value="Biggest Alliance ever!"),
]

RANKING_STATS_PLACEHOLDER = [
    InfoValue(name="governor_0", display_name="Super Governor 1", value="1000"),
    InfoValue(name="governor_1", display_name="Super Governor 2", value="500"),
    InfoValue(name="governor_2", display_name="Super Governor 3", value="250"),
    InfoValue(name="governor_3", display_name="Super Governor 4", value="125"),
    InfoValue(name="governor_4", display_name="Super Governor 5", value="64"),
    InfoValue(name="governor_5", display_name="Super Governor 6", value="32"),
]

ADDITIONAL_STATS_PLACEHOLDER = AdditionalInfoData(
    current_time="00:00:00",
    eta_remaining="00:00:00",
    current_amount=0,
    target_amount=300,
    skipped=0,
)

ADDITIONAL_RANKING_STATS_PLACEHOLDER = AdditionalInfoData(
    current_time="00:00:00",
    eta_remaining="00:00:00",
    current_amount=0,
    target_amount=100,
    skipped=-1,
)
