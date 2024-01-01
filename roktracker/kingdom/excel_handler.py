from openpyxl import Workbook
from openpyxl.styles import Font
from roktracker.kingdom.governor_data import GovernorData
from roktracker.utils.general import next_alpha, to_int_check


class ExcelHandler:
    def __init__(self, scan_options, filename, date):
        self.save_path = filename
        self.scan_options = scan_options

        self.wb = Workbook()
        self.sheet = self.wb.active
        self.sheet.title = str(date)

        self.header_font = Font(bold=True)
        self.colNames = self.assign_columns()

    def assign_columns(self):
        assigned_cols = {}
        current_char = "A"

        if self.scan_options["ID"]:
            assigned_cols.update({"ID": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Name"]:
            assigned_cols.update({"Name": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Power"]:
            assigned_cols.update({"Power": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Killpoints"]:
            assigned_cols.update({"Killpoints": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Deads"]:
            assigned_cols.update({"Deads": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["T1 Kills"]:
            assigned_cols.update({"T1 Kills": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["T2 Kills"]:
            assigned_cols.update({"T2 Kills": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["T3 Kills"]:
            assigned_cols.update({"T3 Kills": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["T4 Kills"]:
            assigned_cols.update({"T4 Kills": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["T5 Kills"]:
            assigned_cols.update({"T5 Kills": current_char})
            current_char = next_alpha(current_char)

        if (
            self.scan_options["T1 Kills"]
            and self.scan_options["T2 Kills"]
            and self.scan_options["T3 Kills"]
            and self.scan_options["T4 Kills"]
            and self.scan_options["T5 Kills"]
        ):
            assigned_cols.update({"Total Kills": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["T4 Kills"] and self.scan_options["T5 Kills"]:
            assigned_cols.update({"T45 Kills": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Ranged"]:
            assigned_cols.update({"Ranged": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Rss Gathered"]:
            assigned_cols.update({"Rss Gathered": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Rss Assistance"]:
            assigned_cols.update({"Rss Assistance": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Helps"]:
            assigned_cols.update({"Helps": current_char})
            current_char = next_alpha(current_char)

        if self.scan_options["Alliance"]:
            assigned_cols.update({"Alliance": current_char})
            current_char = next_alpha(current_char)

        return assigned_cols

    def createHeader(self, display_name, name):
        if name in self.colNames:
            self.sheet[str(self.colNames[name]) + "1"] = display_name
            self.sheet[str(self.colNames[name]) + "1"].font = self.header_font

    def setCell(self, name, row, value):
        if name in self.colNames:
            self.sheet[str(self.colNames[name]) + str(row)] = value

    def write_governor(self, row: int, gov_data: GovernorData) -> None:
        # fmt: off
        # Write results in excel file
        self.setCell("ID", row, to_int_check(gov_data.id))
        self.setCell("Name", row, gov_data.name)
        self.setCell("Power", row, to_int_check(gov_data.power))
        self.setCell("Killpoints", row, to_int_check(gov_data.killpoints))
        self.setCell("Deads", row, to_int_check(gov_data.dead))
        self.setCell("T1 Kills", row, to_int_check(gov_data.t1_kills))
        self.setCell("T2 Kills", row, to_int_check(gov_data.t2_kills))
        self.setCell("T3 Kills", row, to_int_check(gov_data.t3_kills))
        self.setCell("T4 Kills", row, to_int_check(gov_data.t4_kills))
        self.setCell("T5 Kills", row, to_int_check(gov_data.t5_kills))
        self.setCell("Total Kills", row, to_int_check(gov_data.total_kills()))
        self.setCell("T45 Kills", row, to_int_check(gov_data.t45_kills()))
        self.setCell("Ranged", row, to_int_check(gov_data.ranged_points))
        self.setCell("Rss Gathered", row, to_int_check(gov_data.rss_gathered))
        self.setCell("Rss Assistance", row, to_int_check(gov_data.rss_assistance))
        self.setCell("Helps", row, to_int_check(gov_data.helps))
        self.setCell("Alliance", row, gov_data.alliance.rstrip())

    # fmt: on

    def save(self):
        self.wb.save(self.save_path)
