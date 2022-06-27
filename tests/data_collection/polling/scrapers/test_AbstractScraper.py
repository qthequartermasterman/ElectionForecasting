import datetime
from unittest import TestCase

import pandas as pd

from ElectionForecasting.data_collection.polling.scrapers import SCRAPERS
from ElectionForecasting.data_collection.polling.scrapers import AbstractScraper

from .raw_generic_dataframe import raw_generic_df

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
