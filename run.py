from Margatsni import app, scheduler

if __name__ == '__main__':
	#import logging
	#logging.basicConfig(filename='error.log',level=logging.DEBUG)
	#app.run(host='0.0.0.0', port=80)
	scheduler.init_app(app)
	scheduler.start()
	app.run(debug=True)