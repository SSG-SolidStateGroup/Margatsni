from Margatsni import app
from instagram_scraper import InstagramScraper
from flask import Flask, request, render_template, session, redirect, flash, send_file
from bs4 import BeautifulSoup
import os, requests, shutil, json, concurrent.futures, tqdm, re

LOGIN_URL = "https://www.instagram.com/accounts/login/ajax/"
logged_in = False
api = InstagramScraper( media_types=['image','story', 'video'], maximum=100 )

'''------------------------------------------------------- page views ----------------------------------------------------'''

# main page
@app.route('/')
def index():
	return render_template('index.html')

# log-in page, will detect invalid logins
@app.route('/login', methods=['GET', 'POST'])
def login():
	session['logged_in'] = False
	if request.method == 'POST':
		session['login_user'] = request.form['username']
		session['login_pass'] = request.form['password']
		login_text, login = validateUser()

		if login_text.get('authenticated') and login.status_code == 200:
			api.login_user = session['login_user']
			api.login_pass = session['login_pass']
			api.login()
			global logged_in
			logged_in = True
			session['logged_in'] = True
			return redirect('/')
		else:
			flash('Unsuccessful login.')
	return render_template('login.html')

@app.route('/help')
def help():
	return render_template('help.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	global logged_in
	logged_in = False
	session['logged_in'] = False
	api.logout()
	return redirect('/')

# takes input from user as instagram user name, profile url, or user's photo url
# and retrieves image(s)/video(s) from given input
@app.route('/get-media', methods=['GET', 'POST'])
def get_media():
	try:
		global logged_in
		target = request.form['target']
		pieces = target.split('/')

		if 'p' in pieces:
			json_text = create_json_text(target)
			entry_data = json_text['entry_data']

			if entry_data:
				is_video = json_text['entry_data']['PostPage'][0]['graphql']['shortcode_media']['is_video']
				type_name = json_text['entry_data']['PostPage'][0]['graphql']['shortcode_media']['__typename']
			else:
				is_video = False
				type_name = None

			if not entry_data and not logged_in:
				flash('User is private. You will need to log in and follow this user to retrieve media.')
				return redirect('/')
			else:
				if is_video:
					file_path, base_name = get_video(target)
				elif type_name == "GraphSidecar":
					zip_fname = get_graph_sidecar(target)
					return send_file( filename_or_fp = '../zip_files/' + zip_fname,
								  as_attachment=True,
								  attachment_filename=zip_fname)
				else:
					file_path, base_name = get_single_photo(target)
				return send_file( filename_or_fp = '../' + file_path,
								  as_attachment=True,
				 				  attachment_filename=base_name )
	
		else:
			if '.com' not in target:
				json_text = create_json_text('https://www.instagram.com/' + target + '/')
			else:
				json_text = create_json_text(target)
	
			is_private = json_text['entry_data']['ProfilePage'][0]['user']['is_private']

			if is_private and not logged_in:
				flash('User is private. You will need to log in and follow this user to retrieve media.')
				return redirect('/')
			else:
				zip_fname = get_target_batch(target)
				return send_file( filename_or_fp = '../zip_files/' + zip_fname,
								  as_attachment=True,
								  attachment_filename=zip_fname)
		return redirect('/')
	except (KeyError, ValueError) as e:
		flash('Not a valid instagram user.')
		pass
		return redirect('/')
'''-------------------------------------------------------helper functions----------------------------------------------------'''
def validateUser():
	s = requests.Session()
	s.headers.update({'Referer': "https://www.instagram.com"})
	req = s.get("https://www.instagram.com")
	s.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
	login_data = {'username': session['login_user'], 'password': session['login_pass']}
	login = s.post(LOGIN_URL, data=login_data, allow_redirects=True)
	s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
	return json.loads(login.text), login

def get_video(target):
	json_text = create_json_text(target)
	url = json_text['entry_data']['PostPage'][0]['graphql']['shortcode_media']['video_url']

	dst = './downloads/single_videos'

	create_dir(dst)

	#saves all photos in directory made above
	base_name = url.split('/')[-1].split('?')[0]
	file_path = os.path.join(dst, base_name)
	r = requests.get(url)
	if not os.path.isfile(file_path):
		with open(file_path, 'wb') as media_file:
				try:
					content = r.content
				except requests.exceptions.ConnectionError:
					time.sleep(5)
					content = r.content
				media_file.write(content)

	return file_path, base_name

#retrieves carousel posts (posts with multiple images)
def get_graph_sidecar(target):
	img_urls = []
	json_text = create_json_text(target)
	sidecar = json_text['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
	owner = json_text['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['username'] + '_carousel'
	zip_fname = owner + '.zip'
	for edge in sidecar:
		img_urls.append(edge['node']['display_url'])

	dst = './downloads/' + owner
	create_dir(dst)

	for url in img_urls:
		base_name = url.split('/')[-1].split('?')[0]
		file_path = os.path.join(dst, base_name)
		r = requests.get(url)
		if not os.path.isfile(file_path):
			with open(file_path, 'wb') as media_file:
					try:
						content = r.content
					except requests.exceptions.ConnectionError:
						time.sleep(5)
						content = r.content
					media_file.write(content)

	create_zip(owner, zip_fname, dst)
	return zip_fname

# retrieves batch file of all of target's media
def get_target_batch(target):
	executor=concurrent.futures.ThreadPoolExecutor(max_workers=20)
	
	blacklist = ['https:', '', 'www.instagram.com']
	pieces = target.split('/')
	for p in pieces:
		if p not in blacklist:
			target = p
			break
	api.usernames = [target]
	zip_fname = target + '.zip'

	for username in api.usernames:
		api.posts = []
		api.last_scraped_filemtime = 0
		future_to_item = {}

		dst = './downloads/' + username
		create_dir(dst)

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
	
	create_zip(username, zip_fname, dst)
	return zip_fname

def get_single_photo(img_url):
	json_text = create_json_text(img_url)
	url = json_text['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_url']

	dst = './downloads/single_photos'

	create_dir(dst)

	#saves all photos in directory made above
	base_name = url.split('/')[-1].split('?')[0]
	file_path = os.path.join(dst, base_name)
	r = requests.get(url)
	if not os.path.isfile(file_path):
		with open(file_path, 'wb') as media_file:
				try:
					content = r.content
				except requests.exceptions.ConnectionError:
					time.sleep(5)
					content = r.content
				media_file.write(content)

	return file_path, base_name

#formats script portion of html to create json text
def create_json_text(url):
	pieces = url.split('/')
	if 'http:' not in pieces and 'https:' not in pieces:
		url = 'https://' + url

	r = api.session.get(url)
	soup = BeautifulSoup(r.text)
	script = soup.find('script', type=["text/javascript"], string=re.compile("window._sharedData"))
	temp = re.search(r'^\s*window._sharedData\s*=\s*({.*?})\s*;\s*$', script.string, flags=re.DOTALL | re.MULTILINE).group(1)
	json_text = json.loads(temp)
	return json_text

#creates a directory at 'dst' and replaces old one if already existing
def create_dir(dst):
	try:
		os.mkdir(dst)
	except FileExistsError:
		shutil.rmtree(dst)
		os.mkdir(dst)
		pass

#creates a zip file at dst and replaces old one if already existing
def create_zip(username, zip_fname, dst):
	shutil.make_archive(username, 'zip', dst)
	try:
		shutil.move(zip_fname, './zip_files/' + zip_fname)
	except shutil.Error:
		os.remove('./zip_files/' + zip_fname)
		shutil.move(zip_fname, './zip_files/' + zip_fname)
		pass