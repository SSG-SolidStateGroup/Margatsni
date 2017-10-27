import os
from flask import Flask,redirect,url_for,render_template

app = Flask(__name__)

'''
@app.route('/')
def hello():
    return redirect(url_for('static', filename='index.html'))
'''

#below is for testing
@app.route('/')
def test():
    return "Hello World!"

@app.route('/test2')
def test2():
    return "Next page"

#this is for static redirecting
@app.route('/index.html') #both redirect to hello()
@app.route('/website')
def hello():
    return redirect(url_for('static', filename='index.html'))

#this is for dynamic redirecting
@app.route('/instagram')
def hello2():
    return redirect("https://www.instagram.com/", code=302)

def returning(): 
    return 302

#end test

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
