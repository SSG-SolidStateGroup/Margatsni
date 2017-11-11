import os, shutil
from flask import Flask
from flask_apscheduler import APScheduler

class Config(object):
	JOBS = [
		{
			'id': 'wipe_dl_and_zip',
			'func': 'Margatsni:wipe_dl_and_zip',
			'args': (),
			'trigger': 'interval',
			'minutes': 1
		}
	]

	SCHEDULER_API_ENABLED = True

def wipe_dl_and_zip():
	file_path = os.path.dirname(os.path.realpath(__file__))
	dl_path = file_path + '/../downloads'
	zip_path = file_path + '/../zip_files'
	try:
		os.remove(dl_path)
		os.remove(zip_path)
		#os.mkdir(dl_path)
		#os.mkdir(zip_path)
	except Exception as e:
		print(e)

	print("cleared folders")

app = Flask(__name__)
app.config.from_object(Config())
app.secret_key = os.urandom(32)
scheduler = APScheduler()

import Margatsni.views