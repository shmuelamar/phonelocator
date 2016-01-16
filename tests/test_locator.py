import pytest
from phonelocator import locator


@pytest.fixture(scope='function')
def countries():
    return {
        u'US': u'1', u'UG': u'256', u'IL': u'972', u'TZ': u'255',
        u'TW': u'886', u'AU': u'61',
    }


@pytest.fixture(scope='function')
def states():
    return {
       u'US': {
           u'WY': [u'307'],
           u'WV': [u'304', u'681'],
           u'WI': [u'262', u'274', u'414', u'534', u'608', u'715', u'920'],
           u'WA': [u'206', u'253', u'360', u'425', u'509', u'564'],
           u'NY': [u'212'],
        },
       u'AU': {
           u'WA': [u'85', u'86', u'89'],
           u'VIC': [u'33', u'34', u'35'],
           u'TAS': [u'36'],
        }
    }


def test_get_phone_prefixes_from_default_files_smoke():
    phone_prefixes = locator.get_phone_prefixes()
    assert isinstance(phone_prefixes.prefixes, dict)
    assert isinstance(phone_prefixes.prefix_lengths, list)


def test_get_phone_prefixes(countries, states):
    phone_prefixes = locator.get_phone_prefixes(countries, states)

    assert len(phone_prefixes.prefixes) == 28
    assert phone_prefixes.prefixes[u'972'] == [u'IL']
    assert phone_prefixes.prefixes[u'1212'] == [u'US', u'NY']
    assert u'1' not in phone_prefixes.prefixes
    assert u'61' not in phone_prefixes.prefixes


def test_get_phone_prefixes_bad_file(states):
    with pytest.raises(ValueError):
        locator.get_phone_prefixes(countries={}, states=states)


@pytest.mark.parametrize('phone_no,expected', [
    (u'9721234567890', [u'IL']),
    (u'1212345678902', [u'US', u'NY']),
    (u'9999999999999', None),
])
def test_locate_phone(phone_no, expected, countries, states):
    phone_prefixes = locator.get_phone_prefixes(countries, states)
    assert locator.locate_phone(phone_no, phone_prefixes) == expected
