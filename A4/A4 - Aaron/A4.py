#submission by Aaron Reyes
import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def hello():
	testList = []
	my_url = 'https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card'
	uClient = uReq(my_url)
	page_html = uClient.read()
	uClient.close()

	page_soup = soup(page_html, "html.parser")
	containers = page_soup.findAll("div", {"class":"item-container"})

	#filename = "products.csv"
	#f = open(filename, "w")

	headers = "brand, product_name, shipping\n"

	#f.write(headers)

	for container in containers:
		brand = container.div.div.a.img["title"]

		title_container = container.findAll("a", {"class":"item-title"})
		product_name = title_container[0].text

		shipping_container = container.findAll("li", {"class":"price-ship"})
		shipping = shipping_container[0].text.strip()

		testList.extend([brand, product_name.replace(",","|"),shipping])
		#f.write(brand + "," +  product_name.replace(",", "|") + "," + shipping + "\n")

	#f.close()
	return render_template('index.html', name="Aaron", list=testList)

if __name__ == "__main__":
    app.run(debug=True)