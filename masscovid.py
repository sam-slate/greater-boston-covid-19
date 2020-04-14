# Sam Slate - 04/14/2020
# 	Script to either scrape or help with manually inputting COVID-19 case numbers from the
#	websites of towns in the greater Boston area. Will create a JSON file with town names,
#	population, number of cases, number of cases per 10000 residents, and link to source website.
#
#
#	Notes:
#		- This script requires a Chrome webdriver. You can download one here: https://chromedriver.chromium.org/downloads. 
#			Make sure to update the executable path to where you place the webdriver.
#		- Depending on a town website, COVID-19 case numbers may or may not be in a stable
#		  location in the HTML file. For those that are, an XPATH can be used to locate
#		  the element which contains the case numbers and regex can be used to pull the number
#		  itself. As websites are updated, the XPATH may have to change. 
#		- New towns can be added easily to the towns list.
#		- Some towns do not make COVID-19 case numbers available, hence the data_available boolean.
#		- Population numbers come from the U.S. Census Bureau 2018 estimates, as found here: 
#			http://www.donahue.umassp.edu/business-groups/economic-public-policy-research/massachusetts-population-estimates-program/population-estimates-by-massachusetts-geography/by-city-and-town

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import time
import json

OUTPUT_FILE = "masscovid_results_04-10-20.json"
WEBDRIVER_LOCATION = "chromedriver"

towns = [
	{
		"town_name":"Arlington",
		"population": "45,624",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.arlingtonma.gov/departments/health-human-services/health-department/coronavirus-information",
		"infected_xpath":"", 
		"infected_regex":""
	},		
	{
		"town_name": "Belmont",
		"population": "26,330",
		"data_available": True,
		"manually_find": False,
		"url":"https://www.belmont-ma.gov/home/urgent-alerts/covid-19-information-for-the-town-of-belmont-find-all-updates-here",
		"infected_xpath":"/html/body/div[3]/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div/article/div/div/table/tbody/tr[1]/td[2]/span",
		"infected_regex":".*",
	},
	{
		"town_name": "Boston",
		"population": "694,583",
		"data_available": True,
		"manually_find": False,
		"url":"https://www.boston.gov/news/coronavirus-disease-covid-19-boston",
		"infected_xpath":"/html/body/div/div/div/div/section/article/div[1]/div[3]/div[1]/div/div/div[2]/div/div/address[1]",
		"infected_regex":"BOSTON: ((?:\d|,)*) CONFIRMED"
	},
	{
		"town_name": "Braintree",
		"population": "37,250",
		"data_available": True,
		"manually_find": True,
		"url":"https://braintreema.gov/918/Board-of-Health-Updates",
		"infected_xpath":"",
		"infected_regex":""
	},
	{
		"town_name": "Brookline",
		"population": "59,310",
		"data_available": True,
		"manually_find": False,
		"url":"https://brooklinecovid19.com/",
		"infected_xpath":"/html/body/div[1]/div[2]/div/main/div[1]/section[1]/div/div/p[2]/strong",
		"infected_regex":"There are currently ((?:\d|,)*) "
	},
	{
		"town_name":"Cambridge",
		"population": "118,977",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.cambridgema.gov/covid19/casecount",
		"infected_xpath":"/html/body/form/div[3]/main/section/article/aside/section/div/div[1]/div/p[1]", 
		"infected_regex":"((?:\d|,)*)"
	},
	{
		"town_name":"Canton",
		"population": "23,629",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.town.canton.ma.us/801/7460/Coronavirus-Information",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Chelsea",
		"population": "40,160",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.chelseama.gov/coronavirusupdates",
		"infected_xpath":"/html/body", 
		"infected_regex":"There are now ((?:\d|,)*) confirmed"
	},
	{
		"town_name":"Dedham",
		"population": "25,334",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.dedham-ma.gov/departments/health/covid-19-coronavirus-information",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Dover",
		"population": "6,101",
		"data_available":True,
		"manually_find": True,
		"url":"http://doverma.org/covid-19/",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Everett",
		"population": "46,880",
		"data_available": False,
		"manually_find": False,
		"url":"",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Lexington",
		"population": "33,792",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.lexingtonma.gov/public-health/pages/everything-you-need-know-during-covid-19-state-emergency",
		"infected_xpath":"/html/body/div[2]/div[2]/div/div/section/div/div/div/div/div/div/div[2]/div/div/article/div/div/div[1]/div[3]/p", 
		"infected_regex":"((?:\d|,)*) confirmed"
	},
	{
		"town_name":"Lincoln",
		"population": "6,797",
		"data_available":True,
		"manually_find": False,
		"url":"http://www.lincolntown.org/1169/Coronavirus-Covid-19",
		"infected_xpath":"/html/body/div[4]/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div/div/div/div/div[1]/div/strong/span/div/strong[1]/h2/span[1]/span", 
		"infected_regex":".*"
	},
	{
		"town_name":"Lynn",
		"population": "94,654",
		"data_available":True,
		"manually_find": True,
		"url":"http://www.ci.lynn.ma.us/departments/publichealth_covid19_resources.shtml#gpm1_2",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Lynnfield",
		"population": "13,041",
		"data_available":True,
		"manually_find": False,
		"url":"https://coronavirus-response-lynnfield-ma-dgl-ssu.hub.arcgis.com/",
		"infected_xpath":"/html/body/div[6]/div[3]/div/div[1]/div/section[3]/div/div[9]/div[1]/div/table/tbody/tr[4]/td[2]/h6", 
		"infected_regex":".*",
		"need_to_wait": True
	},
	{
		"town_name":"Malden",
		"population": "61,036",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.cityofmalden.org/AlertCenter.aspx",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Marblehead",
		"population": "20,634",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.marblehead.org/home/urgent-alerts/information-alert-coronavirus-disease-2019-covid-19",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Medford",
		"population": "57,765",
		"data_available":True,
		"manually_find": False,
		"url":"http://www.medfordma.org/coronavirus-information/",
		"infected_xpath":"/html/body/div[4]/div/div[1]/main/div/div/div/div/h3[2]/strong[2]", 
		"infected_regex":".*",
		"need_to_wait": True
	},
	{
		"town_name":"Melrose",
		"population": "28,193",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.cityofmelrose.org/covid-19-important-information/pages/news-updates",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Milton",
		"population": "27,616",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.townofmilton.org/health-department/infectious-diseases/pages/health-department-coronavirus-information",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Nahant",
		"population": "3,524",
		"data_available":True,
		"manually_find": False,
		"url":"https://nahantcovid19.com/",
		"infected_xpath":"/html/body", 
		"infected_regex":"Positive COVID-19 cases in Nahant: ((?:\d|,)*)"
	},
	{
		"town_name":"Needham",
		"population": "31,248",
		"data_available":True,
		"manually_find": True,
		"url":"https://stories.opengov.com/needhamma/published/lP3WUJtv_",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Newton",
		"population": "88,904",
		"data_available":True,
		"manually_find": False,
		"url":"http://www.newtonma.gov/gov/health_n_human_services/public/covid19/default.asp",
		"infected_xpath":"/html/body/div[1]/div[2]/div[2]/div/div[2]/section/div[3]/div/table[2]/tbody/tr/td[1]/p[2]/span/strong/span", 
		"infected_regex":"Confirmed COVID-19 Cases in Newton: ((?:\d|,)*)"
	},
	{
		"town_name":"Peabody",
		"population": "53,278",
		"data_available":False,
		"manually_find": False,
		"url":"",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Quincy",
		"population": "94,580",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.quincyma.gov/covid19.htm",
		"infected_xpath":"/html/body/div[1]/div[3]/div[2]/div/div[2]/section/div[3]/div/p[2]", 
		"infected_regex":"Quincy Cases: ((?:\d|,)*) \("
	},
	{
		"town_name":"Randolph",
		"population": "34,398",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.randolph-ma.gov/home/urgent-alerts/coronavirus-information",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Revere",
		"population": "53,821",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.revere.org/departments/public-health-division/coronavirus",
		"infected_xpath":"/html/body", 
		"infected_regex":"Confirmed Cases in Revere.*: ((?:\d|,)*)",
		"need_to_wait": True
	},
	{
		"town_name":"Salem",
		"population": "43,559",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.salem.com/news",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Saugus",
		"population": "28,385",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.saugus-ma.gov/node/1/news",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Somerville",
		"population": "81,562",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.somervillema.gov/departments/programs/novel-coronavirus-preparedness-and-information",
		"infected_xpath":"/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div/section[2]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[1]/font/span/b",
		"infected_regex":".*"
	},
	{
		"town_name":"Stoneham",
		"population": "22,729",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.stoneham-ma.gov/825/COVID-19",
		"infected_xpath":"/html/body/div[4]/div/div[2]/div[2]/div/div[2]/div/div/div/div[1]/div/div[2]/div[1]/div/div[1]/div/div/div/div/div/p[2]/strong/span", 
		"infected_regex":"COVID-19:   ((?:\d|,)*)"
	},
	{
		"town_name":"Swampscott",
		"population": "15,227",
		"data_available":True,
		"manually_find": False,
		"url":"http://www.swampscottma.gov/covid-19-updates",
		"infected_xpath":"/html/body", 
		"infected_regex":"There have been ((?:\d|,)*) cases"
	},
	{
		"town_name":"Wakefield",
		"population": "27,135",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.wakefield.ma.us/covid-updates",
		"infected_xpath":"/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div/article/div/section/ul[1]/li", 
		"infected_regex":"Wakefield: ((?:\d|,)*)"
	},
	{
		"town_name":"Waltham",
		"population": "62,962",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.city.waltham.ma.us/home/urgent-alerts/see-latest-update-regarding-covid-19-in-waltham-from-mayor-mccarthy-councillor",
		"infected_xpath":"/html/body/div[3]/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div/article/div/div/p[1]/strong", 
		"infected_regex":"((?:\d|,)*) \(in isolation\)"
	},
	{
		"town_name":"Watertown",
		"population": "35,954",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.watertown-ma.gov/CivicAlerts.aspx?AID=1295",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Wellesley",
		"population": "29,673",
		"data_available":True,
		"manually_find": False,
		"url":"https://coronavirus-wellesleyma.hub.arcgis.com/",
		"infected_xpath":"//html/body/div[6]/div[3]/div/div[1]/div/section[4]/div/div[2]/div[1]/div/div[2]/span", 
		"infected_regex":".*"
	},
	{
		"town_name":"Weston",
		"population": "12,134",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.weston.org/CivicAlerts.aspx?AID=595",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Westwood",
		"population": "16,127",
		"data_available":True,
		"manually_find": True,
		"url":"https://www.townhall.westwood.ma.us/departments/community-economic-development/health-division/covid-19-information",
		"infected_xpath":"", 
		"infected_regex":""
	},
	{
		"town_name":"Winchester",
		"population": "22,851",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.winchester.us/573/Updates-from-the-Town-Manager",
		"infected_xpath":"/html/body/div[4]/div/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[1]/div/div/div/div/div/table/tbody/tr[1]/td[2]", 
		"infected_regex":"((?:\d|,)*)"
	},
	{
		"town_name":"Winthrop",
		"population": "18,688",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.town.winthrop.ma.us/home/urgent-alerts/covid-19-public-health-updates",
		"infected_xpath":"/html/body", 
		"infected_regex":"((?:\d|,)*) confirmed cases"
	},
	{
		"town_name":"Woburn",
		"population": "40,397",
		"data_available":True,
		"manually_find": False,
		"url":"https://www.woburnma.gov/coronoavirus-covid-19-information-for-woburn-massachusetts/#woburn-covid-19-case-information",
		"infected_xpath":"/html/body/div[1]/div[3]/div/div/div/div[3]/table/tbody/tr[2]/td[1]", 
		"infected_regex":".*"
	}
]

def get_num_cases(towns):
	browser = webdriver.Chrome(executable_path=WEBDRIVER_LOCATION)

	results = []

	for town in towns:
		town_result = {"town_name":town["town_name"].upper(), "find_data_url":town["url"], "population":town["population"]}
		print(town["town_name"])


		if not town["data_available"]:
			town_result["data_available"] = False
			print("Data not available")
		else:
			town_result["data_available"] = True

			browser.get(town["url"])

			# If Javascript needs to load
			if "need_to_wait" in town:
				time.sleep(2)

			# Gets manual input if not scrapable
			if town["manually_find"]:
				infected_number = input("Number of cases: ")
			else:
				try:
					# Uses selenium to scrape the relevent element by XPATH 
					# and regex to pull the data
					element = browser.find_element(By.XPATH, town["infected_xpath"])
					print(element.text)
					x = re.findall(town["infected_regex"], element.text)

					if x:
						infected_number = x[0]
						print("Infected: ", infected_number)
					else:
						print("Regex Failure")
						infected_number = input("Number of cases: ")

				# Excepts a selenium error of no elements found and switches to manual 
				except NoSuchElementException:
					print("XPATH Error")
					infected_number = input("Number of cases: ")

			town_result["num_cases"] = infected_number

			# Computes the number of cases per 10000 residents, rounded to 2 decimal places
			town_result["cases_per_10000"] = round((int(infected_number.replace(',', '')) * 10000)/int(town["population"].replace(',', '')), 2)

		print(town_result)
		results.append(town_result)

	print(results)
	return results

results = get_num_cases(towns)
results_json = json.dumps(results)
print(results_json)

f = open(OUTPUT_FILE, "w")
f.write(results_json)
f.close()




