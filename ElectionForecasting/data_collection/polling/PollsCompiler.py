import pandas as pd
from typing import Optional
from datetime import date

from .scrapers import SCRAPERS, AbstractScraper
from collections import defaultdict

from ..DataCollectionUtils import cache_download_csv_to_file
from ..cookpvi.CookPviScraper import cook_pvi_data

STARTING_DATE = date(2022, 3, 13)
ELECTION_DATE = date(2022, 11, 8)
REFRESH_TIME = 1


class PollsCompiler:
    """Interface to take raw polls and compile them into usable Timeseries DataFrames."""

    #@cache_download_csv_to_file('../../data/compiled_polls/house_polls_timeseries.csv', refresh_time=REFRESH_TIME)
    def obtain_house_poll_timeseries(self, party: str = 'Republican', election_date=ELECTION_DATE,
                                     starting_date=STARTING_DATE) -> pd.DataFrame:
        """
        Obtain a `pd.DataFrame` with each row representing polling averages for each house district. Columns represent
        dates between the first poll and the election.
        :param starting_date: first date to start recording polls (all polls before this date are discarded)
        :param party: standard party name for the party we want timeseries data for
        :param election_date: `datetime.date` object representing the date of the election
        :return: `pd.DataFrame` with a timeseries row for each house district
        """
        combined_raw_polls = pd.concat([scraper.get_raw_house_data() for scraper in SCRAPERS])
        return self.compile_raw_house_data_to_timeseries(combined_raw_polls,
                                                         party=party,
                                                         election_date=election_date,
                                                         starting_date=starting_date)

    #@cache_download_csv_to_file('../../data/compiled_polls/generic_house_polls_timeseries.csv', refresh_time=REFRESH_TIME)
    def obtain_generic_house_poll_timeseries(self, party: str = 'Republican', election_date=ELECTION_DATE,
                                             starting_date=STARTING_DATE) -> pd.DataFrame:
        """
        Obtain a `pd.DataFrame` with each row representing polling averages for each house district. Columns represent
        dates between the first poll and the election.
        :param starting_date: first date to start recording polls (all polls before this date are discarded)
        :param party: standard party name for the party we want timeseries data for
        :param election_date: `datetime.date` object representing the date of the election
        :return: `pd.DataFrame` with a timeseries row for each house district
        """
        combined_raw_polls = pd.concat([scraper.get_raw_generic_ballot_data() for scraper in SCRAPERS])
        return self.compile_raw_generic_ballot_data_to_timeseries(combined_raw_polls,
                                                                  party=party,
                                                                  election_date=election_date,
                                                                  starting_date=starting_date)

    @classmethod
    def compile_raw_house_data_to_timeseries(cls, raw_poll_df: pd.DataFrame, party: str, election_date: date,
                                             starting_date: Optional[date] = None) -> pd.DataFrame:
        return cls.compile_raw_polls_to_timeseries(raw_poll_df, party, election_date, starting_date)

    @classmethod
    def compile_raw_generic_ballot_data_to_timeseries(cls, raw_poll_df: pd.DataFrame, party: str, election_date: date,
                                                      starting_date: Optional[date] = None) -> pd.DataFrame:
        if party not in raw_poll_df.columns:
            raise ValueError(f'Party {party} not present in supplied raw polling dataframe')

        party_col = AbstractScraper.party_col
        percent_col = AbstractScraper.percent_col

        # If we put our desired party and percentage into the party and percent columns, we can re-use our previous
        # compile function
        raw_poll_df = raw_poll_df.copy()
        raw_poll_df[party_col] = party
        raw_poll_df[percent_col] = raw_poll_df[party].astype(float)

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
        sample_size_col = AbstractScraper.sample_size_col

        compiled_df: pd.DataFrame = pd.DataFrame()
        # Take each row, and put the poll results in the correct date column and district row
        district_date_counts = defaultdict(lambda: defaultdict(lambda:0))
        for index, row in raw_poll_df.iterrows():
            # print(row['election_date'], row['party'])
            if (
                    row[election_date_col] == election_date and
                    row[party_col] == party and
                    (not starting_date or (row[end_date_col] > starting_date))
            ):
                # TODO: estimate polling averages using correlated districts
                # TODO: smooth out polling averages over consecutive days
                district, end_date = row[district_col], row[end_date_col]

                district_date_counts[(district, end_date)]['party_count'] += row[percent_col]*row[sample_size_col]
                district_date_counts[(district, end_date)]['total_count'] += row[sample_size_col]

        for (district, end_date), count in district_date_counts.items():
            compiled_df.loc[district, end_date] = district_date_counts[(district, end_date)]['party_count']/district_date_counts[(district, end_date)]['total_count']

        compiled_df = compiled_df.copy()  # Defragment the frame
        compiled_df = compiled_df.sort_index()
        compiled_df = compiled_df.sort_index(axis=1, ascending=True)/100
        return compiled_df

    @classmethod
    def estimate_district_polls_from_generic_ballot(cls, generic_timeseries: pd.DataFrame, party:str):
        """
        Estimate a district's polling average by adding its PVI to the generic timeseries.
        :param generic_timeseries:
        :param party:
        :return:
        """
        if party not in ['Republican', 'Democratic']:
            raise ValueError(f'Party {party} is not currently supported when estimating district polls from generic.')
        pvi = cook_pvi_data[['New PVI Raw']]/100
        if party == 'Democratic':  # We will add points to democratic districts and subtract from repulican
            pvi = -pvi
        return pd.DataFrame(pvi.values + generic_timeseries.values, columns=generic_timeseries.columns, index=pvi.index)
