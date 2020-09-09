from app import app
import urllib3, json
from app.config.Config import Config as config_app
from app.decorators.ProcessResponse import process_response as _


def validate(email):
    response = False
    try:
        http = urllib3.PoolManager()
        params = {
            'secret': config_app().data['service_email_validate_secret'],
            'email': email
        }
        r = http.request('GET', config_app().data['service_email_validate_baseurl'], None, params)
        payload = json.loads(r.data.decode('utf-8'))
        if payload['valid'] is not None:
            response = payload['valid']
    except Exception as e:
        _(500, str(e))
        response = None
        pass
    return response
