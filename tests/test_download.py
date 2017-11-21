from instagram_scraper import InstagramScraper
from bs4 import BeautifulSoup
import os, requests, shutil, json, concurrent.futures, tqdm, re, unittest

api = InstagramScraper( media_types=['image','carousel'], maximum=5 )

def get_single_photo(img_url):
	json_text = create_json_text(img_url)
	url = json_text['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_url']

	dst = os.path.dirname(os.path.realpath(__file__)) + '/dl_test/'

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

		dst = os.path.dirname(os.path.realpath(__file__)) + '/' + username + '/'
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
	
	create_zip(username, 'instagram.zip', dst)
	return zip_fname, dst

def create_json_text(url):
	pieces = url.split('/')
	if 'http:' not in pieces and 'https:' not in pieces:
		url = 'https://' + url

	r = api.session.get(url)
	soup = BeautifulSoup(r.text, "html.parser")
	script = soup.find('script', type=["text/javascript"], string=re.compile("window._sharedData"))
	temp = re.search(r'^\s*window._sharedData\s*=\s*({.*?})\s*;\s*$', script.string, flags=re.DOTALL | re.MULTILINE).group(1)
	json_text = json.loads(temp)
	return json_text

def create_dir(dst):
	try:
		os.mkdir(dst)
	except FileExistsError:
		shutil.rmtree(dst)
		os.mkdir(dst)
		pass

def create_zip(username, zip_fname, dst):
	shutil.make_archive(username, 'zip', dst)
	'''try:
		shutil.move(zip_fname, './zip_files/' + zip_fname)
	except shutil.Error:
		os.remove('//zip_files/' + zip_fname)
		shutil.move(zip_fname, './zip_files/' + zip_fname)
		pass'''

class TestDownload(unittest.TestCase):
	# test checks single downloads
	def test_get_single_photo(self):
		target = 'https://www.instagram.com/p/BbDB730DcY8/?taken-by=instagram'
		file_path, base_name = get_single_photo(target)
		is_file_in_path = os.path.isfile(file_path)
		self.assertTrue(is_file_in_path)

	# test checks batch downloads with 'username'
	def test_get_batch_user(self):
		target = 'instagram'
		zip_fname, dl_dst = get_target_batch(target)
		zip_path= os.path.dirname(os.path.realpath(__file__)) + './instagram.zip'
		is_file_in_path = os.path.isfile(zip_path)
		self.assertTrue(is_file_in_path)

	# test checks batch downloads with target link
	def test_get_batch_user_link(self):
		target = 'https://www.instagram.com/instagram/'
		zip_fname, dl_dst = get_target_batch(target)
		zip_path = os.path.dirname(os.path.realpath(__file__)) + './instagram.zip'
		is_file_in_path = os.path.isfile(zip_path)	
		self.assertTrue(is_file_in_path)

if __name__ == '__main__':
	unittest.main()
