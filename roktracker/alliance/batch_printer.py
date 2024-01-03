from typing import List
from roktracker.alliance.additional_data import AdditionalData

from roktracker.alliance.governor_data import GovernorData
from roktracker.utils.console import console

from rich.markup import escape
from rich.table import Table


def print_batch(govs: List[GovernorData], extra: AdditionalData) -> None:
    # nice output for console
    table = Table(
        title="["
        + extra.current_time
        + "]\n"
        + "Latest Scan Result\nGovernor "
        + f"{extra.current_page * extra.govs_per_page} - {extra.current_page * extra.govs_per_page + len(govs)}"
        + " of "
        + str(extra.target_governor),
        show_header=True,
        show_footer=True,
    )
    table.add_column("Governor Name", "Approx time remaining", style="magenta")
    table.add_column("Score", extra.eta(), style="cyan")

    for governor in govs:
        table.add_row(escape(governor.name), str(governor.score))

    console.print(table)
