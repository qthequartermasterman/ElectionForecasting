import numpy as np
import pandas as pd
from typing import Optional, Dict, List
from datetime import date, timedelta

from .scrapers import SCRAPERS, AbstractScraper
from collections import defaultdict

from ..DataCollectionUtils import cache_download_csv_to_file, daterange
from ..cookpvi.CookPviScraper import cook_pvi_data
from ..districts.DistrictSimilarity import DistrictSimilarity

STARTING_DATE = date(2022, 3, 13)
ELECTION_DATE = date(2022, 11, 8)
REFRESH_TIME = 1


class PollsCompiler:
    """Interface to take raw polls and compile them into usable Timeseries DataFrames."""
    district_similarity = DistrictSimilarity()

    # @cache_download_csv_to_file('../../data/compiled_polls/house_polls_timeseries.csv', refresh_time=REFRESH_TIME)
    def obtain_house_poll_timeseries(self, party: str = 'Republican', election_date=ELECTION_DATE,
                                     starting_date=STARTING_DATE, window_days=7) -> pd.DataFrame:
        """
        Obtain a `pd.DataFrame` with each row representing polling averages for each house district. Columns represent
        dates between the first poll and the election.
        :param starting_date: first date to start recording polls (all polls before this date are discarded)
        :param party: standard party name for the party we want timeseries data for
        :param election_date: `datetime.date` object representing the date of the election
        :return: `pd.DataFrame` with a timeseries row for each house district
        """
        combined_raw_polls = pd.concat([scraper.get_raw_house_data() for scraper in SCRAPERS])
        house_timeseries = self.compile_raw_house_data_to_timeseries(combined_raw_polls,
                                                                     party=party,
                                                                     election_date=election_date,
                                                                     starting_date=starting_date)

        generic_timeseries = self.obtain_generic_house_poll_timeseries(party=party,
                                                                       election_date=election_date,
                                                                       starting_date=starting_date)

        estimated_polls_from_generic = self.estimate_district_polls_from_generic_ballot(
            generic_timeseries=generic_timeseries, party=party)
        correlated_districts = self.average_correlated_district_polls(house_timeseries)

        house_timeseries = self.interpolate_district_polls(house_timeseries, election_date=election_date)
        estimated_polls_from_generic = self.interpolate_district_polls(estimated_polls_from_generic,
                                                                       election_date=election_date)
        correlated_districts = self.interpolate_district_polls(correlated_districts, election_date=election_date)

        house_timeseries = self.window_district_timeseries(house_timeseries, window_days=window_days)
        estimated_polls_from_generic = self.window_district_timeseries(estimated_polls_from_generic,
                                                                       window_days=window_days)
        correlated_districts = self.window_district_timeseries(correlated_districts, window_days=window_days)

        # We want the cell-wise mean of those three dataframes, but pandas has no easy way to do this.
        # Instead, we concat the three df into one with MultiIndex, group by the top level index, and
        # then mean-aggregate rows with the same index
        concat = pd.concat([house_timeseries, estimated_polls_from_generic, correlated_districts]).groupby(level=0)
        return concat.agg('mean')

    # @cache_download_csv_to_file('../../data/compiled_polls/generic_house_polls_timeseries.csv', refresh_time=REFRESH_TIME)
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
        district_date_counts = defaultdict(lambda: defaultdict(lambda: 0))
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

                district_date_counts[(district, end_date)]['party_count'] += row[percent_col] * row[sample_size_col]
                district_date_counts[(district, end_date)]['total_count'] += row[sample_size_col]

        for (district, end_date), count in district_date_counts.items():
            compiled_df.loc[district, end_date] = district_date_counts[(district, end_date)]['party_count'] / \
                                                  district_date_counts[(district, end_date)]['total_count']

        compiled_df = compiled_df.copy()  # Defragment the frame
        compiled_df = compiled_df.sort_index()
        compiled_df = compiled_df.sort_index(axis=1, ascending=True) / 100
        return compiled_df

    @classmethod
    def estimate_district_polls_from_generic_ballot(cls, generic_timeseries: pd.DataFrame, party: str) -> pd.DataFrame:
        """
        Estimate a district's polling average by adding its PVI to the generic timeseries.
        :param generic_timeseries:
        :param party:
        :return:
        """
        if party not in ['Republican', 'Democratic']:
            raise ValueError(f'Party {party} is not currently supported when estimating district polls from generic.')
        pvi = cook_pvi_data[['New PVI Raw']] / 100
        if party == 'Democratic':  # We will add points to democratic districts and subtract from republican
            pvi = -pvi
        return pd.DataFrame(pvi.values + generic_timeseries.values, columns=generic_timeseries.columns, index=pvi.index)

    @classmethod
    def average_correlated_district_polls(cls, district_timeseries: pd.DataFrame) -> pd.DataFrame:
        """
        Transform each row (district timeseries) into a weighted average of similar districts, to show
        correlated effects.

        If two districts are similar, then they will likely vote similarly on election day, even if polls don't show
        that clearly.

        :param district_timeseries: pd.DataFrame with each row being a district timeseries
        :return:
        """
        correlated_timeseries = district_timeseries.copy()
        for index, row in district_timeseries.iterrows():
            similar_districts: Dict[str, float] = cls.district_similarity.get_similar_districts(str(index))
            similar_district_df = correlated_timeseries.loc[
                [key for key in similar_districts if key in district_timeseries.index]]
            correlated_timeseries.loc[index] = similar_district_df.mean()

        return correlated_timeseries

    @staticmethod
    def brownian_bridge(num: int, a: float = 0, b: float = 0, trials: int = 10, mu: float = 0,
                        sigma: float = 1) -> np.ndarray:
        """
        Generate a numpy array with shape (trials, num) where each trial is a generalized brownian bridge between a and
        b with length num. This means that each trial (of length num) is a brownian walk that begins with a and ends
        with b.

        :param num: length of each generalized brownian bridge
        :param a: start point of each generalized brownian bridge
        :param b: end point of each generalized brownian bridge
        :param trials: number of generalized brownian bridges
        :param mu: mean of the normal distribution generating the brownian walks
        :param sigma: standard deviation of the normal distribution generating the brownian walks
        :return: numpy array of shape (trial, num) where each row is a generalized brownian walk
        """
        # Generate the unconstrained brownian walks
        z = np.random.normal(mu, sigma, size=(trials, num))
        z[:, 0] = 0
        z = z.cumsum(axis=1)

        # Transform those brownian walks, so they become standard brownian bridges (i.e. begin and end at 0)
        t = np.linspace(0, 1, num)
        t = np.broadcast_to(t, z.shape)
        x = z - t * np.broadcast_to(z[:, -1], t.T.shape).T

        # Transform the standard brownian bridges, so they begin and end at a and b respectively
        return (1 - t) * a + t * b + x

    @staticmethod
    def brownian_interpolation(x: np.ndarray, xp: np.ndarray, fp: np.ndarray, trials: int = 10, mu: float = 0,
                               sigma: float = .01) -> np.ndarray:
        """
        Fill in any NaN values in arr by interpolating the values with brownian walks.
        :param x: The x-coordinates at which to evaluate the interpolated values.
        :param xp: 1-D sequence of floats. The x-coordinates of the data points, must be increasing if argument period
            is not specified. Otherwise, xp is internally sorted after normalizing the periodic
            boundaries with xp = xp % period.
        :param fp: 1-D sequence of float or complex. The y-coordinates of the data points, same length as xp.
        :param trials: number of generalized brownian bridges to average over
        :param mu: mean of the normal distribution generating the brownian walks
        :param sigma: standard deviation of the normal distribution generating the brownian walks
        """
        interp = np.interp(x, xp, fp, right=np.NaN)
        random_walk = PollsCompiler.brownian_bridge(num=len(x), trials=trials, mu=mu, sigma=sigma, a=0, b=0)
        random_walk = random_walk.mean(axis=0)
        # TODO: Add a random walk to the linear interpolation that fixes the walk to 0 at each of the values in xp

        return interp+random_walk
        #return interp

    @staticmethod
    def interpolate_district_polls(district_timeseries: pd.DataFrame, election_date:date, step=timedelta(1)) -> pd.DataFrame:
        # Make sure the columns are in time order so our underlying numpy arrays satisfy the requirements of our
        # numpy interpolation functions
        district_timeseries = district_timeseries.sort_index(axis=1)

        # We want to interpolate every day from the beginning to the end of the polling period
        dates: List[date] = list(daterange(min(district_timeseries.columns),
                                           election_date,
                                           step=step
                                           )
                                 )
        dates_int = np.array([d.toordinal() for d in dates])
        dates_int_current_cols = np.array([d.toordinal() for d in district_timeseries.columns])

        # Do the interpolation
        polls_np = district_timeseries.to_numpy()
        interpolated_polls = [PollsCompiler.brownian_interpolation(dates_int,
                                                                   dates_int_current_cols,
                                                                   fp)
                              for fp in polls_np]
        interpolated_polls_np = np.stack(interpolated_polls)
        # Return this as a dataframe with the new dates as the columns and retaining the old indices
        return pd.DataFrame(interpolated_polls_np, columns=dates, index=district_timeseries.index)

    @staticmethod
    def window_district_timeseries(district_timeseries: pd.DataFrame, window_days=7) -> pd.DataFrame:
        district_timeseries = district_timeseries.sort_index(axis=1)
        rolling = district_timeseries.T.rolling(window_days, min_periods=1, closed='both').mean()
        return rolling[::-1][::window_days][::-1].T  # we want the step to end on the last day, not start on the first
