#coding:utf-8

config = {
	"VERSION":"2.4.6",
	"WEB_API_VERSION":"0.4.3",
	"localAddress":"127.0.0.1",
	"localPort":1087,
	"excludeRemarks":[
		"剩余流量",
		"到期时间",
		"过期时间"
	],
	"web":{
		"listen":"127.0.0.1",
		"port":10870,
		"token":""
	},
	"exportResult":{
		"hideMaxSpeed":True,
		"uploadResult":False,
		"font":"./resources/fonts/SourceHanSansCN-Medium.otf",
		"colors":[
			{
				"name":"origin",
				"colors":{
					"0.064":[128,255,0],
					"0.512":[255,255,0],
					"4.0":[255,128,192],
					"16.0":[255,0,0]
				}
			},
			{
				"name":"chunxiaoyi",
				"colors":{
					"0.064":[102,255,102],
					"0.512":[255,255,102],
					"4.0":[255,178,102],
					"16.0":[255,102,102],
					"24.0":[226,140,255],
					"32.0":[102,204,255],
					"40.0":[102,102,255]
				}
			},
			{
				"name":"chunxiaoyi2",
				"colors":{
					"0.064":[153,255,153],
					"1.0":[102,255,102],
					"4.0":[255,228,191],
					"8.0":[255,191,102],
					"16.0":[255,140,140],
					"24.0":[255,63,63],
					"32.0":[255,0,0],
					"40.0":[165,0,0]
				}
			}
		]
	},
	"uploadResult":{
		"apiToken":"",
		"server":"",
		"remark":"Example Remark."
	},
	"speedtestsocket":{
		"maxThread":6,	#Thread count
		"buffer":4096,	#Buffer size,bytes
		"skipRuleMatch":False,
		"rules":[
	#		{
	#			"mode":"match_isp", #match_isp or match_location
	#			"ISP":"Microsoft Corporation",
	#			"tag":"Cachefly"
	#		},
			{
				"mode":"match_isp",
				"ISP":"Google LLC",
				"tag":"Default"
			}
	#		{
	#			"mode":"match_location",
	#			"countries":[	#Country Code,for example: HK, US, JP etc.
	#			],
	#			"continent":"EU",
	#			"tag":"Hetzner_DE"
	#		},
	#		{
	#			"mode":"match_location",
	#			"countries":[	#Country Code,for example: HK, US, JP etc.
	#				"HK","SG"
	#			],
	#			"continent":"",
	#			"tag":"Linode_SG"
	#		}
		],
		"downloadLinks":[
			{
				"link":"https://download.microsoft.com/download/2/2/A/22AA9422-C45D-46FA-808F-179A1BEBB2A7/office2007sp3-kb2526086-fullfile-en-us.exe",
				"fileSize":350,	#File size,MBytes
				"tag":"Not"
			},
			{
				"link":"https://cachefly.cachefly.net/100mb.test",
				"fileSize":100,	#File size,MBytes
				"tag":"Default"
			},
			{
				"tag":"Hetzner_DE",
				"link":"https://speed.hetzner.de/1GB.bin",
				"fileSize":1000	#File size,MBytes
			},
			{
				"tag":"Linode_SG",
				"link":"http://speedtest.singapore.linode.com/100MB-singapore.bin",
				"fileSize":100	#File size,MBytes
			}
			
		]
	}
}

