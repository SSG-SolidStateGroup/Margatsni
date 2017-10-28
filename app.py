from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

app = Flask(__name__)
app.secret_key = "SUPER SECRET KEY"

# System variables found on server's computer
instaConfig = {
	'client_id':'7aaf07aaa882491eb4c73bbdc94fa455',
	'client_secret':'67a95b790d714163bf039758690a9b60',
	'redirect_uri' : 'http://localhost:5000/instagram_callback'
}
api = InstagramAPI(**instaConfig)

@app.route('/')
def user_photos():
	if 'instagram_access_token' in session and 'instagram_user' in session:
		return "HELLO"
	else:
		return redirect('/connect')

# Redirect users to Instagram for login
@app.route('/connect')
def connect():
	url = api.get_authorize_url(scope=["basic", "public_content", "follower_list"])
	return redirect(url)

# Instagram will redirect users back to this route after successfully logging in
@app.route('/instagram_callback', methods=['GET', 'POST'])
def instagram_callback():
	code = request.args.get('code')
	app.logger.debug("HELLOOO HOLY SHIT")
	if code:
		access_token, user = api.exchange_code_for_access_token(code)
		if not access_token:
			return 'Could not get access token'
		
		app.logger.debug('got an access token')
		app.logger.debug(access_token)

		# Sessions are used to keep this data 
		session['instagram_access_token'] = access_token
		session['instagram_user'] = user

		return redirect('/') # redirect back to main page
	else:
		return "Uhoh no code provided"

if __name__ == "__main__":
	app.run(port=80, debug=True)

'''
access_token = "1452718484.7aaf07a.512deb47397e4bffb6e18da65f11270e"
client_secret = "67a95b790d714163bf039758690a9b60"
client_id = "7aaf07aaa882491eb4c73bbdc94fa455"
redirect_uri = "http://google.com"

instaConfig = {
	'client_id':os.environ.get('CLIENT_ID'),
	'client_secret':os.environ.get('CLIENT_SECRET'),
	'redirect_uri' : os.environ.get('REDIRECT_URI')
}
'''