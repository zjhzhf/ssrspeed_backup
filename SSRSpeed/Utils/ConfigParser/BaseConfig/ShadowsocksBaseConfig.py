#coding:utf-8

import copy

ShadowsocksConfig = {
	"server":"",
	"server_port":-1,
	"method":"",
	"protocol":"",
	"obfs":"",
	"plugin":"",
	"password":"",
	"protocol_param":"",
	"obfsparam":"",
	"plugin_opts":"",
	"plugin_args":"",
	"remarks":"",
	"group":"N/A",
	"timeout":0,
	"local_port":0,
	"local_address":"",
	"fastopen":False
}

def getConfig():
	return copy.deepcopy(ShadowsocksConfig)


