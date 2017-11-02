from instagram.client import InstagramAPI
import os, requests, shutil, unittest

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

def download(photo_urls):
	username = "dl_test"
	dl_dst = '../downloads/' + username
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
	dl_dst = '../downloads/dl_test'
	# makes .zip file with photos inside inside /zip_files/ directory
	shutil.make_archive('dl_test', 'zip', dl_dst)

	try:
		shutil.move('dl_test.zip', '../zip_files/dl_test.zip')
	except shutil.Error:
		os.remove('../zip_files/' + 'dl_test.zip')
		shutil.move('dl_test.zip', '../zip_files/dl_test.zip')
		pass

class TestDownload(unittest.TestCase):
	# test checks to see if download is in downloads folder; deletes folder afterwards
	def test_downloads(self):
		photos = get_self_recent_media()
		path = download(photos)
		is_file_in_path = os.path.isfile(path)
		shutil.rmtree('../downloads/dl_test/')
		self.assertTrue(is_file_in_path)

	# test checks to see if file zipped is in zip_files folder; deletes zip file afterwards
	def test_zip_files(self):
		photos = get_self_recent_media()
		download(photos)
		zip_files()
		zip_path = os.path.dirname(os.path.realpath(__file__)) + '/../zip_files/dl_test.zip'
		is_file_in_path = os.path.isfile(zip_path)
		shutil.rmtree('../downloads/dl_test/')
		os.remove(zip_path)
		self.assertTrue(is_file_in_path)

if __name__ == '__main__':
	unittest.main()