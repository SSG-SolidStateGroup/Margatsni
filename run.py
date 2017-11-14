from Margatsni import app, scheduler

if __name__ == '__main__':
	import logging
	logging.basicConfig(filename='error.log',level=logging.DEBUG)
	scheduler.init_app(app)
	scheduler.start()
	app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=80)
	