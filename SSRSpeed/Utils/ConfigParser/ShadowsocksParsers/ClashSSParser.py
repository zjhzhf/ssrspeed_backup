#coding:utf-8

import logging
import yaml
import copy
import json

logger = logging.getLogger("Sub")

class ParserShadowsocksClash(object):
	def __init__(self,baseConfig):
		self.__configList = []
		self.__baseConfig = baseConfig

	def __getShadowsocksBaseConfig(self):
		return copy.deepcopy(self.__baseConfig)

	def __parseConfig(self,clashCfg):
		for cfg in clashCfg["Proxy"]:
			if (cfg.get("type","N/A").lower() != "ss"):
				logger.info("Config {}, type {} not support.".format(
					cfg["name"],
					cfg["type"]
					)
				)
				continue

			_dict = self.__getShadowsocksBaseConfig()
			_dict["server"] = cfg["server"]
			_dict["server_port"] = int(cfg["port"])
			_dict["password"] = cfg["password"]
			_dict["method"] = cfg["cipher"]
			_dict["remarks"] = cfg.get("name",cfg["server"])
			_dict["group"] = cfg.get("group","N/A")
			_dict["fast_open"] = False

			plugin = cfg.get("plugin","")
			if (plugin == "obfs"):
				plugin = "obfs-local"
			elif (plugin == "v2ray-plugin"):
				logger.warn("V2Ray plugin not supported.")
				logger.info("Skip {} - {}".format(_dict["group"],_dict["remarks"]))
				continue
			pOpts = cfg.get("plugin-opts",{})
			pluginOpts = ""
			pluginOpts += ("obfs={}".format(pOpts.get("mode","")) if pOpts.get("mode","") else "")
			pluginOpts += (";obfs-host={}".format(pOpts.get("host","")) if pOpts.get("host","") else "")

			_dict["plugin"] = plugin
			_dict["plugin_opts"] = pluginOpts
			_dict["plugin_args"] = ""
			
			self.__configList.append(_dict)

		logger.debug("Read {} configs.".format(
			len(self.__configList)
			)
		)

	def parseSubsConfig(self,config):
		try:
			clashCfg = yaml.load(config,Loader=yaml.FullLoader)
		except:
			logger.exception("Not Clash Subscription.")
			return False

		self.__parseConfig(clashCfg)
		logger.debug("Read {} configs.".format(
			len(self.__configList)
			)
		)
		return self.__configList

	def parseGuiConfig(self,filename):
		with open(filename,"r+",encoding="utf-8") as f:
			try:
				clashCfg = yaml.load(f,Loader=yaml.FullLoader)
			except:
				logger.exception("Not Clash config.")
				f.close()
				return False
			f.close()

		return self.__configList


