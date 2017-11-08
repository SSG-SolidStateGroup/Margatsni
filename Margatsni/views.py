from Margatsni import app
from instagram.client import InstagramAPI
from instagram_scraper import InstagramScraper
from flask import Flask, request, render_template, session, redirect, flash, send_file
import os, requests, shutil, json, concurrent.futures, tqdm

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
	executor=concurrent.futures.ThreadPoolExecutor(max_workers=20)

	target = request.form['target']
	api.usernames = [target]
	app.logger.debug(api.usernames)
	zip_fname = target + '.zip'
	
	if api.login_user and api.login_pass:
			api.login()
			if not api.logged_in and api.login_only:
				api.logger.warning('Fallback anonymous scraping disabled')
				return

	for username in api.usernames:
		api.posts = []
		api.last_scraped_filemtime = 0
		future_to_item = {}

		dst = './downloads/' + username
		try:
			os.makedirs(dst)
		except FileExistsError:
			shutil.rmtree(dst)
			os.makedirs(dst)
			pass

		# Get the user metadata.
		user = api.fetch_user(username)

		# Crawls the media and sends it to the executor.
		user_details = api.get_user_details(username)
		api.get_media(dst, executor, future_to_item, user_details)

		# Displays the progress bar of completed downloads. Might not even pop up if all media is downloaded while
		# the above loop finishes.
		if future_to_item:
			for future in tqdm.tqdm(concurrent.futures.as_completed(future_to_item), total=len(future_to_item), desc='Downloading', disable=api.quiet):
				item = future_to_item[future]

				if future.exception() is not None:
					api.logger.warning('Media at {0} generated an exception: {1}'.format(item['urls'], future.exception()))

		if (api.media_metadata or api.comments or api.include_location) and api.posts:
			api.save_json(api.posts, '{0}/{1}.json'.format(dst, username))

	api.logout()

	shutil.make_archive(username, 'zip', dst)

	try:
		shutil.move(zip_fname, './zip_files/' + zip_fname)
	except shutil.Error:
		os.remove('./zip_files/' + zip_fname)
		shutil.move(zip_fname, './zip_files/' + zip_fname)
		pass
	return send_file(filename_or_fp='../zip_files/'+zip_fname, as_attachment=True, attachment_filename=zip_fname)