import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time


API_KEY = "tCeaUtDpTRRu"
PROJECT_TOKEN = "tc8gDoTm9Nq_"
RUN_TOKEN = "tWv6HkwXLSwn"


class Data:
	def __init__(self, api_key, project_token):
		self.api_key = api_key
		self.project_token = project_token
		self.params = {
			"api_key": self.api_key
		}
		self.data = self.get_data()

	def get_data(self):
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
		data = json.loads(response.text)
		return data
		return data

	def get_total_cases(self):
		data = self.data['total']

		for content in data:
			if content['name'] == "Coronavirus Cases:":
				return content['value']

	def get_total_deaths(self):
		data = self.data['total']

		for content in data:
			if content['name'] == "Deaths:":
				return content['value']
		return '0'

	def get_country_data(self, country):
		data = self.data['country']

		for content in data:
			if content['name'].lower() == country.lower():
				return content

		return '0'


	def get_list_of_countries(self):
		countries = []
		for country in self.data['country']:
			countries.append(country['name'].lower())

		return countries

	def update_data(self):
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)
		

		def poll():
			time.sleep(0.1)
			old_data = self.data
			while True:
				new_data = self.get_data()
				if new_data != old_data:
					self.data = new_data
					print("DataBase Updated")
					break
				time.sleep(5)

		t = threading.Thread(target=poll)
		t.start()


def get_audio():
	
	r = sr.Recognizer()
	with sr.Microphone() as source:
		r.adjust_for_ambient_noise(source)
		audio = r.listen(source, phrase_time_limit=4)
		said = ""
		try:
			said = r.recognize_google(audio)
		except sr.UnknownValueError:
			print("Google Speech Recognition could not understand audio")
		except sr.RequestError as e:
			print("Could not request results from Google Speech Recognition service; {0}".format(e))
	return said.lower()

	

def main():
	print("Program Started")
	data = Data(API_KEY, PROJECT_TOKEN)
	country_list = data.get_list_of_countries()
	END_PHRASE = "stop the program"

	TOTAL_PATTERNS = {
					re.compile("[\w\s]+ total [\w\s]+ cases$"):data.get_total_cases,
					re.compile("[\w\s]+ total cases$"): data.get_total_cases,
                    re.compile("[\w\s]+ total [\w\s]+ deaths$"): data.get_total_deaths,
                    re.compile("[\w\s]+ total deaths$"): data.get_total_deaths
					}

	COUNTRY_PATTERNS = {
					re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
                    re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
					}

	UPDATE_COMMAND = "update the database"


	while True:
		print("Listening...")
		text = get_audio()
		result = None
		print(text)

		for pattern, func in COUNTRY_PATTERNS.items():
			if pattern.match(text):
				words = set(text.split(" "))
				for country in country_list:
					if country in words:
						result = func(country)
						break
				
				

		for pattern, func in TOTAL_PATTERNS.items():
			if pattern.match(text):
				result = func()
				break

		if text == UPDATE_COMMAND:
			result = "Data is being updated. This may take a moment!"
			data.update_data()


		if result:
				print(result)

		if text.find(END_PHRASE)!=-1:
			print("Existing Program")
			break

main()
