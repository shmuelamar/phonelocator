from os.path import dirname, abspath, join as pathjoin

here = abspath(dirname(__file__))
DEFAULT_STATES_FILE = pathjoin(here, 'states.json')
DEFAULT_COUNTRIES_FILE = pathjoin(here, 'countries.json')
DEBUG = False
