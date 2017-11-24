from app import application, scheduler

if __name__ == '__main__':
	import logging
	logging.basicConfig(filename='error.log',level=logging.DEBUG)
	scheduler.init_app(application)
	scheduler.start()
	application.run(host='0.0.0.0', port=80)
	#application.run(debug=True)