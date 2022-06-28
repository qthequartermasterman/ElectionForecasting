from abc import abstractmethod
from collections import defaultdict
from datetime import date
from typing import Optional

import pandas as pd

from ElectionForecasting.data_collection.polling.scrapers.ABCRegistry import ABCRegistry


class AbstractScraper(metaclass=ABCRegistry):
    _registry_name = 'abstract_scraper'

    # Define the column names
    end_date_col = 'EndDate'
    start_date_col = 'StartDate'
    election_date_col = 'ElectionDate'
    party_col = 'Party'
    district_col = 'District'
    percent_col = 'Percent'
    population_col = 'PopulationType'
    sample_size_col = 'SampleSize'

    @staticmethod
    @abstractmethod
    def get_raw_house_data(url: Optional[str] = None) -> pd.DataFrame:
        """
        Obtain the raw house district polls from a data source, formatted as a pandas DataFrame.
        Each row should be a unique poll result. Columns should include (but are not limited to):
        - District: str of format "StateNameInCamelCase-##" where ## is the zero-padded district number
        - Party: str representing party name for Poll result. Must be in
            ['Republican', 'Democratic', 'Libertarian', 'Green', 'Independent']
        - Percent: float representing the percent of the vote for the party
        - StartDate: date object representing the start date of the poll
        - EndDate: date object representing the start date of the poll
        - ElectionDate: date object representing the date of the election

        :param url: Optional[str] from which to scrape the house data.
        :return: pd.DataFrame with the poll data including above columns
        """
        pass

    @staticmethod
    @abstractmethod
    def get_raw_generic_ballot_data(url: Optional[str] = None) -> pd.DataFrame:
        """
        Obtain the raw generic ballot house polls from a data source, formatted as a pandas DataFrame.
        Each row should be a unique poll. Columns should include (but are not limited to):
        - District: str equal to "Generic Ballot"
        - StartDate: date object representing the start date of the poll
        - EndDate: date object representing the start date of the poll
        - Republican: float representing the percent of the vote for the Republican party
        - Democratic: float representing the percent of the vote for the Democratic party
        - Libertarian: float representing the percent of the vote for the Libertarian party
        - Green: float representing the percent of the vote for the Green party
        - Independent: float representing the percent of the vote for the Independent party

        :param url: Optional[str] from which to scrape the house data.
        :return: pd.DataFrame with the poll data including above columns
        """
        pass

