from typing import Iterable, Dict, List, Optional

import censusdata
import pandas as pd


def combine_dicts(dicts: Iterable[Dict]) -> Dict:
    """

    :param dicts:
    :return:
    """
    combined = {}
    for d in dicts:
        combined = {**combined, **d}
    return combined


def divide_subset_columns(df: pd.DataFrame, dividend_subset: List, divisor: str, in_place=True) -> pd.DataFrame:
    """

    :param df:
    :param dividend_subset:
    :param divisor:
    :return:
    """
    if not in_place:
        df = df.copy()
    df.loc[:, dividend_subset] = df.loc[:, dividend_subset].div(df[divisor], axis=0)
    return df


def get_district_short_name(geo: censusdata.censusgeo) -> str:
    """

    :param geo:
    :return:
    """
    return f"{geo.name.split(', ', maxsplit=-1)[1]}-{geo.geo[1][1]}"


primary_columns = {
    'B01001_001E': 'Total Population',
    'B19013_001E': 'Median household income in the past 12 months (in 2019 inflation-adjusted dollars)',
    'B25024_001E': 'UNITS IN STRUCTURE:Total',
}

units_subcounts_labels = {
    'B25024_002E': 'UNITS IN STRUCTURE:1, detached',
    'B25024_003E': 'UNITS IN STRUCTURE:1, attached',
    'B25024_004E': 'UNITS IN STRUCTURE:2',
    'B25024_005E': 'UNITS IN STRUCTURE:3 or 4',
    'B25024_006E': 'UNITS IN STRUCTURE:5 to 9',
    'B25024_007E': 'UNITS IN STRUCTURE:10 to 19',
    'B25024_008E': 'UNITS IN STRUCTURE:20 to 49',
    'B25024_009E': 'UNITS IN STRUCTURE:50 or more',
    'B25024_010E': 'UNITS IN STRUCTURE:Mobile home',
    'B25024_011E': 'UNITS IN STRUCTURE:Boat, RV, van, etc.',
}

subpopulation_columns_labels = {
    'B01001_002E': 'Male Population',
    'B01001_003E': 'Male Population: Under 5 years',
    'B01001_004E': 'Male Population: 5 to 9 years',
    'B01001_005E': 'Male Population: 10 to 14 years',
    'B01001_006E': 'Male Population: 15 to 17 years',
    'B01001_007E': 'Male Population: 18 and 19 years',
    'B01001_008E': 'Male Population: 20 years',
    'B01001_009E': 'Male Population: 21 years',
    'B01001_010E': 'Male Population: 22 to 24 years',
    'B01001_011E': 'Male Population: 25 to 29 years',
    'B01001_012E': 'Male Population: 30 to 34 years',
    'B01001_013E': 'Male Population: 35 to 39 years',
    'B01001_014E': 'Male Population: 40 to 44 years',
    'B01001_015E': 'Male Population: 45 to 49 years',
    'B01001_016E': 'Male Population: 50 to 54 years',
    'B01001_017E': 'Male Population: 55 to 59 years',
    'B01001_018E': 'Male Population: 60 and 61 years',
    'B01001_019E': 'Male Population: 62 to 64 years',
    'B01001_020E': 'Male Population: 65 and 66 years',
    'B01001_021E': 'Male Population: 67 to 69 years',
    'B01001_022E': 'Male Population: 70 to 74 years',
    'B01001_023E': 'Male Population: 75 to 79 years',
    'B01001_024E': 'Male Population: 80 to 84 years',
    'B01001_025E': 'Male Population: 85 years and over',
    'B01001_026E': 'Female Population:',
    'B01001_027E': 'Female Population: Under 5 years',
    'B01001_028E': 'Female Population: 5 to 9 years',
    'B01001_029E': 'Female Population: 10 to 14 years',
    'B01001_030E': 'Female Population: 15 to 17 years',
    'B01001_031E': 'Female Population: 18 and 19 years',
    'B01001_032E': 'Female Population: 20 years',
    'B01001_033E': 'Female Population: 21 years',
    'B01001_034E': 'Female Population: 22 to 24 years',
    'B01001_035E': 'Female Population: 25 to 29 years',
    'B01001_036E': 'Female Population: 30 to 34 years',
    'B01001_037E': 'Female Population: 35 to 39 years',
    'B01001_038E': 'Female Population: 40 to 44 years',
    'B01001_039E': 'Female Population: 45 to 49 years',
    'B01001_040E': 'Female Population: 50 to 54 years',
    'B01001_041E': 'Female Population: 55 to 59 years',
    'B01001_042E': 'Female Population: 60 and 61 years',
    'B01001_043E': 'Female Population: 62 to 64 years',
    'B01001_044E': 'Female Population: 65 and 66 years',
    'B01001_045E': 'Female Population: 67 to 69 years',
    'B01001_046E': 'Female Population: 70 to 74 years',
    'B01001_047E': 'Female Population: 75 to 79 years',
    'B01001_048E': 'Female Population: 80 to 84 years',
    'B01001_049E': 'Female Population: 85 years and over',

    'C01001A_002E': 'SEX BY AGE (WHITE ALONE) Male:',
    'C01001A_003E': 'SEX BY AGE (WHITE ALONE) Male:Under 18 years',
    'C01001A_004E': 'SEX BY AGE (WHITE ALONE) Male:18 to 64 years',
    'C01001A_005E': 'SEX BY AGE (WHITE ALONE) Male:65 years and over',
    'C01001A_006E': 'SEX BY AGE (WHITE ALONE) Female:',
    'C01001A_007E': 'SEX BY AGE (WHITE ALONE) Female:Under 18 years',
    'C01001A_008E': 'SEX BY AGE (WHITE ALONE) Female:18 to 64 years',
    'C01001A_009E': 'SEX BY AGE (WHITE ALONE) Female:65 years and over',
    'C01001B_002E': 'SEX BY AGE (BLACK OR AFRICAN AMERICAN ALONE) Male:',
    'C01001B_003E': 'SEX BY AGE (BLACK OR AFRICAN AMERICAN ALONE) Male:Under 18 years',
    'C01001B_004E': 'SEX BY AGE (BLACK OR AFRICAN AMERICAN ALONE) Male:18 to 64 years',
    'C01001B_005E': 'SEX BY AGE (BLACK OR AFRICAN AMERICAN ALONE) Male:65 years and over',
    'C01001B_006E': 'SEX BY AGE (BLACK OR AFRICAN AMERICAN ALONE) Female:',
    'C01001B_007E': 'SEX BY AGE (BLACK OR AFRICAN AMERICAN ALONE) Female:Under 18 years',
    'C01001B_008E': 'SEX BY AGE (BLACK OR AFRICAN AMERICAN ALONE) Female:18 to 64 years',
    'C01001B_009E': 'SEX BY AGE (BLACK OR AFRICAN AMERICAN ALONE) Female:65 years and over',
    'C01001C_002E': 'SEX BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE) Male:',
    'C01001C_003E': 'SEX BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE) Male: Under 18 years',
    'C01001C_004E': 'SEX BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE) Male: 18 to 64 years',
    'C01001C_005E': 'SEX BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE) Male: 65 years and over',
    'C01001C_006E': 'SEX BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE) Female:',
    'C01001C_007E': 'SEX BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE) Female:Under 18 years',
    'C01001C_008E': 'SEX BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE) Female:18 to 64 years',
    'C01001C_009E': 'SEX BY AGE (AMERICAN INDIAN AND ALASKA NATIVE ALONE) Female:65 years and over',
    'C01001D_002E': 'SEX BY AGE (ASIAN ALONE) Male:',
    'C01001D_003E': 'SEX BY AGE (ASIAN ALONE) Male: Under 18 years',
    'C01001D_004E': 'SEX BY AGE (ASIAN ALONE) Male: 18 to 64 years',
    'C01001D_005E': 'SEX BY AGE (ASIAN ALONE) Male: 65 years and over',
    'C01001D_006E': 'SEX BY AGE (ASIAN ALONE) Female:',
    'C01001D_007E': 'SEX BY AGE (ASIAN ALONE) Female: Under 18 years',
    'C01001D_008E': 'SEX BY AGE (ASIAN ALONE) Female: 18 to 64 years',
    'C01001D_009E': 'SEX BY AGE (ASIAN ALONE) Female: 65 years and over',
    'C01001E_002E': 'SEX BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE) Male:',
    'C01001E_003E': 'SEX BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE) Male: Under 18 years',
    'C01001E_004E': 'SEX BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE) Male: 18 to 64 years',
    'C01001E_005E': 'SEX BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE) Male: 65 years and over',
    'C01001E_006E': 'SEX BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE) Female:',
    'C01001E_007E': 'SEX BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE) Female: Under 18 years',
    'C01001E_008E': 'SEX BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE) Female: 18 to 64 years',
    'C01001E_009E': 'SEX BY AGE (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE) Female: 65 years and over',
    'C01001F_002E': 'SEX BY AGE (SOME OTHER RACE ALONE) Male:',
    'C01001F_003E': 'SEX BY AGE (SOME OTHER RACE ALONE) Male: Under 18 years',
    'C01001F_004E': 'SEX BY AGE (SOME OTHER RACE ALONE) Male: 18 to 64 years',
    'C01001F_005E': 'SEX BY AGE (SOME OTHER RACE ALONE) Male: 65 years and over',
    'C01001F_006E': 'SEX BY AGE (SOME OTHER RACE ALONE) Female:',
    'C01001F_007E': 'SEX BY AGE (SOME OTHER RACE ALONE) Female: Under 18 years',
    'C01001F_008E': 'SEX BY AGE (SOME OTHER RACE ALONE) Female: 18 to 64 years',
    'C01001F_009E': 'SEX BY AGE (SOME OTHER RACE ALONE) Female: 65 years and over',
    'C01001G_002E': 'SEX BY AGE (TWO OR MORE RACES) Male:',
    'C01001G_003E': 'SEX BY AGE (TWO OR MORE RACES) Male: Under 18 years',
    'C01001G_004E': 'SEX BY AGE (TWO OR MORE RACES) Male: 18 to 64 years',
    'C01001G_005E': 'SEX BY AGE (TWO OR MORE RACES) Male:65 years and over',
    'C01001G_006E': 'SEX BY AGE (TWO OR MORE RACES) Female:',
    'C01001G_007E': 'SEX BY AGE (TWO OR MORE RACES) Female: Under 18 years',
    'C01001G_008E': 'SEX BY AGE (TWO OR MORE RACES) Female: 18 to 64 years',
    'C01001G_009E': 'SEX BY AGE (TWO OR MORE RACES) Female: 65 years and over',
    'B06012_002E': 'Poverty: Below 100 percent of the poverty level',
    'B06012_003E': 'Poverty: 100 to 149 percent of the poverty level',
    'B06012_004E': 'Poverty: At or above 150 percent of the poverty level',
    'B09005_002E': 'Married-couple household',
    'B09005_003E': 'Cohabiting couple household',
    'B09005_004E': 'In male householder, no spouse/partner present household',
    'B09005_005E': 'In female householder, no spouse/partner present household',
    'C15002_003E': 'Education (Male): Less than 9th grade',
    'C15002_004E': 'Education (Male): 9th to 12th grade, no diploma',
    'C15002_005E': 'Education (Male): High school graduate (includes equivalency)',
    'C15002_006E': 'Education (Male): Some college, no degree',
    'C15002_007E': 'Education (Male): Associate\'s degree',
    'C15002_008E': 'Education (Male): Bachelor\'s degree',
    'C15002_009E': 'Education (Male): Graduate or professional degree',
    'C15002_011E': 'Education (Female): Less than 9th grade',
    'C15002_012E': 'Education (Female): 9th to 12th grade, no diploma',
    'C15002_013E': 'Education (Female): High school graduate (includes equivalency)',
    'C15002_014E': 'Education (Female): Some college, no degree',
    'C15002_015E': 'Education (Female): Associate\'s degree',
    'C15002_016E': 'Education (Female): Bachelor\'s degree',
    'C15002_017E': 'Education (Female): Graduate or professional degree',
    'B19001_002E': 'Income: Less than $10,000',
    'B19001_003E': 'Income: $10,000 to $14,999',
    'B19001_004E': 'Income: $15,000 to $19,999',
    'B19001_005E': 'Income: $20,000 to $24,999',
    'B19001_006E': 'Income: $25,000 to $29,999',
    'B19001_007E': 'Income: $30,000 to $34,999',
    'B19001_008E': 'Income: $35,000 to $39,999',
    'B19001_009E': 'Income: $40,000 to $44,999',
    'B19001_010E': 'Income: $45,000 to $49,999',
    'B19001_011E': 'Income: $50,000 to $59,999',
    'B19001_012E': 'Income: $60,000 to $74,999',
    'B19001_013E': 'Income: $75,000 to $99,999',
    'B19001_014E': 'Income: $100,000 to $124,999',
    'B19001_015E': 'Income: $125,000 to $149,999',
    'B19001_016E': 'Income: $150,000 to $199,999',
    'B19001_017E': 'Income: $200,000 or more',
}


def download_congressional_district_data(year: int = 2019,
                                         columns: Optional[Dict[str, str]] = None,
                                         units_subcounts: Optional[Dict[str, str]] = None,
                                         subpopulation_columns: Optional[Dict[str, str]] = None):
    """

    :param year:
    :param columns:
    :param units_subcounts:
    :param subpopulation_columns:
    :return:
    """
    if subpopulation_columns is None:
        subpopulation_columns = subpopulation_columns_labels
    if units_subcounts is None:
        units_subcounts = units_subcounts_labels
    if columns is None:
        columns = primary_columns

    columns = combine_dicts([columns, subpopulation_columns, units_subcounts])

    district_df = censusdata.download('acs1',
                                      year,
                                      censusdata.censusgeo([('congressional district', '*')]),
                                      list(columns.keys())
                                      )
    # Rename columns
    district_df = district_df.rename(columns=columns)
    # Rename rows
    district_df = district_df.rename(index={old: get_district_short_name(old) for old in district_df.index.values})
    # Adjust population and housing columns so they are proportionate measures
    district_df = divide_subset_columns(district_df,
                                        list(subpopulation_columns.values()),
                                        'Total Population')
    district_df = divide_subset_columns(district_df, list(units_subcounts.values()),
                                        'UNITS IN STRUCTURE:Total')

    cook_pvi = pd.read_csv('./data/congressional_district_cook.csv', index_col=0)
    district_df = pd.concat([district_df, cook_pvi], axis=1)
    return district_df


def load_congressional_district_data(filename: str) -> pd.DataFrame:
    """

    :param filename:
    :return:
    """
    try:
        district_df = pd.read_csv(filename, index_col=0)
    except FileNotFoundError:
        district_df = download_congressional_district_data()
        district_df.to_csv(filename)
    return district_df


demographics_filename = './data/demographics/2019-congressional-districts.csv'
congressional_district_demographics = load_congressional_district_data(demographics_filename)
