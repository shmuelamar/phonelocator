#!/usr/bin/env python
import httplib
import logging
from collections import OrderedDict
from flask import Flask, request, jsonify
from phonelocator import locator, settings

logger = logging.getLogger('phonelocator.app')
app = Flask(__name__)


class APIError(Exception):
    def __init__(self, msg, status_code=httplib.BAD_REQUEST):
        self.msg = msg
        self.status_code = status_code

    def __repr__(self):
        return '%s(%s, %d)' % (
            self.__class__.__name__, self.msg, self.status_code
        )

    def to_dict(self):
        return {'error': '%s' % self.msg, 'status_code': self.status_code}


def parse_phones_request(json_request):
    """parses location request into phone numbers

    :param dict json_request: the request object
    :return: the phones from the request
    :raises: APIError on bad request
    """
    if not isinstance(json_request, dict):
        raise APIError('not a json request')
    try:
        phones = json_request['phone_numbers']
    except KeyError:
        raise APIError('missing phone_numbers key from request')

    if not isinstance(phones, list) or \
            not all(isinstance(phone, basestring) for phone in phones):
        raise APIError('bad value in phone_numbers, must be list of strings')
    return phones


def get_phones_locations(phones):
    phone_locations = OrderedDict()

    for phone in phones:
        location = locator.locate_phone(phone)
        if location:
            phone_locations[phone] = ','.join(location)
        else:
            phone_locations[phone] = None

    return phone_locations


@app.route('/get_location', methods=['POST'])
def get_location():
    """API for retrieving the location of phone numbers.

    **Required Parameters:**
        - phone_numbers (list): list of phone numbers (strings) to resolve

    **Returns:**
        - results (dict): mapping of phone => location

    :status 400: Bad Request

    **Example:**

        .. code-block:: json
           :caption: **Request**

           {
                "phone_numbers": ["123456789", "9721234567", "999999999"]
           }

        .. code-block:: json
           :caption: **Response**
           {
                "results": {
                    "123456789": "US,OH",
                    "9721234567": "IL",
                    "9999999999": null
                }
           }
    """
    phones = parse_phones_request(request.json)
    phone2location = get_phones_locations(phones)

    return jsonify({'results': phone2location})


@app.errorhandler(APIError)
def handle_api_error(error):
    logger.info('APIError: %r', error)
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run(debug=settings.DEBUG)
