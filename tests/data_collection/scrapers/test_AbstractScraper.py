from unittest import TestCase

import pandas as pd

from ElectionForecasting.data_collection.scrapers.AbstractScraper import AbstractScraper
from ElectionForecasting.data_collection.scrapers.fivethirtyeight.scraper import FiveThirtyEightScraper
from ElectionForecasting.data_collection.scrapers.realclearpolitics.realclearpolitics import RealClearPoliticsScraper

import pytest


# Since AbstractScraper is a template class, we want to run the below tests on ALL scrapers
# We do this by getting every registered subclass of AbstractScraper and putting them in a list.
# We make sure to ignore AbstractScraper itself, since it cannot be instantiated
SCRAPERS = [c for c in AbstractScraper.get_registry().values() if c._registry_name != AbstractScraper._registry_name]


@pytest.mark.parametrize('scraper_type', SCRAPERS)
def test_get_raw_house_data(scraper_type):
    # Ensure every scraper has the correct columns in its raw house data
    scraper: AbstractScraper = scraper_type()
    columns = ['EndDate', 'StartDate', 'ElectionDate', 'Party', 'District', 'Percent', ]

    raw_house_polls: pd.DataFrame = scraper.get_raw_house_data()
    for col in columns:
        assert col in raw_house_polls.columns


@pytest.mark.parametrize('scraper_type', SCRAPERS)
def test_get_raw_generic_ballot_data(scraper_type):
    # Ensure every scraper has the correct columns in its raw house data
    scraper: AbstractScraper = scraper_type()
    columns = ['EndDate', 'StartDate', 'ElectionDate', 'District', 'Republican', 'Democratic', 'Libertarian', 'Green', 'Independent']

    raw_house_polls: pd.DataFrame = scraper.get_raw_generic_ballot_data()
    for col in columns:
        assert col in raw_house_polls.columns


class TestAbstractScraper(TestCase):

    def setUp(self) -> None:
        self.scraper = self.scraper_type()

    def test_get_raw_house_data(self):
        self.fail()

    def test_get_raw_generic_ballot_data(self):
        self.fail()

    def test_compile_raw_house_data_to_timeseries(self):
        self.fail()

    def test_compile_raw_generic_ballot_data_to_timeseries(self):
        self.fail()

    def test_compile_raw_polls_to_timeseries(self):
        self.fail()
        # TODO: Test start_date=None
        # TODO: assert only polls after start_date appear
