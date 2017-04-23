# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask import Flask, render_template, jsonify
from models import db_session
import json
import requests
import urllib2


from pprint import pprint

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/box/city?bbox={lat1},{long1},{lat2},{long2},{zoom}&appid={appkey}'
WEATHER_API_KEY = '2feb61047e2d1f0763874018ff395415'
API_KEY = 'ToZQl1qWNAYdhWRtGKocMb4tG9vEQa7g'
MAPQUEST_URL = 'http://open.mapquestapi.com/directions/v2/route?key={appkey}'
MAPQUEST_TRAFFIC_URL='http://www.mapquestapi.com/traffic/v2/incidents?key={appkey}&inFormat=json&outFormat=json'
MAPQUEST_SEARCH_URL='http://www.mapquestapi.com/search/v2/radius?key={appkey}&inFormat=json&outFormat=json'
MAPQUEST_GEOCODE_URL='http://www.mapquestapi.com/geocoding/v1/address?key=KEY'

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')


# Automatically tear down SQLAlchemy.
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('/layouts/main.html')

'''
@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')
    '''


def get_weather_conditions(bounding_box):

    lat1 = bounding_box['ul']['lat']
    long1 = bounding_box['ul']['lng']
    lat2 = bounding_box['lr']['lat']
    long2 = bounding_box['lr']['lng']

    url_temp = WEATHER_URL.format(lat1=long2, long1=lat1,lat2=long1, long2=lat2,zoom='10', appkey=WEATHER_API_KEY)
    f = requests.get(url_temp)
    if f.status_code !=200:
        print "error while fetching weather conditions."
    json_parse = f.text
    return {'weather':json_parse}



@app.route('/searchRoute/<addr>')
def get_search_results(addr):

    geocode_request_body ={
                            "location": addr,
                            "options": {
                                "thumbMaps": "false"
                            }
                        }

    r = requests.post(MAPQUEST_SEARCH_URL.format(appkey=API_KEY),
                      data=json.dumps(geocode_request_body)
                      )
    if r.status_code != 200:
        # We didn't get a response from Mapquest
        print "error"

    geocode_result = json.loads(r.content)
    lat_lng = geocode_result['origin']['latLng']


    request_body = {
                    "origin": {
                        "latLng": lat_lng
                    },
                    "options": {
                        "maxMatches": 15,
                        "radius": 10
                    }

                }

    r = requests.post(MAPQUEST_SEARCH_URL.format(appkey=API_KEY),
                      data=json.dumps(request_body)
                      )
    if r.status_code != 200:
        # We didn't get a response from Mapquest
        print "error"

    result = json.loads(r.content)

    if "searchResults" in result:
        search_results = result['searchResults']
    else:
        search_results = "No results found."

    return search_results


@app.route('/getDirections/<src>/<dest>')
def get_route(src, dest):

    ## get route information along with traffic information.

    ## TODO: add from user request.


    request_body = {
        'locations': [
            src,
            dest
        ],
       "options": {
            'avoids': ['Toll Road','Ferry','Approximate Seasonal Closure','Limited Access'],
            'disallows':['Toll Road','Ferry','Approximate Seasonal Closure','Limited Access'],
            'avoidTimedConditions': 'false',
            'doReverseGeocode': 'true',
            'shapeFormat': 'raw',
            'generalize': 0,
            'routeType': 'fastest',
            'timeType': 1,
            'locale': 'en_US',
            'unit': 'm',
            'enhancedNarrative': 'false',
            'drivingStyle':2,
            'highwayEfficiency': 21.0,
            'roadGradeStrategy': 'FAVOR_ALL_HILLS'
        }
    }

    r = requests.post(MAPQUEST_URL.format(appkey=API_KEY),
                      data=json.dumps(request_body)
                      )
    if r.status_code != 200:
        # We didn't get a response from Mapquest
        print "error"

    result = json.loads(r.content)

    narrative_list, lat_long_list = get_lat_long_route(result)
    bounding_box = result['route']['boundingBox']

    weather_conditions = get_weather_conditions(bounding_box)

    traffic_info = get_traffic_info(bounding_box)

    final_result = {'narratives': narrative_list,'lat_long':lat_long_list,'traffic':traffic_info,'weather':weather_conditions}
    return json.dumps(result)

# result['route']['legs'][0]['maneuvers']
def get_lat_long_route(result):

    narrative_list = []
    lat_long_list = []
    directions = result['route']['legs'][0]['maneuvers']
    dir_len = len(directions)

    for i in range(dir_len):
        narrative_list.append(str(result['route']['legs'][0]['maneuvers'][i]['narrative']))
        lat_long_list.append(result['route']['legs'][0]['maneuvers'][i]['startPoint'])

    return narrative_list, lat_long_list

def get_traffic_info(bounding_box):

    request_body_traffic = {'boundingBox':bounding_box, 'filters':["construction","incidents","congestion"]}

    r  = requests.post(MAPQUEST_TRAFFIC_URL.format(appkey=API_KEY),
                       data=json.dumps(request_body_traffic)
                       )
    result = json.loads(r.content)

    return result

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


"""
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')
"""
# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port)
'''