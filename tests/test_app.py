import pytest
import requests
from flask import url_for

from phonelocator.__main__ import get_phones_locations, parse_phones_request, \
    APIError, app as http_app


def test_parse_phones_request_maformed_json():
    with pytest.raises(APIError):
        parse_phones_request(None)


def test_parse_phones_request_no_phone_numbers_key():
    with pytest.raises(APIError):
        parse_phones_request({})


def test_parse_phones_request_bad_phone_numbers_value():
    with pytest.raises(APIError):
        parse_phones_request({'phone_numbers': ['1234567890', None]})


def test_get_phones_locations():
    res = get_phones_locations(['123456789', '9721234567', '999999999'])
    assert res == {'123456789': 'US,OH', '9721234567': 'IL', '999999999': None}


@pytest.fixture
def app():
    http_app.debug = True
    return http_app


@pytest.mark.integration
@pytest.mark.usefixtures('live_server')
class TestLiveServer(object):
    def test_get_location(self):
        resp = requests.post(
                url_for('get_location', _external=True),
                json={'phone_numbers': ['9721234567', '9999999']}
        )

        assert resp.status_code == 200
        resp = resp.json()

        assert 'results' in resp and len(resp) == 1
        assert resp['results'] == {'9721234567': 'IL', '9999999': None}

    def test_get_location_bad_input(self):
        resp = requests.post(
                url_for('get_location', _external=True),
                json={'bad_request': 123}
        )
        assert resp.status_code == 400

        resp = resp.json()
        assert resp['status_code'] == 400
        assert 'error' in resp
