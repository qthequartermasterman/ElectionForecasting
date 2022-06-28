import datetime

from .raw_generic_dataframe import raw_generic_df
import pytest

from ElectionForecasting.data_collection.polling.PollsCompiler import PollsCompiler


def test_compile_raw_house_data_to_timeseries():
    compiler = PollsCompiler()
    pytest.fail()


def test_compile_raw_generic_ballot_data_to_timeseries():
    compiler = PollsCompiler()
    pytest.fail()


def test_compile_raw_polls_to_timeseries_with_start_date():
    compiler = PollsCompiler()
    start_date = datetime.date(2022, 3, 13)
    compiled_df = compiler.compile_raw_polls_to_timeseries(raw_generic_df, party='Republican',
                                                           election_date=datetime.date(2022, 11, 8),
                                                           starting_date=start_date)

    for col in compiled_df.columns:
        if isinstance(col, datetime.date):
            assert col < start_date
    # TODO: assert only polls after start_date appear


def test_compile_raw_polls_to_timeseries_without_start_date():
    compiler = PollsCompiler()
    compiled_df = compiler.compile_raw_polls_to_timeseries(raw_generic_df, party='Republican',
                                                           election_date=datetime.date(2022, 11, 8), )
    pytest.fail()
    # TODO: Test start_date=None
