from openpyxl import Workbook
from openpyxl.styles import Font
from roktracker.alliance.governor_data import GovernorData
from roktracker.utils.general import *
from openpyxl.drawing.image import Image as OpImage
from typing import List


class ExcelHandler:
    def __init__(self, filename, date):
        self.save_path = filename

        self.wb = Workbook()
        self.sheet = self.wb.active
        self.sheet.title = str(date)

        self.header_font = Font(bold=True)

        # Initialize Excel Sheet Header
        self.sheet["A1"] = "Name Image"
        self.sheet["B1"] = "Governor Name"
        self.sheet["C1"] = "Governor Score"

        self.sheet.column_dimensions["A"].width = 42
        self.sheet["A1"].font = self.header_font
        self.sheet["B1"].font = self.header_font
        self.sheet["C1"].font = self.header_font

    def save(self):
        self.wb.save(self.save_path)

    def check_for_duplicate(self, governor: GovernorData, governor_number: int) -> bool:
        for row in self.sheet.iter_rows(
            min_col=2,
            max_col=3,
            min_row=max(2, governor_number - 5),
            max_row=governor_number + 1,
        ):
            if row[0].value == governor.name and row[1].value == to_int_check(
                governor.score
            ):
                return True
        return False

    def add_results_to_sheet(self, governors: List[GovernorData], screen_number: int):
        reached_bottom = False
        govs_per_screen = len(governors)
        duplicates = 0
        for gov_num, governor in enumerate(governors):
            current_gov = (govs_per_screen * screen_number) + gov_num - duplicates

            if self.check_for_duplicate(governor, current_gov):
                print(f"Removed duplicated governor ({governor.name}).")
                duplicates += 1
                # Duplicate can only happen on the last page
                reached_bottom = True
                continue

            self.sheet.row_dimensions[current_gov + 2].height = 24.75
            # Write results in excel file
            self.sheet.add_image(
                OpImage(governor.img_path),
                "A" + str(current_gov + 2),
            )

            self.sheet["B" + str(current_gov + 2)] = governor.name
            self.sheet["C" + str(current_gov + 2)] = to_int_check(governor.score)

        return reached_bottom
