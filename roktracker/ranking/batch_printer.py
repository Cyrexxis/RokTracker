from typing import List

from rich.markup import escape
from rich.table import Table

from roktracker.common.data import AdditionalScanData
from roktracker.ranking.ranking_data import RankingData
from roktracker.utils.console import console


def print_batch(govs: List[RankingData], extra: AdditionalScanData) -> None:
    # nice output for console
    table = Table(
        title="["
        + extra.current_time_str()
        + "]\n"
        + "Latest Scan Result\nGovernor "
        + f"{extra.current_governor}"
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
