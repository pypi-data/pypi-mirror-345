# DEFAULT_API_URL = "https://api.example.com/upload"
# ALLOWED_EXTENSIONS = [".xml"]
# LOGGING_ENABLED = True
# VERSION = "0.1.0"

import os

class Config:
	def __init__(self):
		# self.server = "LOCAL"
		# self.api_base_url = "http://localhost/api.appachhi.com/"
		self.allowed_extensions = [".xml"]
		self.default_api_key = "0c98159b0990e30f6af82a08a3c0c48077bd6545"
		# self.setup_configuration()

	# def setup_configuration(self):
	# 	if self.server == "LOCAL":
	# 		self.api_base_url = "http://localhost/api.appachhi.com/"
	# 	elif self.server == "STAGE":
	# 		self.api_base_url = "https://api.stage.bugasura.io/"
	# 	elif self.server == "LIVE":
	# 		self.api_base_url = "https://api.bugasura.io/"
	# 	elif self.server == "CUSTOM":
	# 		self.api_base_url = ""
	# 	else:
	# 		self.api_base_url = "https://api.stage.bugasura.io/"
