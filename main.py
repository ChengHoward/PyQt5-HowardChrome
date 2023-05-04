# -*- coding: utf-8 -*-
# file: main.py
# author: Howard

import sys
import win32api
import win32con
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from idna import unichr
from img import *
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolBar, QLineEdit, QDesktopWidget, \
    QTabWidget, QTabBar, QWidgetAction, QStatusBar, QProgressBar, QMenu
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QEnterEvent, QPainter, QColor, QPen, QFontDatabase, QCursor
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from qtpy import QtCore


def fontawesome(font=""):
    if font == "":
        fontId = QFontDatabase.addApplicationFont("font//fontawesome-webfont.ttf")
        fontName = QFontDatabase.applicationFontFamilies(fontId)[0]
    elif font == "fab":
        fontId = QFontDatabase.addApplicationFont("font//fa-regular-400.ttf")
        fontName = QFontDatabase.applicationFontFamilies(fontId)[0]
    elif font == "far":
        fontId = QFontDatabase.addApplicationFont("font//fa-solid-900.ttf")
        fontName = QFontDatabase.applicationFontFamilies(fontId)[0]
    elif font == "boot":
        fontId = QFontDatabase.addApplicationFont("font//glyphicons-halflings-regular.ttf")
        fontName = QFontDatabase.applicationFontFamilies(fontId)[0]
    return QFont(fontName, 14)


# 样式
def MainTheme():
    with open("./main.css", mode="r", encoding="utf-8") as f:
        StyleSheet = f.read()
    return StyleSheet


# HOME_PAGE = "chrome:download"
HOME_PAGE = "https://www.hao123.com/"
NEW_PAGE = "about:blank"
CREATE_BROWER = True

argvs = sys.argv
# 支援flash
argvs.append('--ppapi-flash-path=./pepflashplayer.dll')


class TabBarDe(QTabBar):
    # 窗口移动
    windowMoved = pyqtSignal(QPoint)

    def __init__(self, _self):
        super().__init__()
        self._self = _self
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenuShow)

    def mousePressEvent(self, event):
        super(TabBarDe, self).mousePressEvent(event)
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        self.cur_width = event.pos().x()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        super(TabBarDe, self).mouseReleaseEvent(event)
        self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        # print(event.pos().x(),event.pos().y())
        # print(self.size().width())
        # print(self._self.tab_)
        cur_width = len(self._self.tab_.values()) * 220
        if self.cur_width <= cur_width:
            super(TabBarDe, self).mouseMoveEvent(event)
        else:
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()

    def mouseDoubleClickEvent(self, event):
        super(TabBarDe, self).mouseDoubleClickEvent(event)
        self._self.titleBar.showMaximized()

    def rightMenuShow(self):
        try:
            self.contextMenu = QMenu()
            self.contextMenu.setFont(fontawesome("far"))
            index_action = QWidgetAction()
            index_button = QPushButton(unichr(0xf015),
                                       # clicked=self.zoom_out_func,
                                       font=fontawesome("far"), )
            index_button.setToolTip("主页")
            index_button.setCursor(Qt.ArrowCursor)
            index_action.setDefaultWidget(index_button)

            self.actionA = self.contextMenu.addAction(index_action)
            self.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
            # self.actionA.triggered.connect(self.actionHandler)
            self.contextMenu.show()
        except Exception as e:
            print(e)

    def actionHandler(self):
        print('action')


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)

    def interceptRequest(self, info):
        url = info.requestUrl()
        # print("interceptRequest",url)
        if url.fileName() == "luckyMonster":
            pass
            # print(url.filename())
            # print(str(info.requestUrl()))
        # print(info.requestUrl(),info.requestMethod(),info.resourceType(),info.firstPartyUrl())
        # luckyMonster


class WebView(QWebEngineView):
    def __init__(self, mainWin, parent=None):
        super().__init__(mainWin)
        self.mainWin = mainWin

    # 重写createwindow()
    def createWindow(self, QWebEnginePage_WebWindowType):
        # print("createWindow")
        new_webview = WebView(self.mainWin)
        self.mainWin.create_tab(new_webview)
        return new_webview

    def windowCloseRequested(self):  # real signature unknown; restored from __doc__
        """ windowCloseRequested(self) [signal] """
        pass

class Browser(QMainWindow):
    def __init__(self, mainWin, webview=None):
        super().__init__(mainWin)
        self.showFullScreen()
        self.mainWin = mainWin
        self.webview = webview
        self.initUI()

    def initUI(self):
        global CREATE_BROWER
        # print("initUI")
        # self.setWindowFlags(Qt.FramelessWindowHint)  # 去掉标题栏的代码
        # 设置窗口标题
        # self.setWindowTitle('LingBrowser')
        # 设置窗口图标
        self.setWindowIcon(QIcon(':/icons/logo.png'))
        self.page = QWebEnginePage()
        self.page.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)  # 支持视频播放
        self.page.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.page.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        if self.webview == None:
            # 初始化一个 tab
            self.webview = WebView(self)  # self必须要有，是将主窗口作为参数，传给浏览器
            self.page.setUrl(QUrl(HOME_PAGE))
        self.page.windowCloseRequested.connect(self.on_windowCloseRequested)  # 页面关闭请求
        if CREATE_BROWER:
            CREATE_BROWER = False
            self.page.profile().downloadRequested.connect(self.on_downloadRequested)  # 页面下载请求

        self.t = WebEngineUrlRequestInterceptor()
        self.page.profile().setRequestInterceptor(self.t)
        self.webview.setPage(self.page)
        self.url = self.webview.page().url()
        self.initToolbar(self.webview)
        self.setCentralWidget(self.webview)
        self.center()

    def on_downloadRequested(self, downloadItem):
        # print("download..")
        # print(downloadItem.downloadFileName())
        # print('isFinished', downloadItem.isFinished())
        # print('isPaused', downloadItem.isPaused())
        # print('isSavePageDownload', downloadItem.isSavePageDownload())
        # print('path', downloadItem.path())
        # print('url', downloadItem.url())
        downloadFileName, ok2 = QFileDialog.getSaveFileName(self,
                                                            "文件保存",
                                                            downloadItem.path(),
                                                            "All Files (*)")
        print(downloadItem.path())
        downloadItem.setPath(downloadFileName)
        downloadItem.accept()
        downloadItem.finished.connect(self.on_downloadfinished)
        downloadItem.downloadProgress.connect(self.on_downloadProgress)

    def on_downloadfinished(self):
        print()

    def on_downloadProgress(self, int_1, int_2):
        rate = str(round(int_1 / int_2, 2) * 100).split(".")[0]
        self.mainWin.statusBarDownloadLabel.setText("文件下载 " + rate + "%")
        if int(rate) == 100:
            self.mainWin.statusBarDownloadLabel.setHidden(True)
            self.mainWin.statusBar.setHidden(True)
        else:
            self.mainWin.statusBarDownloadLabel.setHidden(False)
            self.mainWin.statusBar.setHidden(False)

    def on_windowCloseRequested(self):
        print("close tab")
        # self.webview.close()
        # del self.webview
        # sip.delete(self.webview)
        # self.webview
        # self.webview.page().profile().deleteLater()
        # self.deleteLater()
        pass

    def moreMenuShow(self):
        try:
            self.contextMenu = QMenu()
            self.contextMenu.setObjectName("moreMenu")
            self.contextMenu.setFont(fontawesome("far"))
            # self.actionA = self.contextMenu.addAction(self.zoom_in_action)
            # self.actionA = self.contextMenu.addAction(self.zoom_out_action)
            self.contextMenu.popup(
                QPoint(self.mainWin.x() + self.more_button.x() - 200, self.mainWin.y() + 75))  # 2菜单显示的位置 QCursor.pos()
            # print(self.more_button.x())
            # print(self.more_button.y())
            # print(self.frameGeometry())
            # print(self.mainWin.x())
            # print(self.mainWin.y())
            self.contextMenu.setContentsMargins(25,0,0,0)
            self.contextMenu.addMenu("打印")
            self.contextMenu.addSeparator()
            # 缩放组合
            sf_widget = QWidget(self)
            sf_widget.setProperty("class","qwidget")
            sf_widget.setObjectName("sf_widget")
            sf_widget.setContentsMargins(0,0,0,0)
            # sf_widget.setFixedHeight(20)
            sf_layout = QHBoxLayout()
            sf_layout.setContentsMargins(0,0,0,0)
            sf_widget.setLayout(sf_layout)
            sf_label = QLabel("缩放")
            sf_label.setObjectName("sf_item_label")
            sf_layout.addWidget(sf_label)
            sf_layout.addWidget(self.zoom_out_button)
            sf_layout.addWidget(self.sf_label_rate)
            sf_layout.addWidget(self.zoom_in_button)
            sf_layout.addWidget(self.full_screen_button)
            sf_action = QWidgetAction(self)
            sf_action.setDefaultWidget(sf_widget)
            self.actionA = self.contextMenu.addAction(sf_action)
            # self.actionA.triggered.connect(self.actionHandler)
            sf_layout.setSpacing(0)

            self.contextMenu.show()
        except Exception as e:
            print(e)

    def initToolbar(self, webview):
        pass
        ###使用QToolBar创建导航栏，并使用QAction创建按钮
        # 添加导航栏
        self.navigation_bar = QToolBar('Navigation')
        # 锁定导航栏
        self.navigation_bar.setMovable(False)
        # 设定图标的大小
        self.navigation_bar.setIconSize(QSize(2, 2))
        # 添加导航栏到窗口中
        self.addToolBar(self.navigation_bar)
        # 添加其它配置
        self.navigation_bar.setObjectName("navigation_bar")
        self.navigation_bar.setCursor(Qt.ArrowCursor)
        # QAction类提供了抽象的用户界面action，这些action可以被放置在窗口部件中
        # 添加前进、后退、停止加载和刷新的按钮
        self.reload_icon = unichr(0xf2f9)
        self.stop_icon = unichr(0xf00d)

        # 后退按钮
        self.back_action = QWidgetAction(self)
        self.back_button = QPushButton(unichr(0xf060), self,
                                       clicked=webview.back,
                                       font=fontawesome("far"),
                                       objectName='back_button')
        self.back_button.setToolTip("后退")
        self.back_button.setCursor(Qt.ArrowCursor)
        self.back_action.setDefaultWidget(self.back_button)

        # 前进按钮
        self.next_action = QWidgetAction(self)
        self.next_button = QPushButton(unichr(0xf061), self,
                                       clicked=webview.forward,
                                       font=fontawesome("far"),
                                       objectName='next_button')
        self.next_button.setToolTip("前进")
        self.next_button.setCursor(Qt.ArrowCursor)
        self.next_action.setDefaultWidget(self.next_button)

        # 刷新与停止按钮
        self.reload_action = QWidgetAction(self)

        self.reload_button = QPushButton(self.reload_icon, self,
                                         clicked=webview.reload,
                                         font=fontawesome("far"),
                                         objectName='reload_button')
        self.reload_button.setToolTip("刷新")
        self.reload_button.setCursor(Qt.ArrowCursor)
        self.reload_action.setDefaultWidget(self.reload_button)

        # 放大按钮
        self.zoom_in_button = QPushButton(unichr(0xf067), self,
                                          clicked=self.zoom_in_func,
                                          font=fontawesome("far"),
                                          objectName='zoom_in_btn')
        self.zoom_in_button.setToolTip("放大")
        self.zoom_in_button.setCursor(Qt.ArrowCursor)

        # 缩小按钮
        self.zoom_out_button = QPushButton(unichr(0xf068), self,
                                           clicked=self.zoom_out_func,
                                           font=fontawesome("far"),
                                           objectName='zoom_out_btn')
        self.zoom_out_button.setToolTip("缩小")
        self.zoom_out_button.setCursor(Qt.ArrowCursor)
        self.sf_label_rate = QLabel()
        self.sf_label_rate.setObjectName("sf_label_rate")
        self.sf_label_rate.setFixedWidth(30)
        self.sf_label_rate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.sf_label_rate.setProperty("class","qlabel")
        self.sf_label_rate.setText(str(int(self.webview.zoomFactor()*100))+"%")

        # 全屏按钮
        self.full_screen_button = QPushButton(unichr(0xe140), self,
                                           clicked=self.full_screen_func,
                                           font=fontawesome("boot"),
                                           objectName='full_screen_button')
        self.full_screen_button.setToolTip("全屏")
        self.full_screen_button.setCursor(Qt.ArrowCursor)

        # 其它按钮
        self.more_action = QWidgetAction(self)
        self.more_button = QPushButton(unichr(0xe235), self,
                                       clicked=self.moreMenuShow,
                                       font=fontawesome("boot"),
                                       objectName='more_button')
        self.more_button.setToolTip("页面控制及浏览器核心")
        self.more_button.setCursor(Qt.ArrowCursor)
        self.more_action.setDefaultWidget(self.more_button)

        # 首页按钮
        self.index_action = QWidgetAction(self)
        self.index_button = QPushButton(unichr(0xf015), self,
                                        # clicked=self.zoom_out_func,
                                        font=fontawesome("far"),
                                        objectName='index_button')
        self.index_button.setToolTip("主页")
        self.index_button.setCursor(Qt.ArrowCursor)
        self.index_action.setDefaultWidget(self.index_button)

        # self.back_button.triggered.connect(webview.back)
        # self.next_button.triggered.connect(webview.forward)
        # self.reload_button.triggered.connect(webview.reload)
        # self.zoom_in_btn.triggered.connect(self.zoom_in_func)
        # self.zoom_out_btn.triggered.connect(self.zoom_out_func)
        # 将按钮添加到导航栏上
        self.navigation_bar.addAction(self.back_action)
        self.navigation_bar.addAction(self.next_action)
        self.navigation_bar.addAction(self.reload_action)
        self.navigation_bar.addAction(self.index_action)
        # 添加URL地址栏
        self.urlbar = QLineEdit()
        # 让地址栏能响应回车按键信号
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        # self.navigation_bar.addSeparator()
        self.navigation_bar.addWidget(self.urlbar)
        # self.navigation_bar.addSeparator()

        # self.navigation_bar.addAction(self.zoom_in_action)
        # self.navigation_bar.addAction(self.zoom_out_action)
        self.navigation_bar.addAction(self.more_action)
        # 让浏览器相应url地址的变化
        webview.urlChanged.connect(self.renew_urlbar)
        webview.loadProgress.connect(self.processLoad)
        webview.loadStarted.connect(self.loadPage)
        webview.loadFinished.connect(self.loadFinish)
        webview.titleChanged.connect(self.renew_title)
        webview.iconChanged.connect(self.renew_icon)
        self.webBind()
        webview.show()
        self.navigation_bar.setIconSize(QSize(20, 20))
        self.urlbar.setFont(QFont('SansSerif', 13))

    def zoom_in_func(self):
        self.webview.setZoomFactor(self.webview.zoomFactor() + 0.1)
        self.sf_label_rate.setText(str(int(self.webview.zoomFactor()*100))+"%")

    def zoom_out_func(self):
        self.webview.setZoomFactor(self.webview.zoomFactor() - 0.1)
        self.sf_label_rate.setText(str(int(self.webview.zoomFactor()*100))+"%")

    def full_screen_func(self):
        self.navigation_bar.setHidden(True)
        self.mainWin.titleBar.setHidden(True)
        self.mainWin.showFullScreen()

    def on_network_call(self, info):
        print(info)
        pass

    def loadPage(self):
        # print("loadPage")
        # print(self.webview.objectName())
        # self.renew_title("空页面")
        index = self.mainWin.tabWidget.currentIndex()
        self.mainWin.tabWidget.setTabIcon(index, QIcon(":icons/earth_128.png"))
        # self.reload_button.setDefaultWidget(self.stop_button_icon)
        self.reload_button.setText(self.stop_icon)
        self.reload_button.setToolTip("停止")

    def processLoad(self, rate):
        self.mainWin.statusBarLabelProgress.setValue(rate)
        self.mainWin.statusBarLabel.setText("网页加载")
        if rate == 0:
            self.mainWin.statusBarLabelProgress.setMaximum(0)
            self.mainWin.statusBarLabelProgress.setMinimum(0)
        else:
            self.mainWin.statusBarLabelProgress.setMaximum(0)
            self.mainWin.statusBarLabelProgress.setMinimum(100)
        if rate == 100:
            self.mainWin.statusBarLabelProgress.setHidden(True)
            self.mainWin.statusBarLabel.setHidden(True)
            self.mainWin.statusBar.setHidden(True)
        else:
            self.mainWin.statusBarLabelProgress.setHidden(False)
            self.mainWin.statusBarLabel.setHidden(False)
            self.mainWin.statusBar.setHidden(False)
        pass

    def loadFinish(self, isEnd):
        if isEnd:
            # print("load finished", isEnd)
            # self.reload_button.setDefaultWidget(self.reload_button_icon)
            self.reload_button.setText(self.reload_icon)
            self.reload_button.setToolTip("刷新")
        else:
            # print("load finished", isEnd)
            # print("load finished",isEnd)
            pass
        # index = self.webview.objectName()
        # title = self.page.title()
        # print("title", title)
        try:
            url = self.page.url().toString()
        except BaseException as base:
            url = self.webview.page().url().toString()
        # self.mainWin.tabWidget.setTabText(int(index), title if title else url)
        self.urlbar.setText(url)

    def webBind(self):
        # print("webBind")
        # self.back_button.disconnect()
        # self.next_button.disconnect()
        # self.stop_button.disconnect()
        # self.reload_button.disconnect()
        # self.add_button.disconnect()
        # self.back_button.triggered.connect(self.webview.back)
        # self.next_button.triggered.connect(self.webview.forward)
        # self.stop_button.triggered.connect(self.webview.stop)
        # self.reload_button.triggered.connect(self.webview.reload)
        # self.add_button.triggered.connect(self.mainWin.newTab)
        self.webview.urlChanged.connect(self.renew_urlbar)
        self.webview.titleChanged.connect(self.renew_title)
        self.webview.iconChanged.connect(self.renew_icon)

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('http')
        self.webview.setUrl(q)

    def renew_urlbar(self, url):
        # 将当前网页的链接更新到地址栏
        # print("renew_urlbar")
        self.urlbar.setText(url.toString())
        self.urlbar.setCursorPosition(0)
        # print("url", url)f

    def renew_title(self, title):
        # 将当前网页的标题更新到标签栏
        index = self.webview.objectName()
        self.mainWin.tabWidget.setTabToolTip(int(index), title)
        title = " " + title[:11] + ".." if len(title) >= 12 else " " + title
        self.mainWin.tabWidget.setTabText(int(index), title)
        pass

    def renew_icon(self, icon):
        # 将当前网页的图标更新到标签栏
        # print("renew_icon")
        index = self.webview.objectName()
        self.mainWin.tabWidget.setTabIcon(int(index), icon)

    def center(self):
        # print("center")
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 创建tab
    def create_tab(self, webview):
        # print("create_tab")
        self.tab = QWidget()
        self.mainWin.tabWidget.addTab(self.tab, "新标签页")
        self.mainWin.tabWidget.setCurrentWidget(self.tab)
        index = self.mainWin.tabWidget.currentIndex()
        # self.mainWin.tabWidget.setTabIcon(index, ":icons/logo.png")
        #####
        self.Layout = QVBoxLayout(self.tab)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.Layout.addWidget(Browser(self.mainWin, webview=webview))
        webview.setObjectName(str(index))
        self.mainWin.tab_[str(index)] = webview
        self.tab.setObjectName("tab_" + str(index))

        # self.statusBarLabelProgress.setValue(100)

        # self.statusBar = QStatusBar()
        # self.Layout.addWidget(self.statusBar)
        # self.statusBarLabel = QLabel("就绪")
        # self.statusBarLabel.setObjectName("statusBarLabel")
        # self.statusBar.addWidget(self.mainWin.statusBarLabel)
        # self.statusBarLabelProgress = QProgressBar(self)
        # self.statusBar.addWidget(self.mainWin.statusBarLabelProgress)
        # self.statusBarLabelProgress.setObjectName("statusBarLabelProgress")


class TitleBar(QWidget):
    # 窗口最小化信号
    windowMinimumed = pyqtSignal()
    # 窗口最大化信号
    windowMaximumed = pyqtSignal()
    # 窗口还原信号
    windowNormaled = pyqtSignal()
    # 窗口关闭信号
    windowClosed = pyqtSignal()
    # 添加标签页信号
    addPaged = pyqtSignal()
    # 窗口移动
    windowMoved = pyqtSignal(QPoint)

    def __init__(self, *args, **kwargs):
        super(TitleBar, self).__init__(*args, **kwargs)
        # 支持qss设置背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.mPos = None
        self.iconSize = 20  # 图标的默认大小
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        # 布局
        self.layout = QHBoxLayout(self, spacing=0)
        # 功能按钮组
        # self.layout.addStretch()
        self.layout.setContentsMargins(0, 0, 0, 0)
        # 窗口图标
        # self.iconLabel = QLabel(self)
        # self.setIcon(QIcon(':/icons/logo.png'))
        # self.iconLabel.setScaledContents(True)
        # self.layout.addWidget(self.iconLabel)
        # 窗口标题
        # self.titleLabel = QLabel(self)
        # self.titleLabel.setMargin(0)
        # self.titleLabel.setText("QT Browser")
        # self.layout.addWidget(self.titleLabel)

        # 中间伸缩条
        self.layout.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def loadFnBtn(self):
        # 利用Webdings字体来显示图标
        font = self.font() or QFont()
        font.setFamily('Webdings')

        # 添加新的标签页
        self.buttonAddPage = QPushButton(unichr(0xf067), self, clicked=self.addPaged.emit, font=fontawesome("far"),
                                         objectName='buttonAddPage')
        # self.buttonAddPage.setIconSize(QSize(16,16))
        # self.buttonAddPage.setIcon(QIcon(':/icons/plus.png'))

        self.layout.addWidget(self.buttonAddPage)
        # 最小化按钮
        self.buttonMinimum = QPushButton(
            '0', self, clicked=self.windowMinimumed.emit, font=font, objectName='buttonMinimum')
        self.layout.addWidget(self.buttonMinimum)
        # 最大化/还原按钮
        self.buttonMaximum = QPushButton(
            '1', self, clicked=self.showMaximized, font=font, objectName='buttonMaximum')
        self.layout.addWidget(self.buttonMaximum)
        # 关闭按钮
        self.buttonClose = QPushButton(
            'r', self, clicked=self.windowClosed.emit, font=font, objectName='buttonClose')
        self.layout.addWidget(self.buttonClose)
        # 初始高度
        self.setHeight()

    def showMaximized(self):
        if self.buttonMaximum.text() == '1':
            # 最大化
            self.buttonMaximum.setText('2')
            self.windowMaximumed.emit()
        else:  # 还原
            self.buttonMaximum.setText('1')
            self.windowNormaled.emit()

    def setHeight(self, height=34):
        """设置标题栏高度"""
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        # 设置右边按钮的大小
        self.buttonMinimum.setMinimumSize(height, height)
        self.buttonMinimum.setMaximumSize(height, height)
        self.buttonMaximum.setMinimumSize(height, height)
        self.buttonMaximum.setMaximumSize(height, height)
        self.buttonClose.setMinimumSize(height, height)
        self.buttonClose.setMaximumSize(height, height)
        self.buttonAddPage.setMaximumSize(height, height)
        self.buttonAddPage.setMaximumSize(height, height)

    def setTitle(self, title):
        """设置标题"""
        self.titleLabel.setText(title)

    def setIcon(self, icon):
        """设置图标"""
        self.iconLabel.setPixmap(icon.pixmap(self.iconSize, self.iconSize))

    def setIconSize(self, size):
        """设置图标大小"""
        self.iconSize = size

    def enterEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super(TitleBar, self).enterEvent(event)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mPos:
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()


# 枚举左上右下以及四个定点
Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


class FramelessWindow(QWidget):
    # 四周边距
    Margins = 2
    # 窗口移动
    windowMoved = pyqtSignal(QPoint)

    def __init__(self):
        super(FramelessWindow, self).__init__()
        self.tab_ = {}
        self.initTab()
        # 初始化一个 tab
        self.newTab()

        self._pressed = False
        self.Direction = None
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 无边框
        self.setWindowFlags(Qt.FramelessWindowHint)  # 隐藏边框
        # 鼠标跟踪
        self.setMouseTracking(True)
        # 布局
        layout = QVBoxLayout(self, spacing=0)
        # 预留边界用于实现无边框窗口调整大小
        layout.setContentsMargins(self.Margins, self.Margins, self.Margins, self.Margins)
        # 标题栏
        self.titleBar = TitleBar(self)
        # layout = QGridLayout(self, spacing=0)
        # layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.titleBar)
        # self.titleBar.layout.addChildWidget(self.tabWidget.tabBar())
        # self.layout().addWidget(self.titleBar)
        self.titleBar.layout.addChildWidget(self.tabWidget.tabBar())
        self.titleBar.loadFnBtn()
        # self.addPage = QAction(QIcon(':/icons/plus.png'), '页面缩小', self)
        # QTabBar.setS
        self.layout().addWidget(self.tabWidget)
        self.titleBar.addPaged.connect(self.newTab)

        self.statusBar = QStatusBar()
        layout.addWidget(self.statusBar)
        self.headStatusBarLabel = QLabel("就绪")
        self.headStatusBarLabel.setObjectName("headStatusBarLabel")
        self.statusBar.addWidget(self.headStatusBarLabel)

        # 网页加载标签
        self.statusBarLabel = QLabel("网页加载")
        self.statusBarLabel.setObjectName("statusBarLabel")
        self.statusBar.addPermanentWidget(self.statusBarLabel)

        # 网页加载进度条
        self.statusBarLabelProgress = QProgressBar(self)
        self.statusBar.addPermanentWidget(self.statusBarLabelProgress)
        self.statusBarLabelProgress.setObjectName("statusBarLabelProgress")
        self.statusBarLabelProgress.setFixedWidth(200)
        self.statusBarLabelProgress.setHidden(True)
        self.statusBarLabel.setHidden(True)
        # 文件下载标签
        self.statusBarDownloadLabel = QLabel("")
        self.statusBarDownloadLabel.setObjectName("statusBarDownloadLabel")
        self.statusBar.addPermanentWidget(self.statusBarDownloadLabel)
        self.statusBarDownloadLabel.setHidden(True)

        self.statusBar.setHidden(True)
        self.statusBar.setCursor(Qt.ArrowCursor)

        # 信号槽
        self.titleBar.windowMinimumed.connect(self.showMinimized)
        self.titleBar.windowMaximumed.connect(self.showMaximized)
        self.titleBar.windowNormaled.connect(self.showNormal)
        self.titleBar.windowClosed.connect(self.close)
        self.tabBar.windowMoved.connect(self.move)
        # self.titleBar.windowMoved.connect(self.move)
        # self.windowTitleChanged.connect(self.titleBar.setTitle)
        # self.windowIconChanged.connect(self.titleBar.setIcon)
        self.show()

    def initTab(self):
        # print("initTab")
        # self.setWindowFlags(Qt.FramelessWindowHint)  # 去掉标题栏的代码
        # 设置窗口标题
        self.setWindowTitle('PyQt浏览器 v2.0')
        # 设置窗口图标
        self.setWindowIcon(QIcon(':/icons/logo.png'))
        self.tabWidget = QTabWidget()
        # self.tabWidget.setTabBarAutoHide(True)
        self.tabBar = TabBarDe(self)
        # self.tabBar.addAction()
        self.tabWidget.setTabBar(self.tabBar)
        # self.tabWidget.setTabShape(QTabWidget.Triangular) # QTabWidget.Triangular
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.close_Tab)
        self.tabWidget.currentChanged.connect(self.changeTab)

        # self.tabWidget.tabBar().setAutoHide(True)
        height = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) // 2
        width = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) // 2
        self.setMinimumSize(QSize(height * 0.7, width * 0.7))
        # self.center()
        # self.show()

    def newTab(self):
        # print("new tab")
        test = QPushButton("test")
        self.tab = QWidget()
        self.tabWidget.addTab(self.tab, "新标签页")
        self.tabWidget.setCurrentWidget(self.tab)
        index = self.tabWidget.currentIndex()
        try:
            self.tabWidget.setTabIcon(index, QIcon(":icons/earth_128.png"))
        except BaseException as base:
            print(base)
        #####
        self.Layout = QVBoxLayout(self.tab)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.browser = Browser(self)
        self.browser.webview.setObjectName(str(index))
        self.tab.setObjectName("tab_" + str(index))
        self.tab_[str(index)] = self.browser.webview
        self.Layout.addWidget(self.browser)

    # 关闭tab
    def close_Tab(self, index):
        if self.tabWidget.count() > 1:
            # self.browser.webview.page().url(QUrl(""))
            # print(self.tab_[str(index)])

            webObj_index = str(self.tabWidget.widget(index).objectName()).split("_")[1]
            # self.tab_[webObj_index].page().setUrl(QUrl(NEW_PAGE))
            # self.tab_[webObj_index].deleteLater()
            print(self.tab_[webObj_index].history())
            self.tab_.pop(webObj_index)
            # print(self.tab_)
            self.tabWidget.removeTab(index)
            # print(index)
            # self.browser.on_windowCloseRequested()
        else:
            self.close()  # 当只有1个tab时，关闭主窗口

    def changeTab(self, index):
        # print("index:%d" % (index))
        pass

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setTitleBarHeight(self, height=34):
        """设置标题栏高度"""
        self.titleBar.setHeight(height)

    def setIconSize(self, size):
        """设置图标的大小"""
        self.titleBar.setIconSize(size)

    def setWidget(self, widget):
        """设置自己的控件"""
        if hasattr(self, '_widget'):
            return
        self._widget = widget
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self._widget.setAutoFillBackground(True)
        palette = self._widget.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self._widget.setPalette(palette)
        self._widget.installEventFilter(self)
        self.layout().addWidget(self._widget)

    def move(self, pos):
        if self.windowState() == Qt.WindowMaximized or self.windowState() == Qt.WindowFullScreen:
            # 最大化或者全屏则不允许移动
            return
        super(FramelessWindow, self).move(pos)

    def showMaximized(self):
        """最大化,要去除上下左右边界,如果不去除则边框地方会有空隙"""
        super(FramelessWindow, self).showMaximized()
        self.layout().setContentsMargins(0, 0, 0, 0)

    def showFullScreen(self):
        super(FramelessWindow, self).showFullScreen()
        self.layout().setContentsMargins(0, 0, 0, 0)

    def showNormal(self):
        """还原,要保留上下左右边界,否则没有边框无法调整"""
        super(FramelessWindow, self).showNormal()
        self.layout().setContentsMargins(
            self.Margins, self.Margins, self.Margins, self.Margins)

    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(FramelessWindow, self).eventFilter(obj, event)

    def paintEvent(self, event):
        """由于是全透明背景窗口,重绘事件中绘制透明度为1的难以发现的边框,用于调整窗口大小"""
        super(FramelessWindow, self).paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 255, 255, 1), 2 * self.Margins))
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super(FramelessWindow, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._mpos = event.pos()
            self._pressed = True

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        super(FramelessWindow, self).mouseReleaseEvent(event)
        self._pressed = False
        self.Direction = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super(FramelessWindow, self).mouseMoveEvent(event)
        pos = event.pos()
        xPos, yPos = pos.x(), pos.y()
        wm, hm = self.width() - self.Margins, self.height() - self.Margins
        if self.isMaximized() or self.isFullScreen():
            self.Direction = None
            self.setCursor(Qt.ArrowCursor)
            return
        if event.buttons() == Qt.LeftButton and self._pressed:
            self._resizeWidget(pos)
            return
        if xPos <= self.Margins and yPos <= self.Margins:
            # 左上角
            self.Direction = LeftTop
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= xPos <= self.width() and hm <= yPos <= self.height():
            # 右下角
            self.Direction = RightBottom
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= xPos and yPos <= self.Margins:
            # 右上角
            self.Direction = RightTop
            self.setCursor(Qt.SizeBDiagCursor)
        elif xPos <= self.Margins and hm <= yPos:
            # 左下角
            self.Direction = LeftBottom
            self.setCursor(Qt.SizeBDiagCursor)
        elif 0 <= xPos <= self.Margins and self.Margins <= yPos <= hm:
            # 左边
            self.Direction = Left
            self.setCursor(Qt.SizeHorCursor)
        elif wm <= xPos <= self.width() and self.Margins <= yPos <= hm:
            # 右边
            self.Direction = Right
            self.setCursor(Qt.SizeHorCursor)
        elif self.Margins <= xPos <= wm and 0 <= yPos <= self.Margins:
            # 上面
            self.Direction = Top
            self.setCursor(Qt.SizeVerCursor)
        elif self.Margins <= xPos <= wm and hm <= yPos <= self.height():
            # 下面
            self.Direction = Bottom
            self.setCursor(Qt.SizeVerCursor)

    def _resizeWidget(self, pos):
        """调整窗口大小"""
        if self.Direction == None:
            return
        mpos = pos - self._mpos
        xPos, yPos = mpos.x(), mpos.y()
        geometry = self.geometry()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
        if self.Direction == LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self.Direction == RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
        elif self.Direction == RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos.setX(pos.x())
        elif self.Direction == LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos.setY(pos.y())
        elif self.Direction == Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self.Direction == Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            else:
                return
        elif self.Direction == Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self.Direction == Bottom:  # 下面
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
            else:
                return
        self.setGeometry(x, y, w, h)


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setStyleSheet(MainTheme())
    mainWnd = FramelessWindow()
    sys.exit(app.exec_())
