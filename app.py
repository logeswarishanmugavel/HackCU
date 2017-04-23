# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask import Flask, render_template, jsonify, request
from models import db_session, UserInfo, FriendsList, RouteInfo, UserRouteInfo, UserInfoSchema, FriendsListSchema, RouteInfoSchema, UserRouteInfoSchema
import json
import requests
import datetime
from pprint import pprint
from urllib import unquote_plus

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/box/city?bbox={lat1},{long1},{lat2},{long2},{zoom}&appid={appkey}'
WEATHER_API_KEY = '2feb61047e2d1f0763874018ff395415'
API_KEY = 'ToZQl1qWNAYdhWRtGKocMb4tG9vEQa7g'
MAPQUEST_URL = 'http://open.mapquestapi.com/directions/v2/route?key={appkey}'
MAPQUEST_TRAFFIC_URL='http://www.mapquestapi.com/traffic/v2/incidents?key={appkey}&inFormat=json&outFormat=json'
MAPQUEST_SEARCH_URL='http://www.mapquestapi.com/search/v2/radius?key={appkey}&inFormat=json&outFormat=json'
MAPQUEST_GEOCODE_URL='http://www.mapquestapi.com/geocoding/v1/address?key=KEY'

ATTRACTIVE_SIC_CODES = [999333,902209,903005,901027,901006,901010,901014,901023,842201,841206,829950,806202,806203,809916,
                       799954,799940,799729,799701,735922,703301,703208,702103,701107,701106,581228,554101,541103,541101
                        ,472401,411906,411902,97106,19101]
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


@app.route('/adduser', methods=['POST'])
def adduser():
    user_info = json.loads(request.data)
    uis = UserInfoSchema()
    try:
        ui = uis.load(user_info, session=db_session, partial=True).data
        db_session.add(ui)
    except ValueError:
        return "a data format exception occurred"
    db_session.commit()
    return "User Added"


@app.route('/addfriends/<user_id>', methods=['POST'])
def addfriends(user_id):
    friends_ids = [x.strip() for x in request.data.split(',')]
    fls = FriendsListSchema()
    friend_info = {'user_id': '', 'friend_id': ''}
    for friend_id in friends_ids:
        try:
            fl = fls.load(friend_info, session=db_session, partial=True).data
            fl.user_id = int(user_id)
            fl.friend_id = int(friend_id)
            db_session.add(fl)
        except ValueError:
            print "a data format exception occurred"
    db_session.commit()


@app.route('/addrouteinfo', methods=['POST'])
def addrouteinfo():
    route_info = json.loads(request.data)
    ris = RouteInfoSchema()
    try:
        ri = ris.load(route_info, session=db_session, partial=True).data
        db_session.add(ri)
    except ValueError:
        print "a data format exception occurred"
    db_session.commit()
    return "route info added"


@app.route('/adduserrouteinfo', methods=['POST'])
def adduserrouteinfo():
    user_route_info = json.loads(request.data)
    uris = UserRouteInfoSchema()
    try:
        user_route_info['trip_date'] = datetime.datetime.strptime(user_route_info['trip_date'], "%m/%d/%y").isoformat()
        uri = uris.load(user_route_info, session=db_session, partial=True).data
        uri.user_id = user_route_info['user_id']
        uri.route_id = user_route_info['route_id']
        db_session.add(uri)
    except ValueError:
        print "a data format exception occurred"
    db_session.commit()


@app.route('/getuserinfo/<user_id>')
def getuserinfo(user_id):
    result = UserInfo().query.filter(UserInfo.user_id == user_id).first()
    ui_json = UserInfoSchema().dump(result).data
    return jsonify(result=ui_json)

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
    src = unquote_plus(src)
    dest = unquote_plus(dest)
    sic_code = 13901
    nearby_attractions_search = []

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

    for ll in lat_long_list:
        request_body_temp = {
            "origin": {
                "latLng": ll
            },
            "options": {
                "radius": 20,
                "maxMatches": 10,
                "units": "m"
            }
        }
        r_poi = requests.post(MAPQUEST_SEARCH_URL.format(appkey=API_KEY), data=json.dumps(request_body_temp))
        search_result = json.loads(r_poi.content)
        search_length = len(search_result['searchResults'])
        for i in range(search_length):
            try:
                sic_code = int(search_result['searchResults'][0]['fields']['group_sic_code'])
            except ValueError:
                sic_code = 13901

            if sic_code in ATTRACTIVE_SIC_CODES:
                nearby_attractions_search.append(search_result['searchResults'][i])

    final_result = {'boundingBox': bounding_box, 'narratives': narrative_list, 'lat_long': lat_long_list, 'traffic': traffic_info, 'weather': weather_conditions,'nearbyAttractions':nearby_attractions_search}
    return json.dumps(final_result)

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''