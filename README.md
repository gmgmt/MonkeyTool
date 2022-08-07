# MonkeyTool
1、使用说明 -V1.1.4
![工具总览](https://github.com/gmgmt/MonkeyTool/blob/main/image/summary.jpg)
点击指导手册之后，点击弹窗是，即可跳转至本文档
![帮助](http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools_phone/-/raw/main/image/help.jpg)
操作步骤
![步骤](http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools_phone/-/raw/main/image/step.jpg)
1、刷新设备，未避免拔插设备的问题，开始前手动点击刷新，可查看设备连接是否正常
2、根据刷新的设备列表选择对应设备
3、查询设备信息
4、选择测试包名，第三步选择设置之后，会拉取所有包列表（支持模糊搜索。可多选，选择之后，左键点击会在右边包集合文本框中出现）
![选择框](http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools_phone/-/blob/main/image/select.jpg)
5、根据个人设置，填写对应参数，选择报告和日志文件夹，默认在工具根目录
![日志路径](http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools_phone/-/raw/main/image/logFile.jpg)
6、点击启动Monkey测试
7、测试完成后，会弹窗提示，点击是打开报告路径
![状态](http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools_phone/-/raw/main/image/status.jpg)
2、日志&报告说明
1、过程日志：会在文件夹下生成report目录，下面会有logcat.log、monkey.log、traces.log。
![日志目录](http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools_phone/-/raw/main/image/report.PNG)
2、报告：会在目录下生成序列号目录，下面会有excel报告
注意：选择几个测试的包，就会生成多少个excel文件，还会有一个result.xlsx汇总文件。
![报告](http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools_phone/-/raw/main/image/excel.PNG)

报告大致内容如下：
![报告详情](http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools_phone/-/raw/main/image/Excel2.PNG)
3、工具源码及流程介绍
1、框架结构：
MonkeyTools:
   - MonkeyTools.py:    主入口文件
   - CreateImg.py:    打包文件图标，生成base64编码文件
   - BaseCaseEmnu.py:    异常日志匹配和抓取
   - getInfo.py:    获取手机基本信息以及adb基本命令封装
   - logger2.py:    二次封装logger类，将console打印日志保存到项目根目录，方便后续分析问题
   - logo.py：    CreateImg.py生成的base64编码文件
   - OperateFile.py：    各类文件操作，报告生成
过程文件：
   - info/：    过程数据文件，抓取各类CPU、MEM、FPS、NET信息
   - monkey1.ini：    根据用户填写数据，生成ini配置文件
   - whitelist.txt:    白名单列表，如果用户选取多个包名，则会自动生成文件
结果文件：
   report/：    报告生成目录
        - 时间戳+设备串号/
            - 时间戳+monkey_report.xlsx：    如果选择多个包，则会生成多个xlsx文件，并且会有一个result.xlsx文件汇总
        - 时间戳+monkey_log/
            - uuid+logcat.log:    logcat文件
            - uuid+monkey.log：    monkey日志
            - uuid+traces.log:    trace.log文件

1、框架结构：

MonkeyTools:
   - MonkeyTools.py:    主入口文件
   - CreateImg.py:    打包文件图标，生成base64编码文件
   - BaseCaseEmnu.py:    异常日志匹配和抓取
   - getInfo.py:    获取手机基本信息以及adb基本命令封装
   - logger2.py:    二次封装logger类，将console打印日志保存到项目根目录，方便后续分析问题
   - logo.py：    CreateImg.py生成的base64编码文件
   - OperateFile.py：    各类文件操作，报告生成
过程文件：
   - info/：    过程数据文件，抓取各类CPU、MEM、FPS、NET信息
   - monkey1.ini：    根据用户填写数据，生成ini配置文件
   - whitelist.txt:    白名单列表，如果用户选取多个包名，则会自动生成文件
结果文件：
   report/：    报告生成目录
        - 时间戳+设备串号/
            - 时间戳+monkey_report.xlsx：    如果选择多个包，则会生成多个xlsx文件，并且会有一个result.xlsx文件汇总
        - 时间戳+monkey_log/
            - uuid+logcat.log:    logcat文件
            - uuid+monkey.log：    monkey日志
            - uuid+traces.log:    trace.log文件
源码地址：

http://182.150.22.16:7788/gitlab-instance-ac781f12/monkeytools

打包命令：

pyinstaller -F MonkeyTool.py -n MonkeyTool_V1.0.3
pyinstaller -F MonkeyTools.py BaseCashEmnu.py createImg.py getInfo.py logger2.py OperateFile.py -n MonkeyTool_V1.0.4 -p D:\workspace\work\monkeytools\venv\Lib\site-packages
