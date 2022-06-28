import datetime
from unittest import TestCase

import pandas as pd

from ElectionForecasting.data_collection.polling.scrapers import SCRAPERS
from ElectionForecasting.data_collection.polling.scrapers import AbstractScraper



import pytest


@pytest.mark.parametrize('scraper_type', SCRAPERS)
def test_get_raw_house_data(scraper_type):
    # Ensure every scraper has the correct columns in its raw house data
    scraper: AbstractScraper = scraper_type()
    columns = ['EndDate', 'StartDate', 'ElectionDate', 'Party', 'District', 'Percent', 'PopulationType', 'SampleSize']

    raw_house_polls: pd.DataFrame = scraper.get_raw_house_data()
    for col in columns:
        assert col in raw_house_polls.columns

    # Assert that every column is unique--no duplicated headers that could break things
    assert raw_house_polls.columns.is_unique


@pytest.mark.parametrize('scraper_type', SCRAPERS)
def test_get_raw_generic_ballot_data(scraper_type):
    # Ensure every scraper has the correct columns in its raw house data
    scraper: AbstractScraper = scraper_type()
    columns = ['EndDate', 'StartDate', 'ElectionDate', 'District', 'Republican', 'Democratic', 'Libertarian', 'Green',
               'Independent', 'PopulationType', 'SampleSize']

    raw_house_polls: pd.DataFrame = scraper.get_raw_generic_ballot_data()
    for col in columns:
        assert col in raw_house_polls.columns

    # Assert that every column is unique--no duplicated headers that could break things
    assert raw_house_polls.columns.is_unique


