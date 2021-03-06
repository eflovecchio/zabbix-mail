#!/usr/bin/python3

import sys
import zbx_ex_setting
from zbx_api import ZabbixImage
from zbx_sender import SendEmail

item_id = int(sys.argv[1])

server = zbx_ex_setting.zbx_server
api_user = zbx_ex_setting.zbx_api_user
api_pass = zbx_ex_setting.zbx_api_pass

zbx_image = ZabbixImage(server=server, api_user=api_user, api_pass=api_pass)
try:
    zbx_image.login()
except BaseException:
    pass

# #Parse event_id
# i = 0
# line_count = 0
# for line in sys.argv[3].split('\n'):
#
# 	i += 1
# 	if line.find('zbxgraph') == 0:
# 		event_id = line.split(' ')[1]
# 		line_count = i
#
# #Parce head
# body = sys.argv[3].split('\n')
# print(body, line_count)
# print('\n'.join(body[0:2]))
# print('\n'.join(body[3:-1]))


image_height = zbx_ex_setting.zbx_graph_height
image_width = zbx_ex_setting.zbx_graph_width
image_period = zbx_ex_setting.zbx_graph_period
zbx_image.graph_get(item_id, image_period, None, image_width, image_height)
#zbx_image.graph_get(event_id, image_period, None, image_width, image_height)

email = SendEmail()
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
