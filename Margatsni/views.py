from Margatsni import app
from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect

instaConfig = {
	'client_id':'7aaf07aaa882491eb4c73bbdc94fa455',
	'client_secret':'67a95b790d714163bf039758690a9b60',
	'redirect_uri' : 'http://localhost:5000/instagram_callback',#'http://ec2-18-216-153-52.us-east-2.compute.amazonaws.com:80/instagram_callback'
}
api = InstagramAPI(**instaConfig)

@app.route('/')
def index():
	return render_template('index.html')

# Redirect users to Instagram for login
@app.route('/connect')
def connect():
	if 'instagram_access_token' in session and 'instagram_user' in session:
		return redirect('/')
	else:
		url = api.get_authorize_url(scope=["basic", "public_content", "follower_list"])
		return redirect(url)
# Instagram will redirect users back to this route after successfully logging in
@app.route('/instagram_callback', methods=['GET', 'POST'])
def instagram_callback():
	code = request.args.get('code')

	if code:
		access_token, user = api.exchange_code_for_access_token(code)
		if not access_token:
			return 'Could not get access token'
		
		# Sessions are used to keep this data 
		session['instagram_access_token'] = access_token
		session['instagram_user'] = user

		app.logger.debug(session['instagram_user'])

		return redirect('/') # redirect back to main page
	else:
		return "no code provided hnnnnnnnnnng"
