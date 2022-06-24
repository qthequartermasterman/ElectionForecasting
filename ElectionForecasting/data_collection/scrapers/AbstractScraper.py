from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date
from typing import Optional

import pandas as pd


class AbstractScraper(ABC):
    @staticmethod
    @abstractmethod
    def get_raw_house_data(url: Optional[str] = None) -> pd.DataFrame:
        pass

    @staticmethod
    @abstractmethod
    def get_raw_generic_ballot_data(url: Optional[str] = None) -> pd.DataFrame:
        pass

    @classmethod
    def compile_raw_house_data_to_timeseries(cls, raw_poll_df: pd.DataFrame, party: str, election_date: date,
                                             starting_date: Optional[date] = None) -> pd.DataFrame:
        return cls.compile_raw_polls_to_timeseries(raw_poll_df, party, election_date, starting_date)

    @classmethod
    def compile_raw_generic_ballot_data_to_timeseries(cls, raw_poll_df: pd.DataFrame, party: str, election_date: date,
                                                      starting_date: Optional[date] = None) -> pd.DataFrame:
        return cls.compile_raw_polls_to_timeseries(raw_poll_df, party, election_date, starting_date)

    @staticmethod
    def compile_raw_polls_to_timeseries(raw_poll_df: pd.DataFrame, party: str, election_date: date,
                                        starting_date: Optional[date] = None) -> pd.DataFrame:
        compiled_df: pd.DataFrame = pd.DataFrame()
        # Take each row, and put the poll results in the correct date column and district row

        district_date_counts = defaultdict(lambda: 0)
        for index, row in raw_poll_df.iterrows():
            # print(row['election_date'], row['party'])
            if (
                    row['election_date'] == election_date and
                    row['party'] == party and
                    (not starting_date or (row['end_date'] > starting_date))
            ):
                # TODO: Logic about what to do if multiple polls for a district occur on the same date
                # TODO: For now, just take the average
                if row['District'] in compiled_df.index and row['end_date'] in compiled_df.columns:
                    compiled_df.loc[row['District'], row['end_date']] += row['pct']
                else:
                    compiled_df.loc[row['District'], row['end_date']] = row['pct']
                district_date_counts[(row['District'], row['end_date'])] += 1
        compiled_df = compiled_df.copy()  # Defragment the frame
        for (district, date), count in district_date_counts.items():
            compiled_df.loc[district, date] /= count
        compiled_df = compiled_df.sort_index()
        compiled_df = compiled_df.sort_index(axis=1, ascending=True)
        return compiled_df
