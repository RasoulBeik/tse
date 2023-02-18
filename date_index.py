import pandas as pd
from datetime import datetime, timedelta
from symbol import Symbol

def date_range(start_date, end_date, days_step=1, to_string=True):
    days = (end_date - start_date).days
    all_dates = [start_date + timedelta(days=d) for d in range(0, days, days_step)]
    all_dates = [date.isoformat() for date in all_dates]
    if to_string:
        all_dates = [str(d) for d in all_dates]
        # all_dates = [str(d).replace('-', '') for d in all_dates]
    return all_dates


if __name__ == "__main__":
    symbol1 = Symbol('پترول')
    df = symbol1.sort_descending().get_df().copy()
    df = df.reset_index(drop=True)

    df3 = pd.DataFrame(columns=symbol1.get_df().columns)
    df3['date'] = date_range(datetime.now().date(), datetime.now().date() + timedelta(days=10))
    df3.index = range(-1, -11, -1)
    df3 = df3.sort_values(by='date', ascending=False)

    df = pd.concat([df3, df])
    print(df.loc[0])
    print(df.loc[-1])
    print(df.loc[-10])
