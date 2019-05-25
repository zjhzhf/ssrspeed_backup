#coding:utf-8

import threading
import socks
import socket
import requests
import json
import time
import re
import copy
import logging

logger = logging.getLogger("Sub")
"""
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(lineno)d]%(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
"""

from SSRSpeed.Utils.IPGeo import parseLocation
from config import config

MAX_THREAD = config["speedtestsocket"]["maxThread"]
DEFAULT_SOCKET = socket.socket
MAX_FILE_SIZE = 100 * 1024 * 1024
BUFFER = config["speedtestsocket"]["buffer"]
EXIT_FLAG = False
LOCAL_PORT = 1080
LOCK = threading.Lock()
TOTAL_RECEIVED = 0
MAX_TIME = 0

def setProxyPort(port):
	global LOCAL_PORT
	LOCAL_PORT = port

def restoreSocket():
	socket.socket = DEFAULT_SOCKET


def speedTestThread(link):
	global TOTAL_RECEIVED,MAX_TIME
	logger.debug("Thread {} started.".format(threading.current_thread().ident))
	link = link.replace("https://","").replace("http://","")
	host = link[:link.find("/")]
	requestUri = link[link.find("/"):]
	logger.debug("\nLink: %s\nHost: %s\nRequestUri: %s" % (link,host,requestUri))
	#print(link,MAX_FILE_SIZE)
	try:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.settimeout(12)
		try:
			s.connect((host,80))
			logger.debug("Connected to %s" % host)
		except:
			logger.error("Connect to %s error." % host)
			LOCK.acquire()
			TOTAL_RECEIVED += 0
			LOCK.release()
			return
		s.send(b"GET %b HTTP/1.1\r\nHost: %b\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36\r\n\r\n" % (requestUri.encode("utf-8"),host.encode("utf-8")))
		logger.debug("Request sent.")
		startTime = time.time()
		received = 0
		while True:
			try:
				xx = s.recv(BUFFER)
			except socket.timeout:
				logger.error("Receive data timeout.")
				break
			lxx = len(xx)
		#	received += len(xx)
			received += lxx
		#	TR = 0
			LOCK.acquire()
			TOTAL_RECEIVED += lxx
		#	TR = TOTAL_RECEIVED
			LOCK.release()
		#	logger.debug(TR)
			if (received >= MAX_FILE_SIZE or EXIT_FLAG):
				break
		endTime = time.time()
		deltaTime = endTime - startTime
		if (deltaTime >= 12):
			deltaTime = 11
		s.close()
		logger.debug("Thread {} done,time : {}".format(threading.current_thread().ident,deltaTime))
		LOCK.acquire()
	#	TOTAL_RECEIVED += received
		MAX_TIME = max(MAX_TIME,deltaTime)
		LOCK.release()
	except:
		logger.exception("")
		return 0

def getDownloadLink(tag = None):
	cfg = config["speedtestsocket"]["downloadLinks"]
	defaultCfg = {}
	for link in cfg:
		if (link["tag"].strip() == "Default"):
			defaultCfg = link
			break
	if (not tag):
		return(defaultCfg["link"],defaultCfg["fileSize"])
	for link in cfg:
		if(link["tag"].strip() == tag.strip()):
			logger.info("Tag matched : %s" % tag)
			return (link["link"],link["fileSize"])
	logger.warn("Tag %s not matched,using default." % tag)
	return(defaultCfg["link"],defaultCfg["fileSize"])

def checkRule():
	try:
		res = (False,"DEFAULT","DEFAULT","DEFAULT")
		res = parseLocation()
		if (not res[0]):
			logger.error("Parse location failed,using default.")
			return getDownloadLink()
	#	countryCode = res[1].strip()
	#	cotinent = res[2].strip()
		isp = res[3].strip()
		rules = config["speedtestsocket"]["rules"]
		for rule in rules:
			if (rule["mode"] == "match_isp"):
				if (isp in rule["ISP"].strip()):
					logger.info("ISP %s matched." % isp)
					return getDownloadLink(rule["tag"])
			elif(rule["mode"] == "match_location"):
				logger.debug("Match mode : Location")
				for code in rule.get("countries",[]): 
					if (res[1].strip() == code.strip()):
						logger.info("Country code %s matched." % res[1])
						return getDownloadLink(rule["tag"])
				if (rule.get("continent","") != "" and rule["continent"].strip() in res[2].strip()):
					logger.info("Continent %s matched." % res[2])
					return getDownloadLink(rule["tag"])
		logger.info("No rule matched.using default.")
		return getDownloadLink()
	except:
		logger.exception("Match Rule Error,using default.")
		return getDownloadLink()

def calcMaxSpeed(maxSpeed,deltaRecv,deltaTime):
	if (maxSpeed == 0):
		return (deltaRecv / deltaTime * 0.7)
	else:
		a = 2 / (1+32)
		return (0.5 + maxSpeed * (1 - a) + a * deltaRecv / deltaTime)

def speedTestSocket(port):
	global EXIT_FLAG,LOCAL_PORT,MAX_TIME,TOTAL_RECEIVED,MAX_FILE_SIZE
	LOCAL_PORT = port
	if (not config["speedtestsocket"]["skipRuleMatch"]):
		res = checkRule()
	else:
		logger.info("Skip rule match.")
		res = getDownloadLink()
	link = res[0]
	MAX_FILE_SIZE = res[1] * 1024 * 1024
	#print(link,MAX_FILE_SIZE)
	#return 0
	#logger.debug("Actived threads: %d" % threading.active_count())
	MAX_TIME = 0
	TOTAL_RECEIVED = 0
	EXIT_FLAG = False
	socks.set_default_proxy(socks.SOCKS5,"127.0.0.1",LOCAL_PORT)
	socket.socket = socks.socksocket
#	ii = 0
#	threadCount = threading.active_count()
#	while (threadCount > 1):
#		logger.info("Waiting for thread exit,please wait,thread count : %d" % (threadCount - 1))
#		ii += 1
#		time.sleep(2)
#		threadCount = threading.active_count()
#		if (ii >= 3):
#			logger.warn("%d thread(s) still running,skipping." % (threadCount - 1))
#			break
	for i in range(0,MAX_THREAD):
		nmsl = threading.Thread(target=speedTestThread,args=(link,))
		nmsl.start()
	maxSpeedList = []
	maxSpeed = 0
	currentSpeed = 0
	OLD_RECEIVED = 0
	DELTA_RECEIVED = 0
	for i in range(1,21):
		time.sleep(0.5)
		LOCK.acquire()
	#	print("Delta Received : %d" % DELTA_RECEIVED)
		DELTA_RECEIVED = TOTAL_RECEIVED - OLD_RECEIVED
		OLD_RECEIVED = TOTAL_RECEIVED
		LOCK.release()
		currentSpeed = DELTA_RECEIVED / 0.5
	#	maxSpeed = calcMaxSpeed(maxSpeed,DELTA_RECEIVED,0.5)
	#	maxSpeed = max(maxSpeed,currentSpeed)
	#	if (maxSpeed not in maxSpeedList):
		maxSpeedList.append(currentSpeed)
	#	print("maxSpeed : %.2f" % (maxSpeed / 1024 / 1024))
		print("\r[" + "="*i + "> [%d%%/100%%] [%.2f MB/s]" % (int(i * 5),currentSpeed / 1024 / 1024),end='')
		if (EXIT_FLAG):
			break
	print("\r[" + "="*i + "] [100%%/100%%] [%.2f MB/s]" % (currentSpeed / 1024 / 1024),end='\n')
	EXIT_FLAG = True
	for i in range(0,10):
		time.sleep(0.1)
		if (MAX_TIME != 0):
			break
	if (MAX_TIME == 0):
		logger.error("Socket Test Error !")
		return(0,0)
	restoreSocket()
	rawSpeedList = copy.deepcopy(maxSpeedList)
	maxSpeedList.sort()
#	print (maxSpeedList)
	if (len(maxSpeedList) > 12):
		msum = 0
		for i in range(12,len(maxSpeedList) - 2):
			msum += maxSpeedList[i]
		maxSpeed = (msum / (len(maxSpeedList) - 2 - 12))
	else:
		maxSpeed = currentSpeed
#	print(maxSpeed / 1024 / 1024)
	logger.info("Fetched {:.2f} KB in {:.2f} s.".format(TOTAL_RECEIVED / 1024,MAX_TIME))
	return (TOTAL_RECEIVED / MAX_TIME,maxSpeed,rawSpeedList,TOTAL_RECEIVED)

if (__name__ == "__main__"):
	res = speedTestSocket(1080)
	print(res[0] / 1024 / 1024,res[1] / 1024 / 1024)

