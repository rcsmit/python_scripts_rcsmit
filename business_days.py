# a company in tourism has to decide if they give everybody a fixed salary per month or
# one that it is based on the number of businessdays in the month.

import datetime
import numpy as np
import pandas as pd

season_start, season_end = 6, 9  # number of month (included)
length_season = season_end - season_start + 1
month_list, years_list, workdays_years = (
    [
        "Jan",
        "Feb",
        "March",
        "Apr",
        "May",
        "June",
        "July",
        "Aug",
        "Sept",
        "Okt",
        "Nov",
        "Dec",
    ],
    [],
    [],
)
difference_total = 0
# maandsalaris op parttimebasis
# uren_per_week, maandsalaris= 36, 1439.75 #2018  # supervisor  €1603,35
#uren_per_week, maandsalaris  = 35, 1489.37 # 2021
#uren_per_week, maandsalaris  = 35, 1689.57 # 2022
uren_per_week, maandsalaris  = 40, 2150 # 2022
uursalaris = maandsalaris / (uren_per_week * 4.33333333333)

factor = uren_per_week / 5 * uursalaris

for year in range(2018, 2025):
    workdays_per_month = []
    years_list.append(year)
    season_work_days, total_businessdays_year = 0, 0
    for month in range(1, 13):
        if month == 12:
            year_end = year + 1
            month_end = 1
        else:
            year_end = year
            month_end = month + 1
        start = datetime.date(year, month, 1)
        end = datetime.date(year_end, month_end, 1)

        days = np.busday_count(start, end)

        total_businessdays_year += days
        # print(f'{month} - {year} - Number of business days is: {days} / cumm = {total_businessdays_year}')
        workdays_per_month.append(days)
        if month >= season_start and month <= season_end:
            season_work_days += days
    workdays_years.append(workdays_per_month)
    avg_workdays_month = total_businessdays_year / 12

    # print(f'---- {year} - Total number Number of business days is: {total_businessdays_year} | avg {avg_workdays_month} per month')
    equal_pay = avg_workdays_month * length_season
    difference = season_work_days - equal_pay
    difference_total += difference
    print(
        f"---- {year} - With equal pay : {round(equal_pay,1)}. | With businessday-method {season_work_days} | Difference {round(difference,1)} || Per month: { round(avg_workdays_month,2)} / {round(season_work_days/length_season,2)} | EUR {round(avg_workdays_month* factor,0)} / {round(season_work_days/length_season * factor,0)}"
    )
print(f"TOTAL DIFFERENCE  ALL YEARS {round(difference_total,1)}")

df_ = pd.DataFrame(workdays_years, index=years_list, columns=month_list)
df = pd.DataFrame(df_).T

df.loc["Column_Mean"] = df.mean(numeric_only=True, axis=0).round(1)
df.loc[:, "Row_Mean"] = df.mean(numeric_only=True, axis=1).round(1)
print(df)


df_salary = df.multiply(factor).round(0)
print(df_salary)
