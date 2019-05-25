#coding:utf-8

import time
import logging
import json
import threading
import sys
import os

logger = logging.getLogger("Sub")

from SSRSpeed.Shadowsocks.Shadowsocks import Shadowsocks as SSClient
from SSRSpeed.Shadowsocks.ShadowsocksR import ShadowsocksR as SSRClient
from SSRSpeed.Shadowsocks.V2Ray import V2Ray as V2RayClient

from SSRSpeed.Utils.ConfigParser.ShadowsocksParser import ShadowsocksParser as SSParser
from SSRSpeed.Utils.ConfigParser.ShadowsocksRParser import ShadowsocksRParser as SSRParser
from SSRSpeed.Utils.ConfigParser.V2RayParser import V2RayParser

from SSRSpeed.Result.exportResult import ExportResult
import SSRSpeed.Result.importResult as importResult

from SSRSpeed.SpeedTest.SpeedTestCore import SpeedTestCore
from SSRSpeed.Utils.checkPlatform import checkPlatform
from SSRSpeed.Utils.sorter import Sorter

from config import config

class SSRSpeedCore(object):
	def __init__(self):
		
		self.testMethod = "SOCKET"
		self.proxyType = "SSR"
		self.webMode = False
		self.colors = "origin"
		self.sortMethod = ""
		self.testMode = "TCP_PING"
		self.subscriptionUrl = ""
		self.configFile = ""
		
		self.__client = None
		self.__parser = None
		self.__stc = None
		self.__platformInfo = checkPlatform()
		self.__results = []
		self.__status = "stopped"
	
	def webGetColors(self):
		return config["exportResult"]["colors"]
	
	def webGetStatus(self):
		return self.__status
	
	def webReadSubscription(self,url,proxyType):
		parser = self.__getParserByProxyType(proxyType)
		if (parser):
			parser.readSubscriptionConfig(url)
			return parser.getAllConfig()
		return []
	
	def webSetup(self,**kwargs):
		self.testMethod = kwargs.get("testMethod","SOCKET")
		self.proxyType = kwargs.get("proxyType","SSR")
		self.colors = kwargs.get("colors","origin")
		self.sortMethod = kwargs.get("sortMethod","")
		self.testMode = kwargs.get("testMode","TCP_PING")
		self.__parser = self.__getParserByProxyType(self.proxyType)
		self.__client = self.__getClientByProxyType(self.proxyType)

	def webSetConfigs(self,configs):
		if (self.__parser):
			self.__parser.cleanConfigs()
			self.__parser.addConfigs(configs)

	def startTest(self):
		self.__stc = SpeedTestCore(self.__parser,self.__client,self.testMethod)
		self.__status = "running"
		if (self.testMode == "TCP_PING"):
			self.__stc.tcpingOnly()
		elif(self.testMode == "ALL"):
			self.__stc.fullTest()
		self.__status = "stopped"
		self.__results = self.__stc.getResult()
		self.__exportResult()

	def __getParserByProxyType(self,proxyType):
		if (proxyType == "SSR" or proxyType == "SSR-C#"):
			return SSRParser()
		elif(proxyType == "SS"):
			return SSParser()
		elif(proxyType == "V2RAY"):
			return V2RayParser()

	def __getClientByProxyType(self,proxyType):
		if (proxyType == "SSR"):
			return SSRClient()
		elif (proxyType == "SSR-C#"):
			client = SSRClient()
			client.useSsrCSharp = True
			return client
		elif(proxyType == "SS"):
			return SSClient()
		elif(proxyType == "V2RAY"):
			return V2RayClient()

	def cleanResults(self):
		self.__results = []
		if (self.__stc):
			self.__stc.resetStatus()

	def getResults(self):
		return self.__results

	def webGetResults(self):
		if (self.__status == "running"):
			if (self.__stc):
				status = "running"
			else:
				status = "pending"
		else:
			status = self.__status
		r = {
			"status":status,
			"current":self.__stc.getCurrent() if (self.__stc and status == "running") else {},
			"results":self.__stc.getResult() if (self.__stc) else []
		}
		return r
	
	def __readNodes(self):
		self.__parser.cleanConfigs()
		if (self.configFile):
			self.__parser.readGuiConfig(self.configFile)
		elif(self.subscriptionUrl):
			self.__parser.readSubscriptionConfig(self.subscriptionUrl)
		else:
			logger.critical("No config.")
			sys.exit(1)
	
	def filterNodes(self,fk=[],fgk=[],frk=[],ek=[],egk=[],erk=[]):
		self.__parser.excludeNode([],[],config["excludeRemarks"])
		self.__parser.filterNode(fk,fgk,frk)
		self.__parser.excludeNode(ek,egk,erk)
	#	print(len(self.__parser.getAllConfig()))
		self.__parser.printNode()
		logger.info("{} node(s) will be test.".format(len(self.__parser.getAllConfig())))

	def importAndExport(self,filename,split=0):
		self.__results = importResult.importResult(filename)
		self.__exportResult(split,2)
		self.__results = []

	def __exportResult(self,split = 0,exportType= 0):
		er = ExportResult()
		er.setColors(self.colors)
		er.export(self.__results,split,exportType,self.sortMethod)



