# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask import Flask, render_template, jsonify
from models import db_session
import json
import requests

from pprint import pprint



API_KEY = 'ToZQl1qWNAYdhWRtGKocMb4tG9vEQa7g'
MAPQUEST_URL = 'http://open.mapquestapi.com/directions/v2/route?key={appkey}'
MAPQUEST_TRAFFIC_URL='http://www.mapquestapi.com/traffic/v2/incidents?key={appkey}&inFormat=json&outFormat=json'

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



@app.route('/getdirections')
def get_route():

    ## get route information along with traffic information.

    ## TODO: add from user request.

    src = 'Boulder, CO'
    dest = 'Denver, CO'

    #result = "helo"

    request_body = {
        'locations': [
            src,
            dest
        ]
    }

    r = requests.post(MAPQUEST_URL.format(appkey=API_KEY),
                      data=json.dumps(request_body)
                      )
    if r.status_code != 200:
        # We didn't get a response from Mapquest
        print "error"

    result = json.loads(r.content)
    bounding_box = result['route']['boundingBox']
    #print pprint(result)

    traffic_info = get_traffic_info(bounding_box)

    #print pprint(traffic_info)


    return json.dumps(result)

def get_traffic_info(bounding_box):

    request_body_traffic = {'boundingBox':bounding_box, 'filters':["construction","incidents","congestion"]}

    r  = requests.post(MAPQUEST_TRAFFIC_URL.format(appkey=API_KEY),
                       data=json.dumps(request_body_traffic)
                       )
    result = json.loads(r.content)

    return jsonify(result=result)

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