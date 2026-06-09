from typing import List

from rich.markup import escape
from rich.table import Table

from roktracker.ranking.ranking_data import AdditionalRankingData, RankingData
from roktracker.utils.console import console


def print_batch(govs: List[RankingData], extra: AdditionalRankingData) -> None:
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
