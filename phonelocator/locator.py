import logging
import json
from collections import namedtuple
from phonelocator import settings

PhonePrefixes = namedtuple('PhonePrefixes', ['prefixes', 'prefix_lengths'])

logger = logging.getLogger('phonelocator.locator')


def load_json_file(fname):
    with open(fname) as fp:
        return json.load(fp)


def get_phone_prefixes(countries=None, states=None):
    """takes a `countries` and `states` files or uses the default files to
    build phone prefixes to country code mapping.
    When the same phone prefix has both country and state codes - the state
    code is preferred and the country code is ignored (e.g. all phone numbers
    starting with 1 must be valid number in the U.S. or ignored)

    :param dict countries:
    :param dict states:
    :return: PhonePrefixes object containing the prefixes and prefixes_lengths
      for fast lookup
    :rtype: PhonePrefixes
    """
    if countries is None:
        countries = load_json_file(settings.DEFAULT_COUNTRIES_FILE)
    if states is None:
        states = load_json_file(settings.DEFAULT_STATES_FILE)

    prefixes = {}
    reserved_prefixes = []

    for country, country_states in states.iteritems():
        try:
            country_prefix = countries[country]
        except KeyError:
            raise ValueError('bad country, state files - %s in states '
                             'but not in countries' % country)
        reserved_prefixes.append(country_prefix)
        for state, country_state_prefixes in country_states.iteritems():
            for state_prefix in country_state_prefixes:
                prefix = '%s%s' % (country_prefix, state_prefix)
                prefixes[prefix] = [country, state]

    for country, prefix in countries.iteritems():
        if any(prefix.startswith(reserved) for reserved in reserved_prefixes):
            logger.debug(
                    'ignoring country %s and prefix %s - startswith country '
                    'state code but not a country-state', country, prefix
            )
        else:
            prefixes[prefix] = [country]

    unique_lens = {len(prefix) for prefix in prefixes}
    prefix_lengths = sorted(unique_lens)

    return PhonePrefixes(prefixes, prefix_lengths)


def locate_phone(phone, phone_prefixes=None):
    """resolves phone prefix to country and state code.

    :param str|unicode phone: the phone number to get the prefix for
    :param phone_prefixes: a `PhonePrefixes` object containing the prefixes
      values. if not specified using the default one loaded from default files.
    :return: list of [country-code] or [country-code, state-code] or None
      if phone lookup failed
    :rtype: list|None
    """
    if phone_prefixes is None:
        phone_prefixes = PHONE_PREFIXES

    for length in phone_prefixes.prefix_lengths:
        prefix = phone[:length]
        if phone[:length] in phone_prefixes.prefixes:
            return phone_prefixes.prefixes[prefix]
    return None

PHONE_PREFIXES = get_phone_prefixes()
