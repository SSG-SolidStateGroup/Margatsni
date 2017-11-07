from Margatsni import app
from instagram.client import InstagramAPI

from flask import Flask, request, render_template, session, redirect, send_file
import os, requests, shutil, json

LOGIN_URL = "https://www.instagram.com/accounts/login/ajax/"
# main page
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		session['login_user'] = request.form['username']
		session['login_pass'] = request.form['password']
		s = requests.Session()

		s.headers.update({'Referer': "https://www.instagram.com"})
		req = s.get("https://www.instagram.com")
		s.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

		login_data = {'username': session['login_user'], 'password': session['login_pass']}
		login = s.post(LOGIN_URL, data=login_data, allow_redirects=True)
		s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
		login_text = json.loads(login.text)
		if login_text.get('authenticated') and login.status_code == 200:
			return render_template('index2.html')
		else:
			return render_template('index.html')
	return render_template('login.html')

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
