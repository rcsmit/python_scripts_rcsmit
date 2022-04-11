import os, datetime, time, csv
from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from sys import argv
import random		
import re

# based on
# https://github.com/jcontini/facebook-scraper
# read his instructions how to set up the scraper


# Configure browser session
wd_options = Options()
wd_options.add_argument("--disable-notifications")
wd_options.add_argument("--disable-infobars")
wd_options.add_argument("--mute-audio")
browser = webdriver.Chrome(options=wd_options)

# --------------- Ask user to log in -----------------
def fb_login():
	print("Opening browser...")
	browser.get("https://m.facebook.com/")
	a = input("Please log into facebook and press enter after the page loads...")

# --------------- Scroll to bottom of page -----------------
def scroll_to_bottom():
	print("Scrolling to bottom...")
	while True:
			try:
				browser.find_element_by_class_name('_4khu') # class after friend's list
				print("Reached end!")
				break
			except:
				browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(0.25)
				pass

# ----------------- Load list from CSV -----------------
def load_csv(filename):
	inact = 0
	myfriends = []
	with open(filename, 'r') as input_csv:
		reader = csv.DictReader(input_csv)
		for idx,row in enumerate(reader):
			if row['active'] is '1':
				myfriends.append({
					"name":row['B_name'],
					"uid":row['B_id']
					})
			else:
				print("Skipping %s (inactive)" % row['B_name'])
				inact = inact + 1
	print("%d friends in imported list" % (idx+1))
	print("%d ready for scanning (%d inactive)" % (idx-inact+1, inact))

	return myfriends
	

# --------------- Get list of all friends on page ---------------
def scan_friends():
	print('Scanning page for friends...')
	friends = []
	friend_cards = browser.find_elements_by_xpath('//div[@id="pagelet_timeline_medley_friends"]//div[@class="fsl fwb fcb"]/a')

	for friend in friend_cards:
		if friend.get_attribute('data-hovercard') is None:
			print(" %s (INACTIVE)" % friend.text)
			friend_id = friend.get_attribute('ajaxify').split('id=')[1]
			friend_active = 0
		else:
			print(" %s" % friend.text)
			friend_id = friend.get_attribute('data-hovercard').split('id=')[1].split('&')[0]
			friend_active = 1

		friends.append({
			'name': friend.text.encode('ascii', 'ignore').decode('ascii'), #to prevent CSV writing issues
			'id': friend_id,
			'active': friend_active
			})

	print('Found %r friends on page!' % len(friends))
	return friends



# --------------- Scrape 1st degree connections ---------------
def scrape_1st_degrees():
	#Prep CSV Output File
	csvOut = '1st-degree_%s.csv' % now.strftime("%Y-%m-%d_%H%M")
	writer = csv.writer(open(csvOut, 'w'))
	writer.writerow(['A_id','A_name','B_id','B_name','active'])

	#Get your unique Facebook ID
	profile_icon = browser.find_element_by_css_selector("[data-click='profile_icon'] > a > span > img")
	myid = profile_icon.get_attribute("id")[19:]

	#Scan your Friends page (1st-degree connections)
	print("Opening Friends page...")
	browser.get("https://www.facebook.com/" + myid + "/friends")
	scroll_to_bottom()
	myfriends = scan_friends()

	#Write connections to CSV File
	for friend in myfriends:
			writer.writerow([myid,"Me",friend['id'],friend['name'],friend['active']])

	print("Successfully saved to %s" % csvOut)
	
	
# --------------- Scrape current city of your connections. ---------------
#This can take several days if you have a lot of friends!!
def scrape_wp_degrees():

	volgnr = "1"
	#Prep CSV Output File
	# csvOut = volgnr + 'woonplaats-degree_%s.csv' % now.strftime("%Y-%m-%d_%H%M")
	csvOut = "uitvoer.csv"
	writer = csv.writer(open(csvOut, 'w'))
	writer.writerow("----------------------- "+ volgnr + " ------------------")

	writer.writerow(['A_id', 'B_id', 'A_name','B_name','active'])

	#Load friends from CSV Input File
	#script, filename = argv
	print("Loading list ..." )
	myfriends = load_csv("in/" + volgnr + ".csv")
	n=0
	
	for idx,friend in enumerate(myfriends):
		#Load URL of friend's friend page
		scrape_url = "https://m.facebook.com/profile.php?id=" + friend['uid'] + "&v=info" 
	
		browser.get(scrape_url)
	
		s = browser.find_element_by_class_name("aboutme").text

		#Scan your friends' current city
		print("%d) %s" % (idx+1, scrape_url))
		s = s.replace('\n', '')
		print (s)
		
		result = re.search('LIVED(.*)Current', s)
		try:
			wp2 = result.group(1)
		except:
			wp2= "na"
				
		print ("WOONPLAATS " + wp2)
		#Write connections to CSV File
		writer.writerow([friend['uid'],friend['name'],wp2])
		n = n + 1
		
		# Wait for for a random number of seconds	
		time.sleep(random.uniform(3, 6))

# --------------- Start Scraping ---------------
now = datetime.now()
fb_login()
scrape_1st_degrees()
scrape_wp_degrees()
