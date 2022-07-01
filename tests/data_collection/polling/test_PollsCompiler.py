import datetime

from .raw_generic_dataframe import raw_generic_df
import pytest

from ElectionForecasting.data_collection.polling.PollsCompiler import PollsCompiler


def test_obtain_house_poll_timeseries():
    election_date = datetime.date(2022, 11, 8)
    start_date = datetime.date(2022, 3, 13)
    compiler = PollsCompiler()
    rep_timeseries = compiler.obtain_house_poll_timeseries(party='Republican', election_date=election_date,
                                                           starting_date=start_date)
    assert len(rep_timeseries)  # Make sure it's not empty
    dem_timeseries = compiler.obtain_house_poll_timeseries(party='Democratic', election_date=election_date,
                                                           starting_date=start_date)
    assert len(dem_timeseries)  # Make sure it's not empty


def test_compile_raw_generic_ballot_data_to_timeseries():
    election_date = datetime.date(2022, 11, 8)
    start_date = datetime.date(2022, 3, 13)
    compiler = PollsCompiler()
    rep_timeseries = compiler.obtain_generic_house_poll_timeseries(party='Republican', election_date=election_date,
                                                                   starting_date=start_date)
    assert len(rep_timeseries)  # Make sure it's not empty
    dem_timeseries = compiler.obtain_generic_house_poll_timeseries(party='Democratic', election_date=election_date,
                                                                   starting_date=start_date)
    assert len(dem_timeseries)  # Make sure it's not empty


def test_compile_raw_polls_to_timeseries_with_start_date():
    compiler = PollsCompiler()
    start_date = datetime.date(2022, 3, 13)
    compiled_df = compiler.compile_raw_polls_to_timeseries(raw_generic_df, party='Republican',
                                                           election_date=datetime.date(2022, 11, 8),
                                                           starting_date=start_date)

    for col in compiled_df.columns:
        if isinstance(col, datetime.date):
            assert col > start_date  # Every column should be after the start_date


def test_compile_raw_polls_to_timeseries_without_start_date():
    compiler = PollsCompiler()
    start_date = datetime.date(2022, 3, 13)
    compiled_df = compiler.compile_raw_polls_to_timeseries(raw_generic_df, party='Republican',
                                                           election_date=datetime.date(2022, 11, 8),
                                                           starting_date=None)
    assert any(col < start_date for col in compiled_df.columns if isinstance(col, datetime.date))


def test_estimate_district_polls_from_generic_ballot():
    election_date = datetime.date(2022, 11, 8)
    start_date = datetime.date(2022, 3, 13)
    compiler = PollsCompiler()
    rep_timeseries = compiler.obtain_generic_house_poll_timeseries(party='Republican', election_date=election_date,
                                                                   starting_date=start_date)
    dem_timeseries = compiler.obtain_generic_house_poll_timeseries(party='Democratic', election_date=election_date,
                                                                   starting_date=start_date)

    rep_estimated_polls = compiler.estimate_district_polls_from_generic_ballot(rep_timeseries, 'Republican')
    dem_estimated_polls = compiler.estimate_district_polls_from_generic_ballot(dem_timeseries, 'Democratic')

    assert len(rep_estimated_polls) == 435  # Assert that all 435 districts are present
    assert len(dem_estimated_polls) == 435  # Assert that all 435 districts are present
    assert not rep_estimated_polls.isnull().values.any()  # Assert there are no NaN
    assert not dem_estimated_polls.isnull().values.any()  # Assert there are no NaN

    assert not rep_estimated_polls.equals(dem_estimated_polls)


