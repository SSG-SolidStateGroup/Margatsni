from flask import *
from flask_sqlalchemy import *
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from flask_bootstrap import Bootstrap 

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class students(db.Model):
	id = db.Column('student_id', db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	pin = db.Column(db.String(10))

	def __init__(self, name, pin):
		self.name = name
		self.pin = pin

@app.route('/')
def show_all():
   return render_template('show_all.html', students = students.query.all() )

@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['name'] or not request.form['pin']:
         flash('Please enter all the fields', 'error')
      else:
         student = students(request.form['name'], request.form['pin'])
         
         db.session.add(student)
         db.session.commit()
         flash('Record was successfully added')
         return redirect(url_for('show_all'))
   return render_template('new.html')

@app.route('/aaron_soup')
def aaron_soup():
   testList = []
   my_url = 'https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card'
   uClient = uReq(my_url)
   page_html = uClient.read()
   uClient.close()

   page_soup = soup(page_html, "html.parser")
   containers = page_soup.findAll("div", {"class":"item-container"})

   headers = "brand, product_name, shipping\n"

   for container in containers:
      brand = container.div.div.a.img["title"]

      title_container = container.findAll("a", {"class":"item-title"})
      product_name = title_container[0].text

      shipping_container = container.findAll("li", {"class":"price-ship"})
      shipping = shipping_container[0].text.strip()

      testList.extend([brand, product_name.replace(",","|"),shipping])

   return render_template('aaron_soup.html', name="Aaron", list=testList)   

@app.route('/bootstrap_example')
def bootstrap_example():
   return render_template("bootstrap_example.html")

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)