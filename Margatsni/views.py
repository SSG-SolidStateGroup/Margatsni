from Margatsni import app
from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect, send_file
import os, requests, shutil

# Only temporary, later will need to add OS variables to hide config data
CONFIG = {
	'client_id':'7aaf07aaa882491eb4c73bbdc94fa455',
	'client_secret':'67a95b790d714163bf039758690a9b60',
	'redirect_uri' : 'http://margatsni.xyz:80/instagram_callback'
	#	'http://ec2-18-216-153-52.us-east-2.compute.amazonaws.com:80/instagram_callback'
	#	'http://margatsni.xyz:80/instagram_callback'
	#	'redirect_uri' : 'http://localhost:5000/instagram_callback'
}

api = InstagramAPI(**CONFIG)

# main page
@app.route('/')
def index():
	return render_template('index.html')

# Redirect users to Instagram for login to retrieve code for access_token
@app.route('/connect')
def connect():
	url = api.get_authorize_url(scope=["basic", "public_content", "follower_list"])
	return redirect(url)

# Instagram will redirect users back to this route after successfully logging in
@app.route('/instagram_callback')
def instagram_callback():
	code = request.args.get('code')

	if code:
		access_token, user = api.exchange_code_for_access_token(code)
		if not access_token:
			return 'Could not get access token'

		# Sessions are used to keep this data
		session['instagram_access_token'] = access_token
		session['instagram_user'] = user

		app.logger.debug(session['instagram_access_token'])

		return redirect('/') # redirect back to main page
	else:
		return "no code provided hnnnnnnnnnng"

@app.route('/get-user-media', methods=['GET', 'POST'])
def get_self_recent_media():
	next_max = 3
	api = InstagramAPI(access_token=session['instagram_access_token'])
	user_media_feed, next = api.user_media_feed()

	photos = []
	for media in user_media_feed:
		photos.append(media.get_standard_resolution_url())

	counter = 1
	while next and counter < next_max:
		user_media_feed, next = api.user_media_feed(with_next_url=next)
		for media in user_media_feed:
			photos.append(media.get_standard_resolution_url())
		counter += 1

	get_file = ''.join(('/zip_files/', download(photos)))
	dir_path = os.path.dirname(os.path.realpath(__file__))
	dir_path = ''.join((dir_path, '/..'))
	dir_path = ''.join((dir_path, get_file))
	fname = str(session['instagram_user']['username']) + '.zip'
	return send_file(filename_or_fp=dir_path, as_attachment=True, attachment_filename=fname)

def download(photo_urls):
	username = str(session['instagram_user']['username'])
	dl_dst = './downloads/' + username
	zip_fname = username + '.zip'

	# if directory exists, it overwrites the old directory
	try:
		os.makedirs(dl_dst)
	except FileExistsError:
		shutil.rmtree(dl_dst)
		os.makedirs(dl_dst)
		pass

	#saves all photos in directory made above ^^^
	for url in photo_urls:
		base_name = url.split('/')[-1].split('?')[0]
		file_path = os.path.join(dl_dst, base_name)

		r = requests.get(url)

		if not os.path.isfile(file_path):
			with open(file_path, 'wb') as media_file:
					try:
						content = r.content
					except requests.exceptions.ConnectionError:
						time.sleep(5)
						content = r.content

					media_file.write(content)

	#zips downloads and moves them to zip_files directory
	shutil.make_archive(username, 'zip', dl_dst)

	try:
		shutil.move(zip_fname, './zip_files/' + zip_fname)
	except shutil.Error:
		os.remove('./zip_files/' + zip_fname)
		shutil.move(zip_fname, './zip_files/' + zip_fname)
		pass

	return zip_fname
