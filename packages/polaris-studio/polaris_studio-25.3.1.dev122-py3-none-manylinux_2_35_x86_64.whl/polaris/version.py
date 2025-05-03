# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
# from datetime import datetime, date

previous_year_release = 2025
previous_month_release = 1

year_release = 2025
month_release = 3
day_release = 1
alpha = 122

__version__ = f"{str(year_release)[-2:]}.{str(month_release).zfill(2)}.{str(day_release).zfill(3)}.dev{alpha}"
