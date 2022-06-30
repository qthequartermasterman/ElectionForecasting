from typing import Dict

import pandas as pd

from ..cookpvi.CookPviScraper import cook_pvi_data


class DistrictSimilarity:
    """Get the most similar districts for estimation purposes."""

    def __init__(self):
        self.raw_pvi: pd.Series = cook_pvi_data['New PVI Raw'].sort_values()  # Sorted districts by PVI values

    def get_similar_districts(self, district: str, count: int = 5) -> Dict[str, float]:
        """
        Return a dict of district labels and their similarity metric
        :param count: number of districts to find
        :param district: district label of the input district
        :return:
        """
        distances: pd.Series = abs(self.raw_pvi - self.raw_pvi[district])
        return dict(distances.nsmallest(count).to_dict())
