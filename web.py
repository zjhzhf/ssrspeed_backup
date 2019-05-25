#coding:utf-8

import time
import sys
import os
import json
import threading
import urllib.parse
import logging

from flask import Flask,request,redirect#,render_template
from flask_cors import CORS

from SSRSpeed.Utils.RequirementCheck.RequireCheck import RequirementCheck
from SSRSpeed.Utils.checkPlatform import checkPlatform

from SSRSpeed.Utils.Web.getpostdata import getPostData

from SSRSpeed.Core.SSRSpeedCore import SSRSpeedCore
import SSRSpeed.Core.Shell.ConsoleWeb as ShellWebServer

from SSRSpeed.Result.exportResult import ExportResult
import SSRSpeed.Result.importResult as importResult

from config import config

WEB_API_VERSION = config["WEB_API_VERSION"]

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

TEMPLATE_FOLDER = "./resources/webui/templates"
STATIC_FOLDER = "./resources/webui/statics"

app = Flask(__name__,
	template_folder=TEMPLATE_FOLDER,
	static_folder=STATIC_FOLDER,
	static_url_path=""
	)
CORS(app)
sc = None

@app.route("/",methods=["GET"])
def index():
	return redirect("https://web.绒布球.site/",301)
	#return render_template(
	#	"index.html"
	#	)

'''
	{
		"proxyType":"SSR", //[SSR,SSR-C#,SS,V2RAY]
		"testMethod":"SOCKET", //[SOCKET,SPEED_TEST_NET,FAST]
		"testMode":"",//[ALL,TCP_PING]
		"subscriptionUrl":"",
		"colors":"origin",
		"sortMethod":"",//[SPEED,REVERSE_SPEED,PING,REVERSE_PING]
		"include":[],
		"includeGroup":[],
		"includeRemark":[],
		"exclude":[],
		"excludeGroup":[],
		"excludeRemark":[]
	}
'''

@app.route("/getversion",methods=["GET"])
def getVersion():
	return json.dumps(
		{
			"main":config["VERSION"],
			"webapi":config["WEB_API_VERSION"]
		}
	)

@app.route("/status",methods=["GET"])
def status():
	return sc.webGetStatus()

@app.route("/readsubscriptions",methods=["POST"])
def readSubscriptions():
	if (request.method == "POST"):
		data = getPostData()
		if (sc.webGetStatus() == "running"):
			return 'running'
		subscriptionUrl = data.get("url","")
		proxyType = data.get("proxyType","SSR")
		if (not subscriptionUrl):
			return "invalid url."
		return json.dumps(sc.webReadSubscription(subscriptionUrl,proxyType))

@app.route("/getcolors",methods=["GET"])
def getColors():
	return json.dumps(sc.webGetColors())

@app.route('/start',methods=["POST"])
def startTest():
	if (request.method == "POST"):
		data = getPostData()
	#	return "SUCCESS"
		if (sc.webGetStatus() == "running"):
			return 'running'
		configs = data.get("configs",[])
		if (not configs):
			return "No configs"
		proxyType =data.get("proxyType","SSR")
		testMethod =data.get("testMethod","SOCKET")
		colors =data.get("colors","origin")
		sortMethod =data.get("sortMethod","")
		testMode = data.get("testMode","")
		sc.webSetup(
			testMode = testMode,
			testMethod = testMethod,
			colors = colors,
			sortMethod = sortMethod,
			proxyType = proxyType
		)
		sc.cleanResults()
		sc.webSetConfigs(configs)
		sc.startTest()
		return 'done'
	return 'invalid method'

@app.route('/getresults')
def getResults():
	return json.dumps(sc.webGetResults())

if (__name__ == "__main__"):
	pfInfo = checkPlatform()
	if (pfInfo == "Unknown"):
		logger.critical("Your system does not supported.Please contact developer.")
		sys.exit(1)

	DEBUG = False
	
	options,args = ShellWebServer.init(WEB_API_VERSION)

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

	sc = SSRSpeedCore()
	sc.webMode = True
	app.run(host=options.listen,port=int(options.port),debug=DEBUG,threaded=True)

