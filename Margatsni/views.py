from Margatsni import app
from instagram.client import InstagramAPI
from instagram_scraper import InstagramScraper
from flask import Flask, request, render_template, session, redirect, flash, send_file
import os, requests, shutil, json, concurrent.futures

LOGIN_URL = "https://www.instagram.com/accounts/login/ajax/"
max_items = 20
api = InstagramScraper(login_user=None, login_pass=None, media_types=['image','carousel'], maximum=max_items)

# main page
@app.route('/')
def index():
	return render_template('index.html')

# log-in page, will detect invalid logins
@app.route('/login', methods=['GET', 'POST'])
def login():
	failed_login = False
	session['logged_in'] = False
	if request.method == 'POST':
		session['login_user'] = request.form['username']
		session['login_pass'] = request.form['password']
		login_text, login = validateUser()

		if login_text.get('authenticated') and login.status_code == 200:
			api.login_user = session['login_user']
			api.login_pass = session['login_pass']
			api.login()
			session['logged_in'] = True
			return redirect('/')
		else:
			flash('Unsuccessful login.')
	return render_template('login.html')

# validates if user and pass is a valid instagram account
def validateUser():
	s = requests.Session()
	s.headers.update({'Referer': "https://www.instagram.com"})
	req = s.get("https://www.instagram.com")
	s.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
	login_data = {'username': session['login_user'], 'password': session['login_pass']}
	login = s.post(LOGIN_URL, data=login_data, allow_redirects=True)
	s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
	return json.loads(login.text), login

@app.route('/get-target-media', methods=['GET', 'POST'])
def get_target_media():
	executor=concurrent.futures.ThreadPoolExecutor(max_workers=10)

	username = api.username = 'kellynieh'
	zip_fname = username + '.zip'
	api.posts = []
	api.last_scraped_filetime = 0
	future_to_item = {}

	dst = './downloads/' + username
	try:
		os.makedirs(dst)
	except FileExistsError:
		shutil.rmtree(dst)
		os.makedirs(dst)
		pass

	user_details = api.get_user_details(username)

	# Crawls the media and sends it to the executor.
	api.get_media(dst, executor, future_to_item, user_details)

	shutil.make_archive(username, 'zip', dst)

	try:
		shutil.move(zip_fname, './zip_files/' + zip_fname)
	except shutil.Error:
		os.remove('./zip_files/' + zip_fname)
		shutil.move(zip_fname, './zip_files/' + zip_fname)
		pass
	return send_file(filename_or_fp='../zip_files/'+zip_fname, as_attachment=True, attachment_filename=zip_fname)

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
