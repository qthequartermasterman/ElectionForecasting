import datetime
from unittest import TestCase

import pandas as pd

from ElectionForecasting.data_collection.polling.scrapers.AbstractScraper import AbstractScraper
from ElectionForecasting.data_collection.polling.scrapers.fivethirtyeight.scraper import FiveThirtyEightScraper
from ElectionForecasting.data_collection.polling.scrapers.realclearpolitics.realclearpolitics import RealClearPoliticsScraper
from ElectionForecasting.data_collection.DataCollectionUtils import str_to_date

from .raw_generic_dataframe import raw_generic_df

import pytest

# Since AbstractScraper is a template class, we want to run the below tests on ALL scrapers
# We do this by getting every registered subclass of AbstractScraper and putting them in a list.
# We make sure to ignore AbstractScraper itself, since it cannot be instantiated.

SCRAPERS = [c for c in AbstractScraper.get_registry().values() if c._registry_name != AbstractScraper._registry_name]


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


@pytest.mark.parametrize('scraper_type', SCRAPERS)
def test_compile_raw_house_data_to_timeseries(scraper_type):
    scraper: AbstractScraper = scraper_type()
    pytest.fail()


@pytest.mark.parametrize('scraper_type', SCRAPERS)
def test_compile_raw_generic_ballot_data_to_timeseries(scraper_type):
    scraper: AbstractScraper = scraper_type()
    pytest.fail()


@pytest.mark.parametrize('scraper_type', SCRAPERS)
def test_compile_raw_polls_to_timeseries_with_state_date(scraper_type):
    scraper: AbstractScraper = scraper_type()
    scraper.compile_raw_polls_to_timeseries(raw_generic_df, party='Republican',
                                            election_date=datetime.date(2022, 11, 8),
                                            starting_date=datetime.date(2022, 3, 13))



    pytest.fail()
    # TODO: assert only polls after start_date appear


@pytest.mark.parametrize('scraper_type', SCRAPERS)
def test_compile_raw_polls_to_timeseries_without_state_date(scraper_type):
    scraper: AbstractScraper = scraper_type()
    pytest.fail()
    # TODO: Test start_date=None
