from instagram.client import InstagramAPI
import pytest
import os
import requests
import shutil

access_token = "1452718484.7aaf07a.512deb47397e4bffb6e18da65f11270e"
client_secret = "67a95b790d714163bf039758690a9b60"
client_id = "7aaf07aaa882491eb4c73bbdc94fa455"

api = InstagramAPI(access_token=access_token, client_secret=client_secret, client_id=client_id)

def get_self_recent_media():
	next_max = 3
	api = InstagramAPI(access_token=access_token)
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

	return photos

def return_file(photos = []):
	get_file = ''.join(('/zip_files/', download(photos)))
	dir_path = os.path.dirname(os.path.realpath(__file__))
	dir_path = ''.join((dir_path, '/..'))
	dir_path = ''.join((dir_path, get_file))
	fname = str(session['instagram_user']['username']) + '.zip'
	return send_file(filename_or_fp=dir_path, as_attachment=True, attachment_filename=fname)

def download(photo_urls):
	username = "dl_test"
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
	return file_path

def zip_files():
	# makes .zip file with photos inside inside /zip_files/ directory
	shutil.make_archive(username, 'zip', dl_dst)

	try:
		shutil.move(zip_fname, './zip_files/' + zip_fname)
	except shutil.Error:
		os.remove('./zip_files/' + zip_fname)
		shutil.move(zip_fname, './zip_files/' + zip_fname)
		pass

	return zip_fname

def download_test():
	photos = get_self_recent_media()
	path = download(photos)
	is_file_in_path = os.path.isfile(path)
	shutil.rmtree("./downloads/dl_test/")
	assert is_file_in_path
