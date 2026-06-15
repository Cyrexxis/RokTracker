"""Console output for ranking scan batches.

Provides print_batch() for displaying a batch of governors as
a formatted table with progress and timing information."""

from typing import List

from rich.markup import escape
from rich.table import Table

from roktracker.common.data import AdditionalScanData
from roktracker.ranking.ranking_data import RankingData
from roktracker.utils.console import console


def print_batch(govs: List[RankingData], extra: AdditionalScanData) -> None:
    """Print governor batch to console via a nice looking table.

    Args:
        govs (List[RankingData]): The list of governors to print
        extra (AdditionalScanData): Additional data to display
    """
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
