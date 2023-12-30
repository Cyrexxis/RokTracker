from rich.markup import escape
from rich.table import Table
from roktracker.kingdom.additional_data import AdditionalData
from roktracker.kingdom.governor_data import GovernorData
from roktracker.utils.console import console


def print_gov_state(gov_data: GovernorData, extra: AdditionalData) -> None:
    table = Table(
        title="["
        + extra.current_time
        + "]\n"
        + "Latest Scan Result\nGovernor "
        + str(extra.current_governor)
        + " of "
        + str(extra.target_governor),
        show_header=True,
        show_footer=True,
    )

    if bool(extra.kills_ok):
        table.add_column(
            "Entry",
            "Approx time remaining\nSkipped\nKills check out",
            style="magenta",
        )
        table.add_column(
            "Value",
            str(extra.eta())
            + "\n"
            + str(extra.skipped_governors)
            + "\n"
            + str(extra.kills_ok),
            style="cyan",
        )
    else:
        table.add_column(
            "Entry",
            "Approx time remaining\nSkipped\nKills check out\nReconstruct success",
            style="magenta",
        )
        table.add_column(
            "Value",
            str(extra.eta())
            + "\n"
            + str(extra.skipped_governors)
            + "\n"
            + str(extra.kills_ok)
            + "\n"
            + str(extra.reconstruction_success),
            style="cyan",
        )

    table.add_row("Governor ID", gov_data.id)
    table.add_row("Governor Name", gov_data.name)
    table.add_row("Governor Power", gov_data.power)
    table.add_row("Governor Kill Points", gov_data.killpoints)
    table.add_row("Governor Deads", gov_data.dead)
    table.add_row("Governor T1 Kills", gov_data.t1_kills)
    table.add_row("Governor T2 Kills", gov_data.t2_kills)
    table.add_row("Governor T3 Kills", gov_data.t3_kills)
    table.add_row("Governor T4 Kills", gov_data.t4_kills)
    table.add_row("Governor T5 Kills", gov_data.t5_kills)
    table.add_row("Governor T4+5 Kills", gov_data.t45_kills())
    table.add_row("Governor Total Kills", gov_data.total_kills())
    table.add_row("Governor Ranged Points", gov_data.ranged_points)
    table.add_row("Governor RSS Assistance", gov_data.rss_assistance)
    table.add_row("Governor RSS Gathered", gov_data.rss_gathered)
    table.add_row("Governor Helps", gov_data.helps)
    table.add_row("Governor Alliance", escape(gov_data.alliance))

    console.print(table)
