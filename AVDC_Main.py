#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QTextCursor, QCursor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from AVDC import *
import os
import sys
import time
import os.path
from PIL import Image
import json
from configparser import ConfigParser
from AV_Data_Capture import *
from core import *
from fanza import *
import requests
import re
import shutil
import base64


class MyMAinWindow(QMainWindow, Ui_AVDV):
    progressBarValue = pyqtSignal(int)  # 进度条信号量

    def __init__(self, parent=None):
        super(MyMAinWindow, self).__init__(parent)
        self.Ui = Ui_AVDV()  # 实例化 Ui
        self.Ui.setupUi(self)  # 初始化Ui
        self.Init_Ui()
        self.version = '3.4'
        self.m_drag = False
        self.m_DragPosition = 0
        self.Init()
        self.Load_Config()
        self.show_version()

    def Init_Ui(self):
        pix = QPixmap('AVDC-ico.png')
        self.Ui.label_ico.setScaledContents(True)
        self.Ui.label_ico.setPixmap(pix)  # 添加图标
        self.Ui.progressBar_avdc.setValue(0)  # 进度条清0
        self.progressBarValue.connect(self.set_processbar)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        # self.setWindowOpacity(0.9)  # 设置窗口透明度
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        # 控件美化
        self.Ui.widget_setting.setStyleSheet(
            '''
            QWidget#widget_setting{
                    background:#F0F8FF;
                    border-radius:20px;
                    padding:2px 4px;
            }
            QPushButton{
                    font-size:15px;
                    background:gray;
                    border:9px solid gray;
                    border-radius:15px;
                    padding:2px 4px;
            }
            
            ''')
        self.Ui.centralwidget.setStyleSheet(
            '''
            QWidget#centralwidget{
                    background:gray;
                    border:1px solid gray;
                    width:300px;
                    border-radius:20px;
                    padding:2px 4px;
            }            
            QLineEdit{
                    background:white;
                    border:1px solid white;
                    width:300px;
                    border-radius:10px;
                    padding:2px 4px;
            }            
            QTextBrowser#textBrowser_about{
                    background:white;
                    border:1px solid white;
                    width:300px;
                    border-radius:10px;
                    padding:2px 4px;
            }            
            QTextBrowser#textBrowser_warning{
                    background:gray;
                    border:1px solid gray;
                    width:300px;
                    border-radius:10px;
                    padding:2px 4px;
            }            
            QPushButton#pushButton_start_cap,#pushButton_javdb_sp,#pushButton_move_mp4,#pushButton_select_file{
                    font-size:20px;
                    background:#F0F8FF;
                    border:2px solid white;
                    width:300px;
                    border-radius:20px;
                    padding:2px 4px;
            }
            QPushButton#pushButton_save_config,#pushButton_start_javdb,#pushButton_add_actor_pic,#pushButton_show_pic_actor{
                    font-size:18px;
                    background:#F0F8FF;
                    border:2px solid white;
                    width:300px;
                    border-radius:13px;
                    padding:2px 4px;
            }
            ''')

    # ========================================================================按钮点击事件
    def Init(self):
        self.Ui.stackedWidget.setCurrentIndex(0)
        self.Ui.pushButton_close.clicked.connect(self.close_win)
        self.Ui.pushButton_min.clicked.connect(self.min_win)
        self.Ui.pushButton_main.clicked.connect(self.pushButton_main_clicked)
        self.Ui.pushButton_tool.clicked.connect(self.pushButton_tool_clicked)
        self.Ui.pushButton_setting.clicked.connect(self.pushButton_setting_clicked)
        self.Ui.pushButton_select_file.clicked.connect(self.pushButton_select_file_clicked)
        self.Ui.pushButton_about.clicked.connect(self.pushButton_about_clicked)
        self.Ui.pushButton_start_cap.clicked.connect(self.pushButton_start_cap_clicked)
        self.Ui.pushButton_save_config.clicked.connect(self.pushButton_save_config_clicked)
        self.Ui.pushButton_move_mp4.clicked.connect(self.move_file)
        self.Ui.pushButton_add_actor_pic.clicked.connect(self.pushButton_add_actor_pic_clicked)
        self.Ui.pushButton_show_pic_actor.clicked.connect(self.pushButton_show_pic_actor_clicked)

    # ========================================================================加载config
    def Load_Config(self):
        config_file = 'config.ini'
        config = ConfigParser()
        config.read(config_file, encoding='UTF-8')
        if int(config['common']['main_mode']) == 1:
            self.Ui.radioButton_common.setChecked(True)
        elif int(config['common']['main_mode']) == 2:
            self.Ui.radioButton_sort.setChecked(True)
        if int(config['common']['soft_link']) == 1:
            self.Ui.radioButton_soft_on.setChecked(True)
        elif int(config['common']['soft_link']) == 0:
            self.Ui.radioButton_soft_off.setChecked(True)
        if int(config['update']['update_check']) == 1:
            self.Ui.radioButton_update_on.setChecked(True)
        elif int(config['update']['update_check']) == 0:
            self.Ui.radioButton_update_off.setChecked(True)
        if int(config['debug_mode']['switch']) == 1:
            self.Ui.radioButton_debug_on.setChecked(True)
        elif int(config['debug_mode']['switch']) == 0:
            self.Ui.radioButton_debug_off.setChecked(True)
        if config['media']['media_warehouse'] == 'emby' or config['media']['media_warehouse'] == 'jellyfin':
            self.Ui.radioButton_emby.setChecked(True)
        elif config['media']['media_warehouse'] == 'plex':
            self.Ui.radioButton_plex.setChecked(True)
        elif config['media']['media_warehouse'] == 'kodi':
            self.Ui.radioButton_kodi.setChecked(True)
        if config['common']['website'] == 'all':
            self.Ui.radioButton_all.setChecked(True)
        elif config['common']['website'] == 'javdb':
            self.Ui.radioButton_javdb.setChecked(True)
        self.Ui.lineEdit_success.setText(config['common']['success_output_folder'])
        self.Ui.lineEdit_fail.setText(config['common']['failed_output_folder'])
        self.Ui.lineEdit_escape_dir.setText(config['escape']['folders'])
        self.Ui.lineEdit_escape_char.setText(config['escape']['literals'])
        self.Ui.lineEdit_proxy.setText(config['proxy']['proxy'])
        self.Ui.lineEdit_timeout.setText(config['proxy']['timeout'])
        self.Ui.lineEdit_retry.setText(config['proxy']['retry'])
        self.Ui.lineEdit_dir_name.setText(config['Name_Rule']['location_rule'])
        self.Ui.lineEdit_media_name.setText(config['Name_Rule']['naming_rule'])
        self.Ui.lineEdit_escape_dir_move.setText(config['escape']['folders'])
        self.Ui.lineEdit_emby_url.setText(config['emby']['emby_url'])
        self.Ui.lineEdit_api_key.setText(config['emby']['api_key'])

    # ========================================================================显示版本号
    def show_version(self):
        self.add_text_main('[*]======================== AVDC ========================')
        self.add_text_main('[*]                     Version ' + self.version)
        self.add_text_main('[*]======================================================')

    # ========================================================================鼠标拖动窗口
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = e.globalPos() - self.pos()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.m_drag = False
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseMoveEvent(self, e):
        if Qt.LeftButton and self.m_drag:
            self.move(e.globalPos() - self.m_DragPosition)
            e.accept()

    # ========================================================================左侧按钮点击事件响应函数
    def close_win(self):
        os._exit(0)

    def min_win(self):
        self.setWindowState(Qt.WindowMinimized)

    def pushButton_main_clicked(self):
        self.Ui.stackedWidget.setCurrentIndex(0)

    def pushButton_tool_clicked(self):
        self.Ui.stackedWidget.setCurrentIndex(1)

    def pushButton_setting_clicked(self):
        self.Ui.stackedWidget.setCurrentIndex(2)

    def pushButton_about_clicked(self):
        self.Ui.stackedWidget.setCurrentIndex(3)

    def pushButton_start_cap_clicked(self):
        self.Ui.pushButton_start_cap.setEnabled(False)
        try:
            t = threading.Thread(target=self.AVDC_Main)
            t.start()  # 启动线程,即让线程开始执行
        except Exception as error_info:
            self.add_text_main('[-]Error in pushButton_start_cap_clicked: ' + str(error_info))

    def pushButton_save_config_clicked(self):
        try:
            t = threading.Thread(target=self.save_config_clicked)
            t.start()  # 启动线程,即让线程开始执行
        except Exception as error_info:
            self.add_text_main('[-]Error in pushButton_save_config_clicked: ' + str(error_info))

    # ========================================================================读取设置页设置，保存在config.ini
    def save_config_clicked(self):
        main_mode = 1
        soft_link = 0
        switch_debug = 0
        update_check = 0
        media_warehouse = ''
        website = ''
        if self.Ui.radioButton_common.isChecked():  # 普通模式
            main_mode = 1
        elif self.Ui.radioButton_sort.isChecked():  # 整理模式
            main_mode = 2
        if self.Ui.radioButton_soft_on.isChecked():  # 软链接开
            soft_link = 1
        elif self.Ui.radioButton_soft_off.isChecked():  # 软链接关
            soft_link = 0
        if self.Ui.radioButton_debug_on.isChecked():  # 调试模式开
            switch_debug = 1
        elif self.Ui.radioButton_debug_off.isChecked():  # 调试模式关
            switch_debug = 0
        if self.Ui.radioButton_update_on.isChecked():  # 检查更新
            update_check = 1
        elif self.Ui.radioButton_update_off.isChecked():  # 不检查更新
            update_check = 0
        if self.Ui.radioButton_emby.isChecked():  # emby/jellyfin
            media_warehouse = 'emby'
        elif self.Ui.radioButton_plex.isChecked():  # plex
            media_warehouse = 'plex'
        elif self.Ui.radioButton_kodi.isChecked():  # kodi
            media_warehouse = 'kodi'
        if self.Ui.radioButton_all.isChecked():  # all
            website = 'all'
        elif self.Ui.radioButton_javdb.isChecked():  # javdb
            website = 'javdb'
        json_config = {
            'main_mode': main_mode,
            'soft_link': soft_link,
            'switch_debug': switch_debug,
            'update_check': update_check,
            'media_warehouse': media_warehouse,
            'website': website,
            'failed_output_folder': self.Ui.lineEdit_fail.text(),
            'success_output_folder': self.Ui.lineEdit_success.text(),
            'proxy': self.Ui.lineEdit_proxy.text(),
            'timeout': self.Ui.lineEdit_timeout.text(),
            'retry': self.Ui.lineEdit_retry.text(),
            'location_rule': self.Ui.lineEdit_dir_name.text(),
            'naming_rule': self.Ui.lineEdit_media_name.text(),
            'literals': self.Ui.lineEdit_escape_char.text(),
            'folders': self.Ui.lineEdit_escape_dir.text(),
            'emby_url': self.Ui.lineEdit_emby_url.text(),
            'api_key': self.Ui.lineEdit_api_key.text(),
        }
        save_config(json_config)

    # ========================================================================小工具-单视频刮削
    def pushButton_select_file_clicked(self):
        fileName, fileType = QtWidgets.QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "Movie Files(*.mp4 *.avi *.rmvb "
                                                                   "*.wmv *.mov *.mkv *.flv *.ts *.MP4 *.AVI *.RMVB "
                                                                   "*.WMV *.MOV *.MKV *.FLV *.TS);;All Files(*)")
        if fileName != '':
            self.Ui.stackedWidget.setCurrentIndex(0)
            try:
                t = threading.Thread(target=self.select_file_thread, args=(fileName,))
                t.start()  # 启动线程,即让线程开始执行
            except Exception as error_info:
                self.add_text_main('[-]Error in pushButton_select_file_clicked: ' + str(error_info))

    def select_file_thread(self, file_name):
        file_root = os.getcwd().replace("\\\\", "/").replace("\\", "/")
        file_path = file_name.replace(file_root, '.').replace("\\\\", "/").replace("\\", "/")
        file_name = os.path.splitext(file_name.split('/')[-1])[0]
        mode = 0
        if self.Ui.comboBox_website.currentText() == 'All websites':
            mode = 1
        elif self.Ui.comboBox_website.currentText() == 'javdb':
            mode = 2
        elif self.Ui.comboBox_website.currentText() == 'javbus':
            mode = 3
        elif self.Ui.comboBox_website.currentText() == 'avsox':
            mode = 4
        elif self.Ui.comboBox_website.currentText() == 'fc2club':
            mode = 5
        elif self.Ui.comboBox_website.currentText() == 'fanza':
            mode = 6
        elif self.Ui.comboBox_website.currentText() == 'siro':
            mode = 7
        self.add_text_main("[!]Making Data for   [" + file_path + "], the number is [" + file_name + "]")
        try:
            self.Core_Main(file_path, file_name, mode)
        except Exception as error_info:
            self.add_text_main('[-]Error in select_file_thread: ' + str(error_info))
        self.add_text_main("[*]======================================================")

    # ========================================================================小工具-视频移动
    def move_file(self):
        self.Ui.stackedWidget.setCurrentIndex(0)
        try:
            t = threading.Thread(target=self.move_file_thread)
            t.start()  # 启动线程,即让线程开始执行
        except Exception as error_info:
            self.add_text_main('[-]Error in move_file: ' + str(error_info))

    def move_file_thread(self):
        escape_dir = self.Ui.lineEdit_escape_dir_move.text()
        movie_list = movie_lists(escape_dir)
        self.add_text_main('[+]Move Movies Start!')
        for movie in movie_list:
            sour = movie
            lenth = len(sour.split('/'))
            des = os.getcwd() + '/' + sour.split('/')[lenth - 1]
            try:
                if len(sour.split('/')) > 2:
                    shutil.move(sour, des)
                    self.add_text_main('   [+]Move ' + sour.split('/')[lenth - 1] + ' Success!')
            except Exception as error_info:
                self.add_text_main('[-]Error in move_file_thread: ' + str(error_info))
        self.add_text_main("[+]Move Movies All Finished!!!")
        self.add_text_main("[*]======================================================")

    # ========================================================================小工具-emby女优头像
    def pushButton_add_actor_pic_clicked(self):  # 添加头像按钮响应
        self.Ui.stackedWidget.setCurrentIndex(0)
        emby_url = self.Ui.lineEdit_emby_url.text()
        api_key = self.Ui.lineEdit_api_key.text()
        if emby_url == '':
            self.add_text_main('[-]The emby_url is empty!')
            self.add_text_main("[*]======================================================")
            return
        elif api_key == '':
            self.add_text_main('[-]The api_key is empty!')
            self.add_text_main("[*]======================================================")
            return
        try:
            t = threading.Thread(target=self.found_profile_picture, args=(1,))
            t.start()  # 启动线程,即让线程开始执行
        except Exception as error_info:
            self.add_text_main('[-]Error in pushButton_add_actor_pic_clicked: ' + str(error_info))

    def pushButton_show_pic_actor_clicked(self):  # 查看按钮响应
        self.Ui.stackedWidget.setCurrentIndex(0)
        emby_url = self.Ui.lineEdit_emby_url.text()
        api_key = self.Ui.lineEdit_api_key.text()
        if emby_url == '':
            self.add_text_main('[-]The emby_url is empty!')
            self.add_text_main("[*]======================================================")
            return
        elif api_key == '':
            self.add_text_main('[-]The api_key is empty!')
            self.add_text_main("[*]======================================================")
            return
        if self.Ui.comboBox_pic_actor.currentIndex() == 0:  # 可添加头像的女优
            try:
                t = threading.Thread(target=self.found_profile_picture, args=(2,))
                t.start()  # 启动线程,即让线程开始执行
            except Exception as error_info:
                self.add_text_main('[-]Error in pushButton_show_pic_actor_clicked: ' + str(error_info))
        else:
            try:
                t = threading.Thread(target=self.show_actor, args=(self.Ui.comboBox_pic_actor.currentIndex(),))
                t.start()  # 启动线程,即让线程开始执行
            except Exception as error_info:
                self.add_text_main('[-]Error in pushButton_show_pic_actor_clicked: ' + str(error_info))

    def show_actor(self, mode):  # 按模式显示相应列表
        actor_list = self.get_emby_actor_list()
        count = 1
        actor_list_temp = ''
        if mode == 1:  # 没有头像的女优
            self.add_text_main('[+]没有头像的女优!')
        elif mode == 2:  # 有头像的女优
            self.add_text_main('[+]有头像的女优!')
        elif mode == 3:  # 所有女优
            self.add_text_main('[+]所有女优!')
        for actor in actor_list['Items']:
            if mode == 3:  # 所有女优
                actor_list_temp += str(count) + '.' + actor['Name'] + ','
                count += 1
            elif mode == 2 and actor['ImageTags'] != {}:  # 有头像的女优
                actor_list_temp += str(count) + '.' + actor['Name'] + ','
                count += 1
            elif mode == 1 and actor['ImageTags'] == {}:  # 没有头像的女优
                actor_list_temp += str(count) + '.' + actor['Name'] + ','
                count += 1
            if (count - 1) % 5 == 0 and actor_list_temp != '':
                self.add_text_main('[+]' + actor_list_temp)
                actor_list_temp = ''
        self.add_text_main("[*]======================================================")

    def get_emby_actor_list(self):  # 获取emby的演员列表
        emby_url = self.Ui.lineEdit_emby_url.text()
        api_key = self.Ui.lineEdit_api_key.text()
        emby_url = emby_url.replace('：', ':')
        url = 'http://' + emby_url + '/emby/Persons?api_key=' + api_key
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/60.0.3100.0 Safari/537.36'}
        getweb = requests.get(str(url), headers=headers, timeout=10)
        getweb.encoding = 'utf-8'
        actor_list = json.loads(getweb.text)
        return actor_list

    def found_profile_picture(self, mode):  # mode=1，上传头像，mode=2，显示可添加头像的女优
        path = 'Actor'
        profile_pictures = os.listdir(path)
        actor_list = self.get_emby_actor_list()
        if mode == 1:
            self.add_text_main('[+]Start upload profile pictures!')
        elif mode ==2:
            self.add_text_main('[+]可添加头像的女优!')
        count = 1
        for actor in actor_list['Items']:
            flag = 0
            pic_name = ''
            if actor['ImageTags'] == {}:
                if actor['Name'] + '.jpg' in profile_pictures:
                    flag = 1
                    pic_name = actor['Name'] + '.jpg'
                elif actor['Name'] + '.png' in profile_pictures:
                    flag = 1
                    pic_name = actor['Name'] + '.png'
                if flag == 0:
                    byname_list = re.split('[,()]', actor['Name'])
                    for byname in byname_list:
                        if byname + '.jpg' in profile_pictures:
                            pic_name = byname + '.jpg'
                            flag = 1
                            break
                        elif byname + '.png' in profile_pictures:
                            pic_name = byname + '.png'
                            flag = 1
                            break
                if flag == 1:
                    if mode == 1:
                        self.upload_profile_picture(count, actor, path + '/' + pic_name)
                    else:
                        self.add_text_main('[+]' + "%4s" % str(count) + '.Actor name: ' + actor['Name'] + '  Pic name: '
                                           + pic_name)
                    count += 1
        self.add_text_main("[*]======================================================")

    def upload_profile_picture(self, count, actor, pic_path):  # 上传头像
        emby_url = self.Ui.lineEdit_emby_url.text()
        api_key = self.Ui.lineEdit_api_key.text()
        emby_url = emby_url.replace('：', ':')
        f = open(pic_path, 'rb')  # 二进制方式打开图文件
        b6_pic = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
        f.close()
        url = 'http://' + emby_url + '/emby/Items/' + actor['Id'] + '/Images/Primary?api_key=' + api_key
        if pic_path.endswith('jpg'):
            header = {"Content-Type": 'image/png', }
        else:
            header = {"Content-Type": 'image/jpeg', }
        try:
            respones = requests.post(url=url, data=b6_pic, headers=header)
            self.add_text_main('[+]' + "%4s" % str(count) + '.Success upload profile picture for ' + actor['Name'] + '!')
        except Exception as error_info:
            self.add_text_main('[-]Error in upload_profile_picture! ' + str(error_info))

    # ========================================================================core.py
    def add_text_main(self, text):
        time.sleep(0.1)
        self.Ui.textBrowser_log_main.append(text)
        self.Ui.textBrowser_log_main.moveCursor(QTextCursor.End)

    def moveFailedFolder(self, filepath, failed_folder):
        self.add_text_main('[-]Move to Failed output folder')
        shutil.move(filepath, str(os.getcwd()) + '/' + failed_folder + '/')

    # =====================资源下载部分===========================
    def DownloadFileWithFilename(self, url, filename, path, Config, filepath,
                                 failed_folder):  # path = examle:photo , video.in the Project Folder!
        retry_count = 0
        proxy = ''
        timeout = 0
        try:
            proxy = Config['proxy']['proxy']
            timeout = int(Config['proxy']['timeout'])
            retry_count = int(Config['proxy']['retry'])
        except:
            self.add_text_main('[-]Proxy config error! Please check the config.')
        i = 0

        while i < retry_count:
            try:
                if not proxy == '':
                    if not os.path.exists(path):
                        os.makedirs(path)
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                    r = requests.get(url, headers=headers, timeout=timeout,
                                     proxies={"http": "http://" + str(proxy), "https": "https://" + str(proxy)})
                    if r == '':
                        self.add_text_main('[-]Movie Data not found!')
                        # os._exit(0)
                    with open(str(path) + "/" + filename, "wb") as code:
                        code.write(r.content)
                    return
                else:
                    if not os.path.exists(path):
                        os.makedirs(path)
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                    r = requests.get(url, timeout=timeout, headers=headers)
                    if r == '':
                        self.add_text_main('[-]Movie Data not found!')
                        # os._exit(0)
                    with open(str(path) + "/" + filename, "wb") as code:
                        code.write(r.content)
                    return
            except requests.exceptions.RequestException:
                i += 1
                print('[-]Image Download :   Connect retry ' + str(i) + '/' + str(retry_count))
            except requests.exceptions.ConnectionError:
                i += 1
                print('[-]Image Download :   Connect retry ' + str(i) + '/' + str(retry_count))
            except requests.exceptions.ProxyError:
                i += 1
                print('[-]Image Download :   Connect retry ' + str(i) + '/' + str(retry_count))
            except requests.exceptions.ConnectTimeout:
                i += 1
                print('[-]Image Download :   Connect retry ' + str(i) + '/' + str(retry_count))
        self.add_text_main('[-]Connect Failed! Please check your Proxy or Network!')
        self.moveFailedFolder(filepath, failed_folder)

    def imageDownload(self, option, cover, number, c_word, path, multi_part, Config, filepath,
                      failed_folder):  # 封面是否下载成功，否则移动到failed
        if option == 'emby':
            if self.DownloadFileWithFilename(cover, number + c_word + '.jpg', path, Config, filepath,
                                             failed_folder) == 'failed':
                self.moveFailedFolder(filepath, failed_folder)
            self.DownloadFileWithFilename(cover, number + c_word + '.jpg', path, Config, filepath, failed_folder)
            if not os.path.getsize(path + '/' + number + c_word + '.jpg') == 0:
                self.add_text_main('[+]Fanart Downloaded! ' + number + c_word + '.jpg')
                return
            i = 1
            while i <= int(Config['proxy']['retry']):
                if os.path.getsize(path + '/' + number + c_word + '.jpg') == 0:
                    print('[!]Image Download Failed! Trying again. ' + str(i) + '/' + Config['proxy']['retry'])
                    self.DownloadFileWithFilename(cover, number + c_word + '.jpg', path, Config, filepath,
                                                  failed_folder)
                    i = i + 1
                else:
                    break
            if multi_part == 1:
                old_name = os.path.join(path, number + c_word + '.jpg')
                new_name = os.path.join(path, number + c_word + '.jpg')
                os.rename(old_name, new_name)
                self.add_text_main('[+]Fanart Downloaded! ' + number + c_word + '.jpg')
            else:
                self.add_text_main('[+]Fanart Downloaded! ' + number + c_word + '.jpg')
        elif option == 'plex':
            if self.DownloadFileWithFilename(cover, 'fanart.jpg', path, Config, filepath, failed_folder) == 'failed':
                self.moveFailedFolder(filepath, failed_folder)
            self.DownloadFileWithFilename(cover, 'fanart.jpg', path, Config, filepath, failed_folder)
            if not os.path.getsize(path + '/fanart.jpg') == 0:
                self.add_text_main('[+]Fanart Downloaded! fanart.jpg')
                return
            i = 1
            while i <= int(Config['proxy']['retry']):
                if os.path.getsize(path + '/fanart.jpg') == 0:
                    print('[!]Image Download Failed! Trying again. ' + str(i) + '/' + Config['proxy']['retry'])
                    self.DownloadFileWithFilename(cover, 'fanart.jpg', path, Config, filepath, failed_folder)
                    i = i + 1
                    continue
                else:
                    break
            if not os.path.getsize(path + '/' + number + c_word + '.jpg') == 0:
                print('[!]Image Download Failed! Trying again.')
                self.DownloadFileWithFilename(cover, number + c_word + '.jpg', path, Config, filepath, failed_folder)
            self.add_text_main('[+]Fanart Downloaded! fanart.jpg')
        elif option == 'kodi':
            if self.DownloadFileWithFilename(cover, number + c_word + '-fanart.jpg', path, Config, filepath,
                                             failed_folder) == 'failed':
                self.moveFailedFolder(filepath, failed_folder)
            self.DownloadFileWithFilename(cover, number + c_word + '-fanart.jpg', path, Config, filepath, failed_folder)
            if not os.path.getsize(path + '/' + number + c_word + '-fanart.jpg') == 0:
                self.add_text_main('[+]Fanart Downloaded! ' + number + c_word + '-fanart.jpg')
                return
            i = 1
            while i <= int(Config['proxy']['retry']):
                if os.path.getsize(path + '/' + number + c_word + '-fanart.jpg') == 0:
                    print('[!]Image Download Failed! Trying again. ' + str(i) + '/' + Config['proxy']['retry'])
                    self.DownloadFileWithFilename(cover, number + c_word + '-fanart.jpg', path, Config, filepath,
                                                  failed_folder)
                    i = i + 1
                    continue
                else:
                    break
            self.add_text_main('[+]Fanart Downloaded! ' + number + c_word + '-fanart.jpg')

    def smallCoverCheck(self, path, number, imagecut, cover_small, c_word, option, Config, filepath, failed_folder):
        if imagecut == 3:
            if option == 'emby':
                self.DownloadFileWithFilename(cover_small, '1.jpg', path, Config, filepath, failed_folder)
                try:
                    img = Image.open(path + '/1.jpg')
                except Exception:
                    img = Image.open('1.jpg')
                w = img.width
                h = img.height
                img.save(path + '/' + number + c_word + '.png')
                self.add_text_main('[+]Poster Downloaded! ' + number + c_word + '.png')
                time.sleep(1)
                os.remove(path + '/1.jpg')
            if option == 'kodi':
                self.DownloadFileWithFilename(cover_small, '1.jpg', path, Config, filepath, failed_folder)
                try:
                    img = Image.open(path + '/1.jpg')
                except Exception:
                    img = Image.open('1.jpg')
                w = img.width
                h = img.height
                img.save(path + '/' + number + c_word + '-poster.jpg')
                self.add_text_main('[+]Poster Downloaded! ' + number + c_word + '-poster.jpg')
                time.sleep(1)
                os.remove(path + '/1.jpg')
            if option == 'plex':
                self.DownloadFileWithFilename(cover_small, '1.jpg', path, Config, filepath, failed_folder)
                try:
                    img = Image.open(path + '/1.jpg')
                except Exception:
                    img = Image.open('1.jpg')
                w = img.width
                h = img.height
                img.save(path + '/poster.png')
                self.add_text_main('[+]Poster Downloaded! poster.png')
                os.remove(path + '/1.jpg')

    # ========================================================================打印NFO
    def PrintFiles(self, option, path, c_word, naming_rule, part, cn_sub, json_data, filepath, failed_folder):
        title, studio, year, outline, runtime, director, actor_photo, actor, release, tag, number, cover, website = get_info(
            json_data)
        naming_rule = naming_rule.split('-')
        name_title = ''
        count = 0
        for rule in naming_rule:
            if count == 0 and json_data[rule] != '':
                name_title += json_data[rule]
                count += 1
            elif count > 0 and json_data[rule] != '':
                name_title += '-' + json_data[rule]
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + "/" + number + part + c_word + ".nfo", "wt", encoding='UTF-8') as code:
                print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
                print("<movie>", file=code)
                print(" <title>" + name_title + part + "</title>", file=code)
                print("  <set>", file=code)
                print("  </set>", file=code)
                print("  <studio>" + studio + "+</studio>", file=code)
                print("  <year>" + year + "</year>", file=code)
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
                print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
                print("  <director>" + director + "</director>", file=code)
                if option == 'emby':
                    print("  <poster>" + number + part + c_word + ".png</poster>", file=code)
                    print("  <thumb>" + number + part + c_word + ".png</thumb>", file=code)
                    print("  <fanart>" + number + part + c_word + '.jpg' + "</fanart>", file=code)
                elif option == 'kodi':
                    print("  <poster>" + number + part + c_word + "-poster.jpg</poster>", file=code)
                    print("  <fanart>" + number + part + c_word + '-fanart.jpg' + "</fanart>", file=code)
                elif option == 'plex':
                    print("  <poster>poster.png</poster>", file=code)
                    print("  <thumb>thumb.png</thumb>", file=code)
                    print("  <fanart>fanart.jpg</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not value == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except Exception as error_info:
                    self.add_text_main('[-]Error in actor_photo: ' + str(error_info))
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in tag:
                        print("  <tag>" + i + "</tag>", file=code)
                except Exception as error_info:
                    self.add_text_main('[-]Error in tag: ' + str(error_info))
                try:
                    for i in tag:
                        print("  <genre>" + i + "</genre>", file=code)
                except Exception as error_info:
                    self.add_text_main('[-]Error in genre: ' + str(error_info))
                if cn_sub == '1':
                    print("  <genre>中文字幕</genre>", file=code)
                print("  <num>" + number + "</num>", file=code)
                if option == 'emby':
                    print("  <premiered>" + release + "</premiered>", file=code)
                elif option == 'kodi' or option == 'plex':
                    print("  <release>" + release + "</release>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + website + "</website>", file=code)
                print("</movie>", file=code)
                self.add_text_main("[+]Nfo Writed!        " + number + part + c_word + ".nfo")
        except IOError as e:
            self.add_text_main("[-]Write Failed!")
            self.add_text_main('[-]Error in PrintFiles: ' + str(e))
            self.moveFailedFolder(filepath, failed_folder)
        except Exception as error_info:
            self.add_text_main("[-]Write Failed!")
            self.add_text_main('[-]Error in PrintFiles: ' + str(error_info))
            self.moveFailedFolder(filepath, failed_folder)

    def cutImage(self, option, imagecut, path, number, c_word):
        if option == 'plex':
            if imagecut == 1:
                try:
                    img = Image.open(path + '/fanart.jpg')
                    imgSize = img.size
                    w = img.width
                    h = img.height
                    img2 = img.crop((w / 1.9, 0, w, h))
                    img2.save(path + '/poster.png')
                    self.add_text_main('[+]Poster Cut!        ' + 'poster.png')
                except:
                    self.add_text_main('[-]Cover cut failed!')
            elif imagecut == 0:
                img = Image.open(path + '/fanart.jpg')
                w = img.width
                h = img.height
                img.save(path + '/poster.png')
                self.add_text_main('[+]Poster Cut!        ' + 'poster.png')
        elif option == 'emby':
            if imagecut == 1:
                try:
                    img = Image.open(path + '/' + number + c_word + '.jpg')
                    imgSize = img.size
                    w = img.width
                    h = img.height
                    img2 = img.crop((w / 1.9, 0, w, h))
                    img2.save(path + '/' + number + c_word + '.png')
                    self.add_text_main('[+]Poster Cut!        ' + number + c_word + '.png')
                except:
                    self.add_text_main('[-]Cover cut failed!')
            elif imagecut == 0:
                img = Image.open(path + '/' + number + c_word + '.jpg')
                w = img.width
                h = img.height
                img.save(path + '/' + number + c_word + '.png')
                self.add_text_main('[+]Poster Cut!        ' + number + c_word + '.png')
        elif option == 'kodi':
            if imagecut == 1:
                try:
                    img = Image.open(path + '/' + number + c_word + '-fanart.jpg')
                    imgSize = img.size
                    w = img.width
                    h = img.height
                    img2 = img.crop((w / 1.9, 0, w, h))
                    img2.save(path + '/' + number + c_word + '-poster.jpg')
                    self.add_text_main('[+]Poster Cut!        ' + number + c_word + '-poster.jpg')
                except:
                    self.add_text_main('[-]Cover cut failed!')
            elif imagecut == 0:
                img = Image.open(path + '/' + number + c_word + '-fanart.jpg')
                w = img.width
                h = img.height
                try:
                    img = img.convert('RGB')
                    img.save(path + '/' + number + c_word + '-poster.jpg')
                except:
                    img = img.convert('RGB')
                    img.save(path + '/' + number + c_word + '-poster.jpg')
                self.add_text_main('[+]Poster Cut!        ' + number + c_word + '-poster.jpg')

    def copyRenameJpgToBackdrop(self, option, path, number, c_word):
        if option == 'plex':
            shutil.copy(path + '/fanart.jpg', path + '/Backdrop.jpg')
            shutil.copy(path + '/poster.png', path + '/thumb.png')
        if option == 'emby':
            shutil.copy(path + '/' + number + c_word + '.jpg', path + '/Backdrop.jpg')
        if option == 'kodi':
            shutil.copy(path + '/' + number + c_word + '-fanart.jpg', path + '/Backdrop.jpg')

    def pasteFileToFolder(self, filepath, path, number, c_word, config):  # 文件路径，番号，后缀，要移动至的位置
        houzhui = str(
            re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|avi|rmvb|wmv|mov|mp4|mkv|flv|ts)$', filepath).group())
        try:
            if config['common']['soft_link'] == '1':  # 如果soft_link=1 使用软链接
                os.symlink(filepath, path + '/' + number + c_word + houzhui)
                self.add_text_main('[+]Movie Linked!     ' + number + c_word + houzhui)
            else:
                os.rename(filepath, path + '/' + number + c_word + houzhui)
                self.add_text_main('[+]Movie Moved!       ' + number + c_word + houzhui)
            if os.path.exists(os.getcwd() + '/' + number + c_word + '.srt'):  # 字幕移动
                os.rename(os.getcwd() + '/' + number + c_word + '.srt', path + '/' + number + c_word + '.srt')
                self.add_text_main('[+]Sub moved!')
            elif os.path.exists(os.getcwd() + '/' + number + c_word + '.ssa'):
                os.rename(os.getcwd() + '/' + number + c_word + '.ssa', path + '/' + number + c_word + '.ssa')
                self.add_text_main('[+]Sub moved!')
            elif os.path.exists(os.getcwd() + '/' + number + c_word + '.sub'):
                os.rename(os.getcwd() + '/' + number + c_word + '.sub', path + '/' + number + c_word + '.sub')
                self.add_text_main('[+]Sub moved!')
        except FileExistsError:
            self.add_text_main('[-]Error in pasteFileToFolder_mode2! File Exists! Please check your movie!')
        except PermissionError:
            self.add_text_main('[-]Error in pasteFileToFolder_mode2! Please run as administrator!')

    def pasteFileToFolder_mode2(self, filepath, path, multi_part, number, part, c_word, config):  # 文件路径，番号，后缀，要移动至的位置
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀
        houzhui = str(
            re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|avi|rmvb|wmv|mov|mp4|mkv|flv|ts)$', filepath).group())
        try:
            if config['common']['soft_link'] == '1':
                os.symlink(filepath, path + '/' + number + c_word + houzhui)
                self.add_text_main('[+]Movie Linked!     ' + number + c_word + houzhui)
            else:
                os.rename(filepath, path + '/' + number + c_word + houzhui)
                self.add_text_main('[+]Movie Moved!       ' + number + c_word + houzhui)
            if os.path.exists(number + '.srt'):  # 字幕移动
                os.rename(number + part + c_word + '.srt', path + '/' + number + c_word + '.srt')
                self.add_text_main('[+]Sub moved!')
            elif os.path.exists(number + part + c_word + '.ass'):
                os.rename(number + part + c_word + '.ass', path + '/' + number + c_word + '.ass')
                self.add_text_main('[+]Sub moved!')
            elif os.path.exists(number + part + c_word + '.sub'):
                os.rename(number + part + c_word + '.sub', path + '/' + number + c_word + '.sub')
                self.add_text_main('[+]Sub moved!')
            self.add_text_main('[!]Success')
        except FileExistsError:
            self.add_text_main('[-]Error in pasteFileToFolder_mode2! File Exists! Please check your movie!')
        except PermissionError:
            self.add_text_main('[-]Error in pasteFileToFolder_mode2! Please run as administrator!')

    def get_part(self, filepath, failed_folder):
        try:
            if re.search('-CD\d+', filepath):
                return re.findall('-CD\d+', filepath)[0]
            if re.search('-cd\d+', filepath):
                return re.findall('-cd\d+', filepath)[0]
        except Exception as error_info:
            self.add_text_main('[-]Error in get_part: ' + str(error_info))
            self.moveFailedFolder(filepath, failed_folder)

    # ========================================================================更新进度条
    def set_processbar(self, value):
        self.Ui.progressBar_avdc.setProperty("value", value)

    # ========================================================================输出调试信息
    def debug_mode(self, json_data, config):
        try:
            if config['debug_mode']['switch'] == '1':
                self.add_text_main('[+] ---Debug info---')
                for key, value in json_data.items():
                    if key == 'title' and value == '':
                        self.add_text_main('   [+]Title is None, Not Find Info!')
                        break
                    if value == '' or key == 'actor_photo' or key == 'year' or key == 'imagecut':
                        continue
                    self.add_text_main('   [+]-' + "%-13s" % key + ': ' + str(value))
                self.add_text_main('[+] ---Debug info---')
        except Exception as error_info:
            self.add_text_main('[-]Error in debug_mode: ' + str(error_info))

    # ========================================================================创建输出文件夹
    def creatFolder(self, success_folder, json_data, config):
        location_rule_list = json_data['location_rule'].split('/')
        path = ''
        count_path = 0
        for location_rule in location_rule_list:
            location_rule = location_rule.split('-')
            count_rule = 0
            for rule in location_rule:
                if count_rule == 0 and json_data[rule] != '':
                    path += json_data[rule]
                    count_rule += 1
                elif count_rule > 0 and json_data[rule] != '':
                    path += '-' + json_data[rule]
            if count_path != len(location_rule_list) - 1:
                path += '/'
            count_path += 1
        path = path.replace('//', '/')
        if len(path) > 240:
            self.add_text_main('[-]Error in Length of Path! Repleaced with actor/number')
            path = json_data['actor'] + '/' + json_data['number']
        path = success_folder + '/' + path
        if not os.path.exists(path):
            path = escapePath(path, config)
            try:
                os.makedirs(path)
            except Exception as error_info:
                self.add_text_main('[-]Error in creatFolder: ' + str(error_info))
                return 'error'
        return path

    # ========================================================================从指定网站获取json_data
    def get_json_data(self, mode, number, config):
        if (mode == 0 and self.Ui.radioButton_all.isChecked()) or mode == 1:
            json_data = getDataFromJSON(number, config, 1)  # 所有网站
        elif (mode == 0 and self.Ui.radioButton_javdb.isChecked()) or mode == 2:
            self.add_text_main('[!]Please Wait Three Seconds！')
            time.sleep(3)
            json_data = getDataFromJSON(number, config, 2)  # 仅javdb
        else:
            json_data = getDataFromJSON(number, config, mode)  # 仅javbus或仅avsox或仅fc2club或仅fanza或仅siro
        return json_data

    def Core_Main(self, file_path, number_th, mode):
        # =======================================================================初始化所需变量
        multi_part = 0
        part = ''
        c_word = ''
        option = ''
        cn_sub = ''
        filepath = file_path  # 影片的路径
        number = number_th.replace('_', '-')
        config_file = 'config.ini'
        Config = ConfigParser()
        Config.read(config_file, encoding='UTF-8')
        try:
            option = ReadMediaWarehouse(Config)
        except Exception as error_info:
            self.add_text_main('[-]Error in Core_Main: ' + str(error_info))
        program_mode = Config['common']['main_mode']  # 运行模式
        failed_folder = Config['common']['failed_output_folder']  # 失败输出目录
        success_folder = Config['common']['success_output_folder']  # 成功输出目录
        # =======================================================================获取json_data
        json_data = self.get_json_data(mode, number, Config)
        # =======================================================================是否找到影片信息
        if json_data['website'] == 'timeout':
            self.add_text_main('[-]Connect Failed! Please check your Proxy or Network!')
            self.moveFailedFolder(filepath, failed_folder)
            return
        elif self.Ui.radioButton_javdb.isChecked() and json_data['actor'] == 'N/A':
            self.add_text_main('[-]Your IP Has Been Blocked By JAVDB!')
            return
        elif json_data['title'] == '':
            self.add_text_main('[-]Movie Data not found!')
            self.moveFailedFolder(filepath, failed_folder)
            return
        # =======================================================================调试模式
        self.debug_mode(json_data, Config)
        # =======================================================================判断-C,-CD后缀
        if '-CD' in filepath or '-cd' in filepath:
            multi_part = 1
            part = self.get_part(filepath, failed_folder)
        if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
            cn_sub = '1'
            c_word = '-C'  # 中文字幕影片后缀
        # =======================================================================创建输出文件夹
        self.CreatFailedFolder(failed_folder)  # 创建输出失败目录
        path = self.creatFolder(success_folder, json_data, Config)  # 创建文件夹
        if path == 'error':
            self.add_text_main('[-]Move ' + file_path + ' to failed folder')
            shutil.move(file_path, str(os.getcwd()) + '/' + 'failed/')
            return
        self.add_text_main('[+]Folder : ' + path)
        self.add_text_main('[+]From : ' + json_data['website'])
        # =======================================================================刮削模式
        number = json_data['number']
        if program_mode == '1':
            if multi_part == 1:
                number += part  # 这时number会被附加上-CDx后缀
            self.smallCoverCheck(path, number, json_data['imagecut'], json_data['cover_small'], c_word, option, Config,
                                 filepath,
                                 failed_folder)  # 检查小封面
            self.imageDownload(option, json_data['cover'], number, c_word, path, multi_part, Config, filepath,
                               failed_folder)  # creatFoder会返回番号路径
            self.cutImage(option, json_data['imagecut'], path, number, c_word)  # 裁剪图
            self.copyRenameJpgToBackdrop(option, path, number, c_word)
            self.PrintFiles(option, path, c_word, json_data['naming_rule'], part, cn_sub, json_data, filepath,
                            failed_folder)  # 打印文件
            self.pasteFileToFolder(filepath, path, number, c_word, Config)  # 移动文件
            # =======================================================================整理模式
        elif program_mode == '2':
            self.pasteFileToFolder_mode2(filepath, path, multi_part, number, part, c_word, Config)  # 移动文件

    # ========================================================================AVDC刮削主功能
    def UpdateCheck(self):
        if self.Ui.radioButton_update_on.isChecked():
            check = 1
            self.add_text_main('[!]Update Checking!')
        else:
            check = 0
        if UpdateCheckSwitch(check) == '1':
            html2 = get_html('https://raw.githubusercontent.com/moyy996/AVDC/master/update_check.json')
            if html2 == 'ProxyError':
                return 'ProxyError'
            html = json.loads(str(html2))
            if float(self.version) < float(html['version']):
                self.add_text_main('[*]                  * New update ' + html['version'] + ' *')
                self.add_text_main('[*]                     ↓ Download ↓')
                self.add_text_main('[*] ' + html['download'])
                self.add_text_main('[*]======================================================')
            else:
                self.add_text_main('[!]No Newer Version Available!')
        return 'True'

    def CreatFailedFolder(self, failed_folder):
        if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
            try:
                os.makedirs(failed_folder + '/')
            except Exception as error_info:
                self.add_text_main('[-]Error in CreatFailedFolder: ' + str(error_info))

    def CEF(self, path):
        try:
            files = os.listdir(path)  # 获取路径下的子文件(夹)列表
            for file in files:
                os.removedirs(path + '/' + file)  # 删除这个空文件夹
                self.add_text_main('[+]Deleting empty folder' + path + '/' + file)
        except:
            print('[+]Deleting empty folder error!')

    def AVDC_Main(self):
        # =======================================================================初始化所需变量
        config_file = 'config.ini'
        config = ConfigParser()
        config.read(config_file, encoding='UTF-8')
        success_folder = config['common']['success_output_folder']
        failed_folder = config['common']['failed_output_folder']  # 失败输出目录
        escape_folder = config['escape']['folders']  # 多级目录刮削需要排除的目录
        # =======================================================================检测更新,判断网络情况,新建failed目录,获取影片列表
        os.chdir(os.getcwd())
        if self.UpdateCheck() == 'ProxyError':
            self.add_text_main('[-]Connect Failed! Please check your Proxy or Network!')
            self.Ui.pushButton_start_cap.setEnabled(True)
            self.add_text_main("[*]======================================================")
            return
        self.CreatFailedFolder(failed_folder)  # 新建failed文件夹
        movie_list = movie_lists(escape_folder)  # 获取所有需要刮削的影片列表
        count = 0
        count_all = str(len(movie_list))
        self.add_text_main("[*]======================================================")
        self.add_text_main('[+]Find ' + count_all + ' movies')
        if config['common']['soft_link'] == '1':
            self.add_text_main('[!] --- Soft link mode is ENABLE! ----')
        # =======================================================================遍历电影列表 交给core处理
        for movie in movie_list:  # 遍历电影列表 交给core处理
            count += 1
            percentage = str(count / int(count_all) * 100)[:4] + '%'
            value = int(count / int(count_all) * 100)
            self.progressBarValue.emit(int(value))
            self.add_text_main('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
            try:
                self.add_text_main("[!]Making Data for   [" + movie + "], the number is [" + getNumber(movie) + "]")
                self.Core_Main(movie, getNumber(movie), 0)
                self.add_text_main("[*]======================================================")
            except Exception as error_info:
                self.add_text_main('[-]Error in AVDC_Main: ' + str(error_info))
                curr_path = str(os.getcwd()).replace('\\', '/')
                if config['common']['soft_link'] == '1':
                    self.add_text_main('[-]Link ' + movie + ' to failed folder')
                    try:
                        os.symlink(movie, curr_path + '/' + 'failed/')
                    except Exception as error_info:
                        self.add_text_main('[-]Error in AVDC_Main: ' + str(error_info))
                else:
                    try:
                        shutil.move(movie, curr_path + '/' + 'failed/')
                        self.add_text_main('[-]Move ' + movie + ' to failed folder')
                    except shutil.Error as error_info:
                        self.add_text_main('[-]Error in AVDC_Main: ' + str(error_info))
                self.add_text_main("[*]======================================================")
                continue
        self.Ui.pushButton_start_cap.setEnabled(True)
        self.CEF(success_folder)
        self.CEF(failed_folder)
        self.add_text_main("[+]All finished!!!")


if __name__ == '__main__':
    '''
    主函数
    '''
    app = QApplication(sys.argv)
    ui = MyMAinWindow()
    ui.show()
    sys.exit(app.exec_())
