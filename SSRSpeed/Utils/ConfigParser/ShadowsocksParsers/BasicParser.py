#coding:utf-8

import logging
import json
import urllib.parse
import copy

import SSRSpeed.Utils.b64plus as b64plus

logger = logging.getLogger("Sub")

class ParserShadowsocksBasic(object):
	def __init__(self,baseConfig):
		self.__configList = []
		self.__baseConfig = baseConfig

	def __getShadowsocksBaseConfig(self):
		return copy.deepcopy(self.__baseConfig)

	def __parseLink(self,link):
		_config = self.__getShadowsocksBaseConfig()

		if (link[:5] != "ss://"):
			logger.error("Unsupport link : %s" % link)
			return None

		urlData = urllib.parse.unquote(link)
		urlResult = urllib.parse.urlparse(urlData)
		decoded = b64plus.decode(urlResult.netloc[:urlResult.netloc.find("@")]).decode("utf-8")
		method = decoded.split(":")[0]
		password = decoded.split(":")[1]
		addrPort = urlResult.netloc[urlResult.netloc.find("@") + 1:].split(":")
		remarks = urlResult.fragment
		if (len(addrPort) != 2):
			return None
		serverAddr = addrPort[0]
		serverPort = int(addrPort[1])

		queryResult = urlResult.query

		plugin = ""
		pluginOpts = ""
		group = "N/A"

		if ("group=" in queryResult):
			index1 = queryResult.find("group=") + 6
			index2 = queryResult.find("&",index1)
			group = b64plus.decode(queryResult[index1:index2 if index2 != -1 else None]).decode("utf-8")
		if ("plugin=" in queryResult):
			index1 = queryResult.find("plugin=") + 7
			index2 = queryResult.find(";",index1)
			plugin = queryResult[index1:index2]
			index3 = queryResult.find("&",index2)
			pluginOpts = queryResult[index2 + 1:index3 if index3 != -1 else None]

		_config["server"] = serverAddr
		_config["server_port"] = serverPort
		_config["method"] = method
		_config["password"] = password
		_config["group"] = group
		_config["remarks"] = remarks
		_config["plugin"] = plugin
		_config["plugin_opts"] = pluginOpts

		if (_config["remarks"] == ""):
			_config["remarks"] = _config["server"]

		return _config

	def parseSubsConfig(self,links):
		for link in links:
			link = link.strip()
			cfg = self.__parseLink(link)
			if (cfg):
				self.__configList.append(cfg)
		logger.info("Read {} config(s).".format(len(self.__configList)))
		return self.__configList

	def parseGuiConfig(self,filename):
		with open(filename,"r",encoding="utf-8") as f:
			try:
				configs = json.load(f)["configs"]
			except:
				logger.exception("Not ShadowsocksBasic file.")
				f.close()
				return False
			f.close()
			for item in configs:
				_dict = self.__getShadowsocksBaseConfig()
				_dict["server"] = item["server"]
				_dict["server_port"] = int(item["server_port"])
				_dict["password"] = item["password"]
				_dict["method"] = item["method"]
				_dict["plugin"] = item.get("plugin","")
				_dict["plugin_opts"] = item.get("plugin_opts","")
				_dict["plugin_args"] = item.get("plugin_args","")
				_dict["remarks"] = item.get("remarks",item["server"])
				_dict["group"] = item.get("group","N/A")
				_dict["fast_open"] = False
				self.__configList.append(_dict)
			f.close()
		logger.info("Read {} config(s).".format(len(self.__configList)))
		return self.__configList

