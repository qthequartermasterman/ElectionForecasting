import pandas as pd
from typing import Optional
from datetime import date
from .scrapers import SCRAPERS, AbstractScraper
from collections import defaultdict


class PollsCompiler:
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

        # Define the column names
        end_date_col = AbstractScraper.end_date_col
        election_date_col = AbstractScraper.election_date_col
        party_col = AbstractScraper.party_col
        district_col = AbstractScraper.district_col
        percent_col = AbstractScraper.percent_col

        compiled_df: pd.DataFrame = pd.DataFrame()
        # Take each row, and put the poll results in the correct date column and district row
        district_date_counts = defaultdict(lambda: 0)
        for index, row in raw_poll_df.iterrows():
            # print(row['election_date'], row['party'])
            if (
                    row[election_date_col] == election_date and
                    row[party_col] == party and
                    (not starting_date or (row[end_date_col] > starting_date))
            ):
                # TODO: Logic about what to do if multiple polls for a district occur on the same date
                # TODO: For now, just take the average

                if row[district_col] in compiled_df.index and row[end_date_col] in compiled_df.columns:
                    compiled_df.loc[row[district_col], row[end_date_col]] += row[percent_col]
                else:
                    compiled_df.loc[row[district_col], row[end_date_col]] = row[percent_col]
                district_date_counts[(row[district_col], row[end_date_col])] += 1
        compiled_df = compiled_df.copy()  # Defragment the frame
        for (district, date), count in district_date_counts.items():
            compiled_df.loc[district, date] /= count
        compiled_df = compiled_df.sort_index()
        compiled_df = compiled_df.sort_index(axis=1, ascending=True)
        return compiled_df
