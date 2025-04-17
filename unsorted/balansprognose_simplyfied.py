""" A script to calculate the loss or gain after x months working in a year with a montly salary of y
    This calculation is a simplification

    Goal is to learn to work with OOP and make the script pythonic as much as possible.  

    TODO : calculate the total capital after z years, with taking inflation in account

Returns:
    A dataframe like this:

                0     1     2     3     4     5     6     7     8      9     10     11     12
    salary
    1400   -8750 -7380 -6010 -4640 -3270 -1900  -530   840  2210   3580   4950   6320   7690
    1600   -8750 -7220 -5690 -4160 -2630 -1100   430  1960  3490   5020   6550   8080   9610
    1800   -8750 -7060 -5370 -3680 -1990  -300  1390  3080  4770   6460   8150   9840  11530
    2000   -8750 -6900 -5050 -3200 -1350   500  2350  4200  6050   7900   9750  11600  13450
    2200   -8750 -6740 -4730 -2720  -710  1300  3310  5320  7330   9340  11350  13360  15370
    2400   -8750 -6580 -4410 -2240   -70  2100  4270  6440  8610  10780  12950  15120  17290

"""

import pandas as pd


class MyPrediction:
    def __init__(self):
        pass

    def calculate_year_delta(self, salary_gross_month, number_of_month_working):
        """Calculate the difference of income and expenses in a year.

        Args:
            salary_gross (int): What is my gross salary per month?
            number_of_month_working (int): How many months in the year do I work?

        Returns:
            int : the amount of money that I gain or loose in a year given the arguments
        """

        monthly_costs_nl = 500
        monthly_costs_asia = 750

        number_of_months_in_asia = 12 - (number_of_month_working + 1)
        number_of_months_in_nl = number_of_month_working + 1
        salary_gross_year = number_of_month_working * salary_gross_month

        total_income_netto = 0.8 * salary_gross_year

        expenses_total = (monthly_costs_nl * number_of_months_in_nl) + (
                           monthly_costs_asia * number_of_months_in_asia
        )
        delta = total_income_netto - expenses_total
        return delta


def main():
    mp = MyPrediction()
    list_total = []
    for salary_gross_month in range(1400, 2500, 200):
        row = [salary_gross_month]
        for number_of_month_working in range(0, 13):
            total_capital = 10000
            # TODO: later we want to know what the total capital is after x years, hence the (for now) useless loop
            for y in range(
                0, 1
            ):  
                delta = mp.calculate_year_delta(
                    salary_gross_month=salary_gross_month,
                    number_of_month_working=number_of_month_working,
                )
                total_capital = total_capital + delta
                row.append(int(delta))
        list_total.append(row)

    columns = ["salary"] + list(range(0, 13))

    total_df = pd.DataFrame(list_total, columns=columns).set_index("salary")
    print(total_df)


if __name__ == "__main__":
    main()
