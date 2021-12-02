# -*- coding: utf-8 -*-
import base64
import sys
import os
import requests
import zbx_ex_setting
from zbx_sender import SendEmail
from zbx_api import ZabbixImage
from email.mime.image import MIMEImage
#test
from bs4 import BeautifulSoup
from urllib import request
import urllib.parse
import urllib.error
from urllib.request import urlopen
import urllib.request
from requests import Session
import shutil
import urllib


class ZabbixImage(object):
    """For get graph image"""

    def __init__(self, server, api_user, api_pass):
        super(ZabbixImage, self).__init__()
        # self.arg = arg
        self.server = server
        self.api_user = api_user
        self.api_pass = api_pass
        self.verify = True
        self.cookie = None
        self.res_img = None
        self.res_url = None

    #Loguea en zabbix
    def login(self):

        if not self.verify:
            requests.package.urllib3.disable_warnings()

        data_api = {"name": self.api_user, "password": self.api_pass, "enter": "Sign in"}
        req_cookie = requests.post(self.server + "/", data=data_api, verify=self.verify)
        cookie = req_cookie.cookies

        if len(req_cookie.history) > 1 and req_cookie.history[0].status_code == 302:
            print_message("Probably the server in your config file has not full URL")

        if not cookie:
            print_message("authorization failed")
            cookie = None

        self.cookie = cookie

        


    #Get URL graph para pegarlo como <img> de html en el mail
    def graph_get(self, itemid, period, title, width, height):
        # title = requests.utils.quote(title)
        urltest = 'http://10.0.100.100/zabbix//chart.php?from=now-1h&to=now&itemids%5B0%5D=36652&type=0&profileIdx=web.item.graph.filter&profileIdx2=36652&width=1367&height=200&_=v6lncq74&screenid='
        zbx_url_url = self.server + "/history.php?action=showgraph&itemids%5B%5D={0}".format(itemid)

        zbx_img_url = self.server + "/chart.php?period={1}" \
                                    "&itemids%5B0%5D={0}" \
                                    "&type=0&updateProfile=1" \
                                    "&width={3}" \
                                    "&height={4}".format(itemid, period, title, width, height)

        print_message(zbx_img_url)  

        res = requests.get(urltest, cookies=self.cookie)
        res_code = res.status_code
        if res_code == 404:
            print_message("can`t get image from '{0}'".format(zbx_img_url))
            return False

        self.res_img = '<img src="data:image/png;base64,' + base64.b64encode(res.content).decode() + '" alt=graph />'
        self.res_url = zbx_url_url

        #Descarga la imagen indicada en el link
        #Solo descarga la imagen si es un usuario con permisos guest sobre ese equipo
        graph_name = "local-filename.png"
        urllib.request.urlretrieve(urltest , graph_name)
        response = requests.get(urltest)
        
        # self.res_img = '<img src="data:image/png;base64,' + base64.b64encode(res.content).decode() + '" alt=graph>'
        self.res_img = '<img src="'+ graph_name + '"' +' alt=graph>'
        self.res_url = zbx_url_url     
        print(self.res_img)
        print(self.res_url)

        

def print_message(string):
    string = str(string) + "\n"
    filename = sys.argv[0].split("/")[-1]
    # The first argument, sys.argv[0], is always the name of the script and sys.argv[1] is the first argument passed to the script.
    sys.stderr.write(filename + ": " + string)

if __name__ == '__main__':
    #ingresa al zabbix como usuario
    server = zbx_ex_setting.zbx_server
    api_user = zbx_ex_setting.zbx_api_user
    api_pass = zbx_ex_setting.zbx_api_pass
    zbx_image = ZabbixImage(server=server, api_user=api_user, api_pass=api_pass)

    try:
        zbx_image.login()
        
    except:
        pass

    #saca el parametro del item_ID y genera la imagen-------------
    # item_id = int(sys.argv[1])
    item_id = zbx_ex_setting.item_id
    zbx_image.graph_get(item_id, zbx_ex_setting.zbx_graph_period, None, zbx_ex_setting.zbx_graph_width, zbx_ex_setting.zbx_graph_height)
    email = SendEmail()
    #inicio de sesion en el mail
    email.mail_from = zbx_ex_setting.email_from
    email.mail_user = zbx_ex_setting.email_username
    email.mail_pass = zbx_ex_setting.email_password
                                                            #email.mail_to = sys.argv[1]
    email.mail_to = zbx_ex_setting.email_to
                                                            #email.mail_subject = sys.argv[2]
    email.mail_subject = zbx_ex_setting.email_subject
    email.mail_smtp_server = zbx_ex_setting.email_smtp_server
    email.company = zbx_ex_setting.company

    email.mail_head = 'head'
    #'<br>\n'.join(body[0:line_count - 1])
    email.mail_footer = 'footer'
    #'<br>\n'.join(body[line_count + 1:-1])
    email.mail_graph = zbx_image.res_img
    email.mail_url = zbx_image.res_url

    email.send()
