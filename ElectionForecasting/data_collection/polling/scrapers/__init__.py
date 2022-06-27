from .fivethirtyeight.scraper import FiveThirtyEightScraper
from .realclearpolitics.realclearpolitics import RealClearPoliticsScraper
from .AbstractScraper import AbstractScraper

# Since AbstractScraper is a template class, we want to have access to ALL scrapers
# We do this by getting every registered subclass of AbstractScraper and putting them in a list.
# We make sure to ignore AbstractScraper itself, since it cannot be instantiated.

SCRAPERS = [c for c in AbstractScraper.get_registry().values() if c._registry_name != AbstractScraper._registry_name]