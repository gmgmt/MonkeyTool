#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# @Author   : chuanwen.peng
# @Time     : 2022/4/15 14:21
# @File     : logger2.py
# @Project  : Glass_UI
"""
import logging
import os.path
import time
from logging.handlers import RotatingFileHandler


class Logger(object):
    def __init__(self, logger):
        """指定保存日志的文件路径，日志级别，以及调用文件
        将日志存入到指定的文件中
        :paramlogger:
        """
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.INFO)
        # self.filename = filename
        rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        # rq = self.filename + '_' + rq
        logfolder = os.getcwd()+"\\report";
        if not os.path.exists(logfolder):
            os.mkdir(logfolder)
        logfolder = logfolder+"\\console";
        if not os.path.exists(logfolder):
            os.mkdir(logfolder)
        self.log_name = os.path.join(logfolder, rq + '_console.log')
        if not self.logger.handlers:
            # 创建一个handler，用于写入日志文件

            # fh = logging.FileHandler(log_name, mode='a', encoding='utf-8')
            fh = RotatingFileHandler(filename=self.log_name, maxBytes=10 * 1024 * 1024, backupCount=100,
                                     encoding='utf-8')

            fh.setLevel(logging.INFO)
            # 再创建一个handler，用于输出到控制台
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            # 定义handler的输出格式
            formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s:    %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            # 给logger添加handler
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

    def getlog(self):
        return self.logger

    def getLog_name(self):
        return self.log_name

