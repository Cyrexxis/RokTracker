from roktracker.ui.status_frame import AdditionalInfoData, InfoValue

kingdom_stats_placeholder = [
    InfoValue(name="id", display_name="ID", value="12345678"),
    InfoValue(name="name", display_name="Name", value="Super Governor"),
    InfoValue(name="power", display_name="Power", value="100000000"),
    InfoValue(name="killpoints", display_name="Killpoints", value="3000000000"),
    InfoValue(name="t1_kills", display_name="T1 Kills", value="0"),
    InfoValue(name="t2_kills", display_name="T2 Kills", value="0"),
    InfoValue(name="t3_kills", display_name="T2 Kills", value="0"),
    InfoValue(name="t4_kills", display_name="T2 Kills", value="0"),
    InfoValue(name="t5_kills", display_name="T2 Kills", value="10000000"),
    InfoValue(name="t45_kills", display_name="T4+5 Kills", value="10000000"),
    InfoValue(name="total_kills", display_name="Total Kills", value="10000000"),
    InfoValue(name="ranged_points", display_name="Total Kills", value="200000"),
    InfoValue(name="deads", display_name="Total Kills", value="1000000"),
    InfoValue(name="assistance", display_name="Total Kills", value="9000000000"),
    InfoValue(name="gathered", display_name="Total Kills", value="10000000000"),
    InfoValue(name="helps", display_name="Total Kills", value="90000"),
    InfoValue(
        name="alliance", display_name="Total Kills", value="Biggest Alliance ever!"
    ),
]

additional_stats_placeholder = AdditionalInfoData(
    current_time="00:00:00",
    eta_remaining="00:00:00",
    current_amount=0,
    target_amount=300,
    skipped=0,
)
