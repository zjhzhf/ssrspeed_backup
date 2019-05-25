# coding:utf-8

import copy
	
V2RayBaseConfig = {
	"remarks": "",
	"group": "N/A",
	"server": "",
	"server_port": "",
	"log": {"access": "", "error": "", "loglevel": "warning"},
	"inbounds": [
		{
			"port": 1087,
			"listen": "127.0.0.1",
			"protocol": "socks",
			"sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
			"settings": {"auth": "noauth", "udp": True, "ip": None, "clients": None},
			"streamSettings": None,
		}
	],
	"outbounds": [
		{
			"tag": "proxy",
			"protocol": "vmess",
			"settings": {
				"vnext": [
					{
						"address": "",
						"port": 1,
						"users": [
							{"id": "", "alterId": 0, "email": "", "security": "auto"}
						],
					}
				],
				"servers": None,
				"response": None,
			},
			"streamSettings": {
				"network": "",
				"security": "",
				"tlsSettings": {},
				"tcpSettings": {},
				"kcpSettings": {},
				"wsSettings": {},
				"httpSettings": {},
				"quicSettings": {},
			},
			"mux": {"enabled": True},
		},
		{
			"tag": "direct",
			"protocol": "freedom",
			"settings": {"vnext": None, "servers": None, "response": None},
			"streamSettings": {},
			"mux": {},
		},
		{
			"tag": "block",
			"protocol": "blackhole",
			"settings": {"vnext": None, "servers": None, "response": {"type": "http"}},
			"streamSettings": {},
			"mux": {},
		},
	],
	"dns": {},
	"routing": {"domainStrategy": "IPIfNonMatch", "rules": []},
}

tcpSettingsObject = {
	"connectionReuse": True,
	"header": {
		"type": "http",
		"request": {
			"version": "1.1",
			"method": "GET",
			"path": ["/pathpath"],
			"headers": {
				"Host": ["hosthost.com", "test.com"],
				"User-Agent": [
					"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
					"Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.109 Mobile/14A456 Safari/601.1.46",
				],
				"Accept-Encoding": ["gzip, deflate"],
				"Connection": ["keep-alive"],
				"Pragma": "no-cache",
			},
		},
		"response": None,
	},
}

quicSettingsObject = {
	"security": "none",
	"key": "",
	"header": {
		"type": "none",
		"request": None,
		"response": None
	}
}
httpSettingsObject = {
	"path": "",
	"host": [
		"aes-128-gcm"
	]
}
webSocketSettingsObject = {
	"connectionReuse": True,
	"path": "",
	"headers": {
		"Host": ""
	}
}

tlsSettingsObject = {
	"allowInsecure": True,
	"serverName": ""
}

def getTlsSettingsObject():
	return copy.deepcopy(tlsSettingsObject)

def getWebSocketSettingsObject():
	return copy.deepcopy(webSocketSettingsObject)

def getHttpSettingsObject():
	return copy.deepcopy(httpSettingsObject)

def getTcpSettingsObject():
	return copy.deepcopy(tcpSettingsObject)

def getQuicSettingsObject():
	return copy.deepcopy(quicSettingsObject)

def getConfig():
	return copy.deepcopy(V2RayBaseConfig)

