#coding:utf-8

import time
import sys
import os
import logging

from SSRSpeed.Shadowsocks.Shadowsocks import Shadowsocks as SSClient
from SSRSpeed.Shadowsocks.ShadowsocksR import ShadowsocksR as SSRClient
from SSRSpeed.Shadowsocks.V2Ray import V2Ray as V2RayClient

import SSRSpeed.Core.Shell.Console as ShellConsole

from SSRSpeed.SpeedTest.SpeedTestCore import SpeedTestCore

from SSRSpeed.Result.exportResult import ExportResult
import SSRSpeed.Result.importResult as importResult

from SSRSpeed.Utils.checkPlatform import checkPlatform
from SSRSpeed.Utils.ConfigParser.ShadowsocksParser import ShadowsocksParser as SSParser
from SSRSpeed.Utils.ConfigParser.ShadowsocksRParser import ShadowsocksRParser as SSRParser
from SSRSpeed.Utils.ConfigParser.V2RayParser import V2RayParser
from SSRSpeed.Utils.RequirementCheck.RequireCheck import RequirementCheck

from config import config

if (not os.path.exists("./logs/")):
	os.mkdir("./logs/")
if (not os.path.exists("./results/")):
	os.mkdir("./results/")

loggerList = []
loggerSub = logging.getLogger("Sub")
logger = logging.getLogger(__name__)
loggerList.append(loggerSub)
loggerList.append(logger)

formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(lineno)d]%(message)s")
fileHandler = logging.FileHandler("./logs/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log",encoding="utf-8")
fileHandler.setFormatter(formatter)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)

VERSION = config["VERSION"]

if (__name__ == "__main__"):
	pfInfo = checkPlatform()
	if (pfInfo == "Unknown"):
		logger.critical("Your system does not supported.Please contact developer.")
		sys.exit(1)

	DEBUG = False
	CONFIG_LOAD_MODE = 0 #0 for import result,1 for guiconfig,2 for subscription url
	CONFIG_FILENAME = ""
	CONFIG_URL = ""
	IMPORT_FILENAME = ""
	FILTER_KEYWORD = []
	FILTER_GROUP_KRYWORD = []
	FILTER_REMARK_KEYWORD = []
	EXCLUDE_KEYWORD = []
	EXCLUDE_GROUP_KEYWORD = []
	EXCLUDE_REMARK_KEWORD = []
	TEST_METHOD = ""
	TEST_MODE = ""
	PROXY_TYPE = "SSR"
	SPLIT_CNT = 0
	SORT_METHOD = ""
	SKIP_COMFIRMATION = False
	RESULT_IMAGE_COLOR = "origin"
	
	options,args = ShellConsole.init(VERSION)

	if (options.paolu):
		for root, dirs, files in os.walk(".", topdown=False):
			for name in files:
				try:
					os.remove(os.path.join(root, name))
				except:
					pass
			for name in dirs:
				try:
					os.remove(os.path.join(root, name))
				except:
					pass
		sys.exit(0)

	print("****** Import Hint 重要提示******")
	print("Before you publicly release your speed test results, be sure to ask the node owner if they agree to the release to avoid unnecessary disputes.")
	print("在您公开发布测速结果之前请务必征得节点拥有者的同意,以避免一些令人烦恼的事情")
	print("*********************************")
	input("Press ENTER to conitnue or Crtl+C to exit.")

	if (options.debug):
		DEBUG = options.debug
		for item in loggerList:
			item.setLevel(logging.DEBUG)
			item.addHandler(fileHandler)
			item.addHandler(consoleHandler)
	else:
		for item in loggerList:
			item.setLevel(logging.INFO)
			item.addHandler(fileHandler)
			item.addHandler(consoleHandler)

	if (logger.level == logging.DEBUG):
		logger.debug("Program running in debug mode")

	rc = RequirementCheck()
	rc.check()

	if (options.proxy_type):
		if (options.proxy_type.lower() == "ss"):
			PROXY_TYPE = "SS"
		elif (options.proxy_type.lower() == "ssr"):
			PROXY_TYPE = "SSR"
		elif (options.proxy_type.lower() == "ssr-cs"):
			PROXY_TYPE = "SSR-C#"
		elif (options.proxy_type.lower() == "v2ray"):
			PROXY_TYPE = "V2RAY"
		else:
			logger.warn("Unknown proxy type {} ,using default ssr.".format(options.proxy_type))

	#print(options.test_method)
	if (options.test_method == "speedtestnet"):
		TEST_METHOD = "SPEED_TEST_NET"
	elif(options.test_method == "fast"):
		TEST_METHOD = "FAST"
	else:
		TEST_METHOD = "SOCKET"

	if (options.test_mode == "pingonly"):
		TEST_MODE = "TCP_PING"
	elif(options.test_mode == "all"):
		TEST_MODE = "ALL"
	else:
		logger.critical("Invalid test mode : %s" % options.test_mode)
		sys.exit(1)
	

	if (options.confirmation):
		SKIP_COMFIRMATION = options.confirmation
	
	if (options.result_color):
		RESULT_IMAGE_COLOR = options.result_color

	if (options.import_file):
		CONFIG_LOAD_MODE = 0
	elif (options.guiConfig):
		CONFIG_LOAD_MODE = 1
		CONFIG_FILENAME = options.guiConfig
	elif(options.url):
		CONFIG_LOAD_MODE = 2
		CONFIG_URL = options.url
	else:
		logger.error("No config input,exiting...")
		sys.exit(1)


	if (options.filter):
		FILTER_KEYWORD = options.filter
	if (options.group):
		FILTER_GROUP_KRYWORD = options.group
	if (options.remarks):
		FILTER_REMARK_KEYWORD = options.remarks

	if (options.efliter):
		EXCLUDE_KEYWORD = options.efliter
	#	print (EXCLUDE_KEYWORD)
	if (options.egfilter):
		EXCLUDE_GROUP_KEYWORD = options.egfilter
	if (options.erfilter):
		EXCLUDE_REMARK_KEWORD = options.erfilter

	logger.debug(
		"\nFilter keyword : %s\nFilter group : %s\nFilter remark : %s\nExclude keyword : %s\nExclude group : %s\nExclude remark : %s" % (
			str(FILTER_KEYWORD),str(FILTER_GROUP_KRYWORD),str(FILTER_REMARK_KEYWORD),str(EXCLUDE_KEYWORD),str(EXCLUDE_GROUP_KEYWORD),str(EXCLUDE_REMARK_KEWORD)
		)
	)

	if (int(options.split_count) > 0):
		SPLIT_CNT = int(options.split_count)
	
	if (options.sort_method):
		sm = options.sort_method
	#	print(sm)
		if (sm == "speed"):
			SORT_METHOD = "SPEED"
		elif(sm == "rspeed"):
			SORT_METHOD = "REVERSE_SPEED"
		elif(sm == "ping"):
			SORT_METHOD = "PING"
		elif(sm == "rping"):
			SORT_METHOD = "REVERSE_PING"
		else:
			logger.error("Sort method %s not support." % sm)

	if (options.import_file and CONFIG_LOAD_MODE == 0):
		IMPORT_FILENAME = options.import_file
		er = ExportResult()
		er.setColors(RESULT_IMAGE_COLOR)
		er.export(importResult.importResult(IMPORT_FILENAME),SPLIT_CNT,1,SORT_METHOD)
		sys.exit(0)

	if (PROXY_TYPE == "SSR"):
		client = SSRClient()
		uConfigParser = SSRParser()
	elif (PROXY_TYPE == "SSR-C#"):
		client = SSRClient()
		client.useSsrCSharp = True
		uConfigParser = SSRParser()
	elif(PROXY_TYPE == "SS"):
		client = SSClient()
		uConfigParser = SSParser()
	elif(PROXY_TYPE == "V2RAY"):
		client = V2RayClient()
		uConfigParser = V2RayParser()

	if (CONFIG_LOAD_MODE == 1):
		uConfigParser.readGuiConfig(CONFIG_FILENAME)
	else:
		uConfigParser.readSubscriptionConfig(CONFIG_URL)
	uConfigParser.excludeNode([],[],config["excludeRemarks"])
	uConfigParser.filterNode(FILTER_KEYWORD,FILTER_GROUP_KRYWORD,FILTER_REMARK_KEYWORD)
	uConfigParser.excludeNode(EXCLUDE_KEYWORD,EXCLUDE_GROUP_KEYWORD,EXCLUDE_REMARK_KEWORD)
	uConfigParser.printNode()
	logger.info("{} node(s) will be test.".format(len(uConfigParser.getAllConfig())))

	if (TEST_MODE == "TCP_PING"):
		logger.info("Test mode : tcp ping only.")
	else:
		logger.info("Test mode : speed and tcp ping.\nTest method : %s." % TEST_METHOD)

	if (not SKIP_COMFIRMATION):
		ans = input("Before the test please confirm the nodes,Ctrl-C to exit. (Y/N)")
		if (ans == "Y"):
			pass
		else:
			sys.exit(0)

	'''
		{
			"group":"",
			"remarks":"",
			"loss":0,
			"ping":0.01,
			"gping":0.01,
			"dspeed":10214441 #Bytes
		}
	'''
	Result = []
	stc = SpeedTestCore(uConfigParser,client,TEST_METHOD)
	if (TEST_MODE == "ALL"):
		stc.fullTest()
		Result = stc.getResult()
	elif (TEST_MODE == "TCP_PING"):
		stc.tcpingOnly()
		Result = stc.getResult()

	er = ExportResult()
	er.setColors(RESULT_IMAGE_COLOR)
	er.export(Result,SPLIT_CNT,0,SORT_METHOD)


