#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author   : chuanwen.peng
# @Time     : 2022/5/16 9:42
# @File     : getInfo.py
# @Project  : MonkeyTools
"""
import math
import os
import re
import subprocess
import time

from wsgiref.validate import validator
from subprocess import Popen, PIPE
from OperateFile import OperatePickle
from logger2 import Logger

mylogger = Logger(logger='TestMyLog').getlog()

PATH = lambda p: p


def call_adb(command):
    command_result = ''
    command_text = 'adb %s' % command
    mylogger.info(command_text)
    results = os.popen(command_text, "r")
    while 1:
        line = results.readline()
        if not line:
            break
        command_result += line
    results.close()
    return command_result


def attached_devices():
    result = os.popen('adb devices -l | findstr "model"').readlines()
    if result:
        device = []
        for each in result:
            device.append(each.split()[0])
        return device


def get_all_pkg(id, act=0):
    """
    获取所有包名
    :param target_app: 目标app包名
    :return: bool
    """
    string = call_adb("-s %s shell pm list packages" % id)
    if act:
        string = string[:-1]
        pag_list = string.replace("package:", '').split('\n')
    else:
        pag_list = string.split('\n')
    return pag_list


def modified(name):
    reu = list(os.popen(name).readlines())
    return re.findall('.*', reu[0])[0]  # ([^\s\\\]+)


def getModel(devices):
    result = {}
    cmd = "adb -s " + devices + " shell getprop ro.product.vendor.name"
    phone_models = modified(cmd)
    return phone_models


def get_men_total(devices):
    cmd = "adb -s " + devices + " shell cat /proc/meminfo"
    mylogger.info(cmd)
    output = subprocess.check_output(cmd).split()
    # item = [x.decode() for x in output]
    return int(output[1].decode())


# # 得到几核cpu
def get_cpu_kel(devices):
    cmd = "adb -s " + devices + " shell cat /proc/cpuinfo"
    mylogger.info(cmd)
    output = subprocess.check_output(cmd).split()
    sitem = ".".join([x.decode() for x in output])  # 转换为string
    return str(len(re.findall(r"processor", sitem))) + "核"


def get_cpu_kel2(devices):
    cmd = "adb -s " + devices + " shell cat /proc/cpuinfo"
    mylogger.info(cmd)
    output = subprocess.check_output(cmd).split()
    sitem = ".".join([x.decode() for x in output])  # 转换为string
    return len(re.findall(r"processor", sitem))


# 得到手机分辨率
def get_app_pix(devices):
    cmd = "adb -s " + devices + " shell wm size"
    mylogger.info(cmd)
    return subprocess.check_output(cmd).split()[2].decode()
    # cmd = 'adb -s %s shell dumpsys window displays | findstr init' % devices
    # mylogger.infof(cmd)
    # try:
    #     return subprocess.check_output(cmd).decode().split('=')[1].split()[0]
    # except:
    #     return 'unknown'


#
def get_phone_Kernel(devices):
    pix = get_app_pix(devices)
    men_total = get_men_total(devices)
    phone_msg = getModel(devices)
    cpu_sum = get_cpu_kel(devices)
    return phone_msg, men_total, cpu_sum, pix
    # return men_total, cpu_sum, pix


def get_phone(devices):
    bg = get_phone_Kernel(devices)
    app = {}
    # app["phone_name"] = bg[0]["phone_name"] + "_" + bg[0]["phone_model"] + "_" + bg[0]["release"]
    app["phone_name"] = bg[0]
    app["pix"] = bg[3]
    app["rom"] = bg[1]
    app["kel"] = bg[2]
    return app


def get_men(pkg_name, devices):
    try:
        cmd = "adb -s " + devices + " shell  dumpsys  meminfo %s" % pkg_name
        mylogger.info(cmd)
        output = subprocess.check_output(cmd).split()
        # mylogger.infof(output)
        s_men = ".".join([x.decode() for x in output])  # 转换为string
        mylogger.info(s_men)
        men2 = int(re.findall(r"TOTAL.(\d+)*", s_men, re.S)[0])
    except:
        men2 = 0
    OperatePickle().writeInfo(men2, PATH("./info/" + devices + "_men.pickle"))
    return men2
    # men_s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
    # for info in men_s:
    #     if len(info.split()) and info.split()[0].decode() == "TOTAL":
    #         # mylogger.infof("men="+info.split()[1].decode())
    #         men.append(int(info.split()[1].decode()))
    #         # writeInfo(int(info.split()[1].decode()), PATH("./info/" + devices + "_men.pickle"))
    #         mylogger.infof("----men----")
    #         mylogger.infof(men)
    #         return men


# 得到fps
def get_fps(pkg_name, devices):
    _adb = "adb -s " + devices + " shell dumpsys gfxinfo %s" % pkg_name
    mylogger.info(_adb)
    # results = os.popen(_adb).read().strip()
    results, b = Popen(_adb, stdout=PIPE, stderr=PIPE).communicate()
    frames = [x for x in results.decode("utf-8").split('\n') if validator(x)]
    frame_count = len(frames)
    jank_count = 0
    vsync_overtime = 0
    render_time = 0
    for frame in frames:
        time_block = re.split(r'\s+', frame.strip())
        if len(time_block) == 3:
            try:
                render_time = float(time_block[0]) + float(time_block[1]) + float(time_block[2])
            except Exception as e:
                render_time = 0

        '''
        当渲染时间大于16.67，按照垂直同步机制，该帧就已经渲染超时
        那么，如果它正好是16.67的整数倍，比如66.68，则它花费了4个垂直同步脉冲，减去本身需要一个，则超时3个
        如果它不是16.67的整数倍，比如67，那么它花费的垂直同步脉冲应向上取整，即5个，减去本身需要一个，即超时4个，可直接算向下取整

        最后的计算方法思路：
        执行一次命令，总共收集到了m帧（理想情况下m=128），但是这m帧里面有些帧渲染超过了16.67毫秒，算一次jank，一旦jank，
        需要用掉额外的垂直同步脉冲。其他的就算没有超过16.67，也按一个脉冲时间来算（理想情况下，一个脉冲就可以渲染完一帧）

        所以FPS的算法可以变为：
        m / （m + 额外的垂直同步脉冲） * 60
        '''
        if render_time > 16.67:
            jank_count += 1
            if render_time % 16.67 == 0:
                vsync_overtime += int(render_time / 16.67) - 1
            else:
                vsync_overtime += int(render_time / 16.67)

    _fps = int(frame_count * 60 / (frame_count + vsync_overtime))
    OperatePickle().writeInfo(_fps, PATH("./info/" + devices + "_fps.pickle"))

    # return (frame_count, jank_count, fps)
    mylogger.info("-----fps------")
    mylogger.info(_fps)


def get_battery(devices):
    try:
        cmd = "adb -s " + devices + " shell dumpsys battery"
        mylogger.info(cmd)
        output = subprocess.check_output(cmd).split()
        # _batter = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
        #                            stderr=subprocess.PIPE).stdout.readlines()
        st = ".".join([x.decode() for x in output])  # 转换为string
        mylogger.info(st)
        battery2 = int(re.findall(r"level:.(\d+)*", st, re.S)[0])
    except:
        battery2 = 90
    OperatePickle().writeInfo(battery2, PATH("./info/" + devices + "_battery.pickle"))

    return battery2


def get_pid(pkg_name, devices):
    cmd = "adb -s " + devices + " shell ps | findstr " + pkg_name
    mylogger.info("----get_pid-------")
    mylogger.info(cmd)
    pid = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).stdout.readlines()
    for item in pid:
        if item.split()[8].decode() == pkg_name:
            return item.split()[1].decode()


def get_flow(pid, type, devices):
    # pid = get_pid(pkg_name)
    upflow = downflow = 0
    if pid is not None:
        cmd = "adb -s " + devices + " shell cat /proc/" + pid + "/net/dev"
        mylogger.info(cmd)
        _flow = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).stdout.readlines()
        for item in _flow:
            if type == "wifi" and item.split()[0].decode() == "wlan0:":  # wifi
                # 0 上传流量，1 下载流量
                upflow = int(item.split()[1].decode())
                downflow = int(item.split()[9].decode())
                mylogger.info("------flow---------")
                mylogger.info(upflow)
                break
            if type == "gprs" and item.split()[0].decode() == "rmnet0:":  # gprs
                mylogger.info("-----flow---------")
                upflow = int(item.split()[1].decode())
                downflow = int(item.split()[9].decode())
                mylogger.info(upflow)
                break

    OperatePickle().writeFlowInfo(upflow, downflow, PATH("./info/" + devices + "_flow.pickle"))


def totalCpuTime(devices):
    user = nice = system = idle = iowait = irq = softirq = 0
    '''
    user:从系统启动开始累计到当前时刻，处于用户态的运行时间，不包含 nice值为负进程。
    nice:从系统启动开始累计到当前时刻，nice值为负的进程所占用的CPU时间
    system 从系统启动开始累计到当前时刻，处于核心态的运行时间
    idle 从系统启动开始累计到当前时刻，除IO等待时间以外的其它等待时间
    iowait 从系统启动开始累计到当前时刻，IO等待时间(since 2.5.41)
    irq 从系统启动开始累计到当前时刻，硬中断时间(since 2.6.0-test4)
    softirq 从系统启动开始累计到当前时刻，软中断时间(since 2.6.0-test4)
    stealstolen  这是时间花在其他的操作系统在虚拟环境中运行时（since 2.6.11）
    guest 这是运行时间guest 用户Linux内核的操作系统的控制下的一个虚拟CPU（since 2.6.24）
    '''

    cmd = "adb -s " + devices + " shell cat /proc/stat"
    mylogger.info(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    res = output.split()

    for info in res:
        if info.decode() == "cpu":
            user = res[1].decode()
            nice = res[2].decode()
            system = res[3].decode()
            idle = res[4].decode()
            iowait = res[5].decode()
            irq = res[6].decode()
            softirq = res[7].decode()
            mylogger.info("user=" + user)
            mylogger.info("nice=" + nice)
            mylogger.info("system=" + system)
            mylogger.info("idle=" + idle)
            mylogger.info("iowait=" + iowait)
            mylogger.info("irq=" + irq)
            mylogger.info("softirq=" + softirq)
            result = int(user) + int(nice) + int(system) + int(idle) + int(iowait) + int(irq) + int(softirq)
            mylogger.info("totalCpuTime" + str(result))
            return result


def processCpuTime(pid, devices):
    '''

    pid     进程号
    utime   该任务在用户态运行的时间，单位为jiffies
    stime   该任务在核心态运行的时间，单位为jiffies
    cutime  所有已死线程在用户态运行的时间，单位为jiffies
    cstime  所有已死在核心态运行的时间，单位为jiffies
    '''
    utime = stime = cutime = cstime = 0
    try:
        cmd = "adb -s " + devices + " shell cat /proc/" + pid + "/stat"
        mylogger.info(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        res = output.split()

        utime = res[13].decode()
        stime = res[14].decode()
        cutime = res[15].decode()
        cstime = res[16].decode()
        mylogger.info("utime=" + utime)
        mylogger.info("stime=" + stime)
        mylogger.info("cutime=" + cutime)
        mylogger.info("cstime=" + cstime)
        result = int(utime) + int(stime) + int(cutime) + int(cstime)
        mylogger.info("processCpuTime=" + str(result))
    except:
        result = 0
    return result


def cpu_rate(pid, cpukel, devices):
    # pid = get_pid(pkg_name)
    processCpuTime1 = processCpuTime(pid, devices)
    time.sleep(1)
    processCpuTime2 = processCpuTime(pid, devices)
    processCpuTime3 = processCpuTime2 - processCpuTime1

    totalCpuTime1 = totalCpuTime(devices)
    time.sleep(1)
    totalCpuTime2 = totalCpuTime(devices)
    totalCpuTime3 = (totalCpuTime2 - totalCpuTime1) * cpukel
    mylogger.info("totalCpuTime3=" + str(totalCpuTime3))
    mylogger.info("processCpuTime3=" + str(processCpuTime3))

    cpu = 100 * (processCpuTime3) / (totalCpuTime3)
    OperatePickle().writeInfo(cpu, PATH("./info/" + devices + "_cpu.pickle"))
    mylogger.info("--------cpu--------")
    mylogger.info(cpu)


# total 是rom容量
def avgMen(men, total):
    if len(men):
        _men = [math.ceil(((men[i]) / total) * 1024) for i in range(len(men))]
        mylogger.info(_men)
        return str(math.ceil(sum(_men) / len(_men))) + "M"
    return "0"


def avgCpu(cpu):
    if len(cpu):
        resutl = "%.1f" % (sum(cpu) / len(cpu))
        return str(math.ceil(float(resutl) * 10)) + "%"
    return "0%"


def avgFps(fps):
    if len(fps):
        return '%.2f' % float(str(math.ceil(sum(fps) / len(fps))))
    return 0.00


def maxMen(men):
    if len(men):
        mylogger.info("men=" + str(men))
        return str(math.ceil((max(men)) / 1024)) + "M"
    return "0M"


def maxCpu(cpu):
    mylogger.info("maxCpu=" + str(cpu))
    if len(cpu):
        result = "%.1f" % max(cpu)
        return str(math.ceil(float(result) * 10)) + "%"
    return "0%"


def maxFps(fps):
    return str(max(fps))


def maxFlow(flow):
    mylogger.info("---maxFlow111----------")
    mylogger.info(flow)
    _flowUp = []
    _flowDown = []
    for i in range(len(flow[0])):
        if i + 1 == len(flow[0]):
            break
        _flowUp.append(math.ceil((flow[0][i + 1] - flow[0][i]) / 1024))
        mylogger.info("---maxFlow2222---------")
        mylogger.info(_flowUp)
    for i in range(len(flow[1])):
        if i + 1 == len(flow[1]):
            break
        _flowDown.append(math.ceil((flow[1][i + 1] - flow[1][i]) / 1024))
        mylogger.info("---maxFlow3333---------")
        mylogger.info(_flowDown)
    if _flowUp:
        maxFpsUp = str(max(_flowUp)) + "KB"  # 上行流量
    else:
        maxFpsUp = "0"
    if _flowDown:
        maxFpsDown = str(max(_flowDown)) + "KB"  # 下行流量
    else:
        maxFpsDown = "0"
    return maxFpsUp, maxFpsDown


def avgFlow(flow):
    _flowUp = []
    _flowDown = []
    for i in range(len(flow[0])):
        if i + 1 == len(flow[0]):
            break
        _flowUp.append((flow[0][i + 1] - flow[0][i]) / 1024)

    for i in range(len(flow[1])):
        if i + 1 == len(flow[1]):
            break
        _flowDown.append((flow[1][i + 1] - flow[1][i]) / 1024)
    # 当测试时间较短时，会引发除0错误，这里先做规避，后面再解决
    # avgFpsUp = str(math.ceil(sum(_flowUp) / len(_flowUp))) + "KB"
    # avgFpsDown = str(math.ceil(sum(_flowDown) / len(_flowDown))) + "KB"
    try:
        avgFpsUp = str(math.ceil(sum(_flowUp) / len(_flowUp))) + "KB"
    except ZeroDivisionError:
        avgFpsUp = '测试时间太短'
    try:
        avgFpsDown = str(math.ceil(sum(_flowDown) / len(_flowDown))) + "KB"
    except ZeroDivisionError:
        avgFpsDown = '测试时间太短'
    return avgFpsUp, avgFpsDown
