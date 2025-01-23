from rich.markup import escape
from rich.table import Table
from roktracker.kingdom.types.additional_data import AdditionalData
from roktracker.kingdom.types.governor_data import GovernorData
from roktracker.utils.console import console


def print_gov_state(gov_data: GovernorData, extra: AdditionalData) -> None:
    table = Table(
        title="["
        + extra.current_time.strftime("%H:%M:%S")
        + "]\n"
        + "Latest Scan Result\nGovernor "
        + str(extra.current_governor)
        + " of "
        + str(extra.target_governor),
        show_header=True,
        show_footer=True,
    )

    first_title = "Entry"
    second_title = "Value"

    first_footer = "Approx time remaining\nSkipped\n"
    second_footer = str(extra.eta()) + "\n" + str(extra.skipped_governors) + "\n"

    if extra.power_ok != "Not Checked":
        first_footer += "Power ok\n"
        second_footer += str(extra.power_ok) + "\n"

    if extra.kills_ok != "Not Checked":
        first_footer += "Kills check out\n"
        second_footer += str(extra.kills_ok) + "\n"

        if (not extra.kills_ok) and extra.reconstruction_success != "Not Checked":
            first_footer += "Reconstruct success\n"
            second_footer += str(extra.reconstruction_success) + "\n"

    table.add_column(
        first_title,
        first_footer.rstrip(),
        style="magenta",
    )
    table.add_column(
        second_title,
        second_footer.rstrip(),
        style="cyan",
    )

    table.add_row("Governor ID", str(gov_data.id))
    table.add_row("Governor Name", gov_data.name)
    table.add_row("Governor Power", str(gov_data.power))
    table.add_row("Governor Kill Points", str(gov_data.killpoints))
    table.add_row("Governor Deads", str(gov_data.dead))
    table.add_row("Governor T1 Kills", str(gov_data.t1_kills))
    table.add_row("Governor T2 Kills", str(gov_data.t2_kills))
    table.add_row("Governor T3 Kills", str(gov_data.t3_kills))
    table.add_row("Governor T4 Kills", str(gov_data.t4_kills))
    table.add_row("Governor T5 Kills", str(gov_data.t5_kills))
    table.add_row("Governor T4+5 Kills", str(gov_data.t45_kills))
    table.add_row("Governor Total Kills", str(gov_data.total_kills))
    table.add_row("Governor Ranged Points", str(gov_data.ranged_points))
    table.add_row("Governor RSS Assistance", str(gov_data.rss_assistance))
    table.add_row("Governor RSS Gathered", str(gov_data.rss_gathered))
    table.add_row("Governor Helps", str(gov_data.helps))
    table.add_row("Governor Alliance", escape(gov_data.alliance))

    console.print(table)
