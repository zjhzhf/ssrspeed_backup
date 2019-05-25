#coding:utf-8

import json
import subprocess
import platform
import signal
import os
import time
import sys
import logging
logger = logging.getLogger("Sub")

from SSRSpeed.Utils.checkPlatform import checkPlatform
from config import config

class Base(object):
	def __init__(self):
		self._localAddress = config.get("localAddress","127.0.0.1")
		self._localPort = config.get("localPort",1087)
		self._configList = []
		self._config = {}
		self._platform = self._checkPlatform()
		self._process = None
	
	def _checkPlatform(self):
		return checkPlatform()

	def _beforeStopClient(self):
		pass

	def startClient(self,config={}):
		pass

	def stopClient(self):
		self._beforeStopClient()
		if(self._process != None):
			if (self._checkPlatform() == "Windows"):
				self._process.terminate()
			#	self._process.send_signal(signal.SIGINT)
			else:
			#	self._process.send_signal(signal.SIGQUIT)
				self._process.send_signal(signal.SIGINT)
	#		print (self.__process.returncode)
			self._process = None
			logger.info("Client terminated.")
	#	self.__ssrProcess.terminate()

if (__name__ == "__main__"):
	pass



