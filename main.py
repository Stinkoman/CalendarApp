import os
import flask
import sys
import uuid

sys.path.insert(0,os.getcwd())
import config
from flask_oauthlib.client import OAuth

app = flask.Flask(__name__, template_folder='templates')
app.debug= True
app.secret_key = 'development'
OAUTH = OAuth(app)
MSGRAPH = OAUTH.remote_app(
        'microsoft', consumer_key=config.CLIENT_ID, consumer_secret = config.CLIENT_SECRET,
        request_token_params={'scope': config.SCOPES},
        base_url=config.RESOURCE + config.API_VERSION + '/',
        request_token_url=None, access_token_method='POST',
        access_token_url=config.AUTHORITY_URL+ config.TOKEN_ENDPOINT,
        authorize_url=config.AUTHORITY_URL + config.AUTH_ENDPOINT)


@app.route('/BFWA/CommunityRoomA')
def hello():
    webpage = "Haro, Navi.<br><br>"
    for scope in config.SCOPES:
        webpage += scope
        webpage + "<br>"
    return webpage

@app.route('/login')
def login():
    """Prompt user to authenticate."""
    flask.session['state'] = str(uuid.uuid4())
    return MSGRAPH.authorize(callback=config.REDIRECT_URL, state=flask.session['state'])

@app.route('/login/authorized')
def authorized():
    """Handler for the application's Redirect Uri."""
    if str(flask.session['state']) != str(flask.request.args['state']):
        raise Exception('state returned to redirect URL does not match!')
    response = MSGRAPH.authorized_response()
    flask.session['access_token'] = response['access_token']
    return flask.redirect('/graphcall')

@app.route('/graphcall')
def graphcall():
    """Confirm user authentication by calling Graph and displaying some data."""
    endpoint = 'me'
    headers = {'SdkVersion': 'sample-python-flask',
               'x-client-SKU': 'sample-python-flask',
               'client-request-id': str(uuid.uuid4()),
               'return-client-request-id': 'true'}
    graphdata = MSGRAPH.get(endpoint, headers=headers).data
    return flask.render_template('graphcall.html',
                                 graphdata=graphdata,
                                 endpoint=config.RESOURCE + config.API_VERSION + '/' + endpoint,
                                 sample='Flask-OAuthlib')

@MSGRAPH.tokengetter
def get_token():
    """Called by flask_oauthlib.client to retrieve current access token."""
    return (flask.session.get('access_token'), '')

if __name__ == '__main__':
    app.run()
