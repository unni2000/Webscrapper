import requests
import csv
from bs4 import BeautifulSoup
import json
import pandas as pd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import cloudscraper

scraper = cloudscraper.create_scraper()
geolocator = Nominatim(user_agent="geoapiExercises")

gbfood = pd.DataFrame()
gbfood = pd.DataFrame(gbfood,
                      columns=[
                          'name', 'place', 'review', 'reviewcount', 'foodcat',
                          'location', 'avgprice', 'waitingtime'
                      ])
fdpanda = pd.DataFrame(gbfood,
                       columns=[
                           'name', 'place', 'review', 'reviewcount', 'foodcat',
                           'location', 'avgprice', 'waitingtime'
                       ])
delivero = pd.DataFrame(gbfood,
                        columns=[
                            'name', 'place', 'review', 'reviewcount',
                            'foodcat', 'location', 'avgprice', 'waitingtime'
                        ])
output = pd.DataFrame(gbfood,
                      columns=[
                          'name', 'place', 'review', 'reviewcount', 'foodcat',
                          'location', 'avgprice', 'waitingtime'
                      ])


def grabfood():
	global gbfood
	URL = 'https://food.grab.com/sg/en/restaurants'
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, 'html.parser')
	job_elems = soup.find_all(class_='RestaurantListCol___1FZ8V')
	for job_elem in job_elems:
		e1 = job_elem.find(class_='name___2epcT')
		e2 = job_elem.find(class_='basicInfoRow___UZM8d')
		e3 = job_elem.find(class_='numbersChild___2qKMV')
		link = job_elem.find('a')['href']
		key = str(link).rsplit('/', 1)
		e1 = str(e1.text).split('-', 1)
		place = e1
		location = geolocator.reverse(
		    jsndt(soup, key[1], 'latitude') + "," +
		    jsndt(soup, key[1], 'longitude'))
		loc = str(location)
		row = pd.DataFrame([[
		    e1[0], place[0], e3.text, 'N/A', e2.text, loc, 'N/A',
		    jsndt(soup, key[1], "estimatedDeliveryTime")
		]],
		                   columns=[
		                       'name', 'place', 'review', 'reviewcount',
		                       'foodcat', 'location', 'avgprice', 'waitingtime'
		                   ])
		gbfood = gbfood.append(row, ignore_index=True)


def jsndt(soup, key, item):
	global grabfood
	e = soup.find(id='__NEXT_DATA__')
	json_data = json.loads(e.contents[0])
	return json.dumps(
	    json_data["props"]["initialReduxState"]["pageRestaurantsV2"]
	    ["entities"]["restaurantList"][key][item])


def foodpanda():
	global fdpanda
	URL = 'https://www.foodpanda.sg/restaurants/new?lat=1.3575338350814834&lng=103.81877549622834&vertical=restaurants'
	page = requests.get(URL,headers={'User-agent': 'Mozilla/5.0'})
	soup = BeautifulSoup(page.content, 'html.parser')
	element = soup.find_all('script')[6].contents[0].strip()[27:]
	try:
		element = element.split(";window")[0]
		json_data = json.loads(element)
	except:
		json_data = json.loads(element)

	jd1 = json_data['swimlanes']['swimlanesList'][4]['items']
	jd2 = json_data['swimlanes']['swimlanesList'][6]['items']
	jd3 = json_data['organicList']['vendors']
	jd = [jd1, jd2, jd3]
	for j in jd:
		for i in j:
			fdct = ""
			li = []
			for k in i["cuisines"]:
				li.append(k["name"])
			fdct = (lambda a: " ".join(a))(li)
			place = (str(i["address"]).split(",", 1))[0]
			row = pd.DataFrame([[
			    i["chain"]["name"], place, i["rating"], i["review_number"],
			    str(fdct), i["address"],
			    int(i["minimum_delivery_fee"]) +
			    int(i["minimum_order_amount"]),
			    int(i["minimum_delivery_time"]) + int(i["minimum_pickup_time"])
			]],
			                   columns=[
			                       'name', 'place', 'review', 'reviewcount',
			                       'foodcat', 'location', 'avgprice',
			                       'waitingtime'
			                   ])
			fdpanda = fdpanda.append(row, ignore_index=True)


def deliveroo():
	global delivero
	URL = "https://deliveroo.com.sg/restaurants/singapore/woodlands-central?fulfillment_method=DELIVERY&geohash=w23b1vbf443w"
	page = scraper.get(URL)
	soup = BeautifulSoup(page.content, 'html.parser')
	job_elems = soup.find_all(class_='HomeFeedUICard-1cc6964985e41c86')
	e = soup.find(id='__NEXT_DATA__')
	data = json.loads(e.contents[0])
	data = data["props"]["initialState"]["home"]["feed"]["results"]["data"]
	for i in data:
		if (i["typeName"] == "UILayoutList"):
			i = i["blocks"]
			for j in i:
				if (j["typeName"] == "UICard"):
					try:
						name = (str(j["target"]["restaurant"]["name"]).split(
						    "-", 1))[0]
						review = j["uiContent"]["default"]["uiLines"][1][
						    "uiSpans"]
					except:
						name = ""
						review = ""
					try:
						avgtime = j["uiContent"]["default"]["bubble"]["text"]
					except:
						avgtime = 'N/A'
					try:
						a = j["uiContent"]["default"]["uiLines"][1]["uiSpans"][
						    20]["text"]
					except:
						a = None
					try:
						b = j["uiContent"]["default"]["uiLines"][1]["uiSpans"][
						    12]["text"]
					except:
						b = None
					try:
						c = j["uiContent"]["default"]["uiLines"][1]["uiSpans"][
						    8]["text"]
					except:
						c = None
					foodcat = str(a) + " " + str(b) + " " + str(c)
					try:
						rvcount = j["uiContent"]["default"]["uiLines"][1][
						    "uiSpans"][4]["text"]
						rvcount = (str(rvcount).split("(")[1]).split(")")[0]
					except:
						rvcount = "N/A"
					rv = ""
					for k in review:
						if (k["typeName"] == "UISpanText"):
							rv = k["text"]
							break
					try:
						rv = (str(rv).split())[0]
					except:
						rv = 'N/A'
					if (len(str(rv)) > 3):
						rv = "N/A"
					row = pd.DataFrame([[
					    name, 'N/A', rv, rvcount, foodcat, 'N/A', 'N/A',
					    avgtime
					]],
					                   columns=[
					                       'name', 'place', 'review',
					                       'reviewcount', 'foodcat',
					                       'location', 'avgprice',
					                       'waitingtime'
					                   ])
					delivero = delivero.append(row, ignore_index=True)


def cleanData():
	csvfile = open('output.csv', 'r', newline='')
	csvfile2 = open('cleanData.csv', 'w')
	obj = csv.reader(csvfile)
	obj2 = csv.writer(csvfile2)
	i = 0
	n = []
	for row in obj:
		if row[1] == '' or row[4] == 'N/A':
			continue
		else:
			row[0] = i
			row[5] = row[5].replace('[', '').replace('\'', '').replace(
			    ',', '').replace(']', '')
			if (row[4] == '500+'):
				row[4] = 500
				row[4] = int(row[4])
			if not row[1] in n:
				n.append(row[1])
				obj2.writerow(row)
				i += 1

	csvfile.close()


def graphplot1():
	df = output
	df.drop_duplicates(subset="name", inplace=True)
	nan_value = float("NaN")
	df.replace("", nan_value, inplace=True)
	df["reviewcount"] = df["reviewcount"].apply(
	    lambda x: str(x).strip().replace("N/A", "0"))
	df.dropna(subset=["reviewcount", "name"], inplace=True)
	df["reviewcount"] = df["reviewcount"].apply(
	    lambda x: str(x).strip().replace("+", ""))
	pd.set_option("display.max_rows", None, "display.max_columns", None)
	df["reviewcount"] = df["reviewcount"].apply(
	    lambda x: int(float(str(x).strip())))
	df = df.nlargest(20, ['reviewcount'])
	ax = plt.gca()
	df.plot(kind='barh', y='reviewcount', x='name', ax=ax)
	plt.xlabel('Review counts')
	plt.ylabel('Name of restaurants')
	plt.title('Review count per restaurants')
	plt.legend()
	plt.savefig("review_count_per_restaurant.png",
	            dpi=300,
	            bbox_inches='tight')
	plt.show()
	df["foodcat"] = df["foodcat"].apply(
	    lambda x: str(x).strip().replace("N/A", " "))
	df["foodcat"] = df["foodcat"].apply(
	    lambda x: str(x).strip().replace("None", " "))
	df["foodcat"] = df["foodcat"].apply(
	    lambda x: str(x).strip().replace(",", " "))
	df.dropna(subset=["foodcat"], inplace=True)
	foods = []
	li = df["foodcat"].tolist()
	for i in li:
		foods.extend(i.split())
	counts = []
	foods = list(set(foods))
	for k in foods:
		if "&" in str(k):
			foods.remove(k)
	for i in foods:
		count = 0
		for j in df["foodcat"]:
			if i in list(j.split()):
				count += 1
		counts.append(count)
	data = pd.DataFrame(list(zip(foods, counts)), columns=['food', 'count'])
	data = data.nlargest(20, ["count"])
	ax = plt.gca()
	data.plot(kind='bar', x='food', y='count', ax=ax)
	plt.xlabel('Food catagory')
	plt.ylabel('Number of restaurants')
	plt.xticks(rotation=45)
	plt.title('Number of restaurants per food catagory')
	plt.legend()
	plt.savefig("restaurant_per_food_catagory.png",
	            dpi=300,
	            bbox_inches='tight')
	plt.show()


try:
	foodpanda()
	output = output.append(fdpanda)
except:
	print("")

grabfood()
deliveroo()

output = output.append(gbfood)
output = output.append(delivero)
print("select the site you want\n")
print("1.foodpanda\n2.grabfood\n3.deliveroo\n4.Create CSV and Plot graph\n")
a = input("Enter the number:")
a = int(a)
if (a == 1):
	try:
		foodpanda()
		output = output.append(fdpanda)
	except:
		print("Foodpanda site error ")
	print("successful!!")
	pd.set_option("display.max_rows", None, "display.max_columns", None)
	print(fdpanda)

elif (a == 2):
	grabfood()
	print("successful!!")
	pd.set_option("display.max_rows", None, "display.max_columns", None)
	print(gbfood)

elif (a == 3):
	deliveroo()
	print("successful!!")
	pd.set_option("display.max_rows", None, "display.max_columns", None)
	print(delivero)
elif (a == 4):
	try:
		foodpanda()
		output = output.append(fdpanda)
	except:
		print("Foodpanda site updating unable to retrive now ")
	grabfood()
	deliveroo()
	output = output.append(gbfood)
	output = output.append(delivero)
	output.to_csv("output.csv")
	cleanData()
	graphplot1()
	print(
	    "output successfully saved as output.csv and cleanData.csv,graph is displyed"
	)

else:
	print("Wrong selection")
