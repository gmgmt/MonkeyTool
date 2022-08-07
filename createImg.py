#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author   : chuanwen.peng
# @Time     : 2022/5/10 11:29
# @File     : imgg.py
# @Project  : money_gui
"""
import base64

open_icon = open("logo.ico", "rb")
b64str = base64.b64encode(open_icon.read())  # 以base64的格式读出
open_icon.close()
write_data = "img=%s" % b64str
f = open("logo.py", "w+")  # 将上面读出的数据写入到qq.py的img数组中
f.write(write_data)
f.close()
