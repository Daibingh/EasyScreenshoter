# coding: utf-8

"""

"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui import Ui_MainWindow
from dialog import Ui_Dialog
from dialog2 import Ui_Dialog as Ui_Dialog2
import uuid
import os.path
from github import Github
import json
from style import styleSheet

def toRectF(rect):
    return QRectF(
        rect.x(),
        rect.y(),
        rect.width(),
        rect.height()
    )


def toRect(rectF):
    return QRect(
        rectF.x(),
        rectF.y(),
        rectF.width(),
        rectF.height()
    )


def normalizeRect(rect):
    x = rect.x()
    y = rect.y()
    w = rect.width()
    h = rect.height()
    if w < 0:
        x = x + w
        w = -w
    if h < 0:
        y = y + h
        h = -h
    return QRectF(x, y, w, h)


def generateName():
    return uuid.uuid4().hex


class WScreenshot(QWidget):
    """
    截图
    """
    captured = pyqtSignal()

    def __init__(self, parent = None):
        super(self.__class__, self).__init__(parent)
        self.saveName = u'截图_{}'.format(QDateTime().currentDateTime().toString("yyyyMMdd_hh-mm-ss"))
        self.saveFormat = 'PNG'
        self.picQuality = 100
        self.ignore = True

        # self.test()
    def launch(self):
        self.setWindowTitle(u'截图窗体')
        self.showFullScreen()  # 全屏显示
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        # 屏幕 和 屏幕信息
        self.screen = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
        self.screenSize = self.screen.rect().size()
        self.screenRect = toRectF(self.screen.rect())
        # -点
        self.screenTopLeft = self.screenRect.topLeft()
        self.screenBottomLeft = self.screenRect.bottomLeft()
        self.screenTopRight = self.screenRect.topRight()
        self.screenBottomRight = self.screenRect.bottomRight()
        # -上下左右限
        self.screenLeft = self.screenRect.left()
        self.screenRight = self.screenRect.right()
        self.screenTop = self.screenRect.top()
        self.screenBottom = self.screenRect.bottom()

        # A:start(x,y)        D:(x+w,y)
        #     -----------------
        #     |               |
        #     |               |
        #     -----------------
        # B:(x,y+h)           C:end(x+w,y+h)

        # 设置 self.screen 为窗口背景
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(self.screen))
        self.setPalette(palette)

        # 调节器层
        self.adjustment_original = QPixmap(self.screenSize)  # 初始调节器
        self.adjustment_original.fill(QColor(0, 0, 0, 64))
        self.adjustment = QPixmap()  # 调节器
        # self.adjustment = self.adjustment_original.copy()  # 调节器

        # 画布层
        self.canvas_original = QPixmap(self.screenSize)  # 初始画布
        self.canvas_original.fill(Qt.transparent)
        self.canvas_saved = self.canvas_original.copy()  # 保存已经画好的图案
        self.canvas = QPixmap()  # 画布

        # self.canvas = self.canvas_original.copy()  # 画布
        # self.canvas_saved = self.canvas.copy()
        # 输出
        self.output = QPixmap()

        # 当前功能状态
        self.isMasking = False
        self.hasMask = False
        self.isMoving = False
        self.isAdjusting = False
        self.isDrawing = False
        self.hasPattern = False
        self.mousePos = ''
        self.isShifting = False

        # 蒙版 和 蒙版信息
        self.maskRect = QRectF()
        self.maskRect_backup = QRectF()

        # 以下 16 个变量随self.maskRect变化而变化
        self.maskTopLeft = QPoint()
        self.maskBottomLeft = QPoint()
        self.maskTopRight = QPoint()
        self.maskBottomRight = QPoint()
        self.maskTopMid = QPoint()
        self.maskBottomMid = QPoint()
        self.maskLeftMid = QPoint()
        self.maskRightMid = QPoint()

        self.rectTopLeft = QRectF()
        self.rectBottomLeft = QRectF()
        self.rectTopRight = QRectF()
        self.rectBottomRight = QRectF()
        self.rectTop = QRectF()
        self.rectBottom = QRectF()
        self.rectLeft = QRectF()
        self.rectRight = QRectF()

        self.adjustmentLineWidth = 2
        self.adjustmentWhiteDotRadius = 6
        self.adjustmentBlueDotRadius = 4
        self.blue = QColor(30, 120, 255)
        self.setCursor(Qt.CrossCursor)  # 设置鼠标样式 十字

        self.setMouseTracking(True)

        # 鼠标事件点
        self.start = QPoint()
        self.end = QPoint()

    def test(self):
        self.hasMask = True
        self.isMasking = False
        self.maskRect = QRectF(100, 100, 600, 800)
        self.updateMaskInfo()
        self.update()

    def toMask(self):
        rect = QRectF(self.start, self.end)

        if self.isShifting:
            x = rect.x()
            y = rect.y()
            w = rect.width()
            h = rect.height()
            absW = abs(w)
            absH = abs(h)
            wIsLonger = True if absW > absH else False
            if w > 0:
                if h > 0:
                    end = QPoint(x + absW, y + absW) if wIsLonger else QPoint(x + absH, y + absH)
                else:
                    end = QPoint(x + absW, y - absW) if wIsLonger else QPoint(x + absH, y - absH)
            else:
                if h > 0:
                    end = QPoint(x - absW, y + absW) if wIsLonger else QPoint(x - absH, y + absH)
                else:
                    end = QPoint(x - absW, y - absW) if wIsLonger else QPoint(x - absH, y - absH)

            rect = QRectF(self.start, end)

        self.maskRect = QRectF(
            rect.x() + min(rect.width(), 0),
            rect.y() + min(rect.height(), 0),
            abs(rect.width()),
            abs(rect.height())
        )

        # 修正超出屏幕、碰撞
        if self.isShifting:
            self.fixCollision()

        self.updateMaskInfo()
        self.update()

    # 修复碰撞。针对 isShifting 的情况
    def fixCollision(self):
        vector = self.end - self.start
        vX = vector.x()
        vY = vector.y()
        resStart = self.maskRect.topLeft()
        resEnd = self.maskRect.bottomRight()
        mLeft = self.maskRect.left()
        mRight = self.maskRect.right()
        mTop = self.maskRect.top()
        mBottom = self.maskRect.bottom()
        # w < h
        if self.maskRect.left() <= self.screenLeft:
            newW = mRight - self.screenLeft
            if vY > 0:
                resStart = QPoint(self.screenLeft, mTop)
                resEnd = resStart + QPoint(newW, newW)
            else:
                resStart = resEnd + QPoint(-newW, -newW)
        elif self.maskRect.right() >= self.screenRight:
            newW = self.screenRight - mLeft
            if vY > 0:
                resEnd = resStart + QPoint(newW, newW)
            else:
                resEnd = QPoint(self.screenRight, mBottom)
                resStart = resEnd + QPoint(-newW, -newW)
        # w > h
        elif self.maskRect.top() <= self.screenTop:
            newW = mBottom - self.screenTop
            if vX > 0:
                resStart = QPoint(mLeft, self.screenTop)
                resEnd = resStart + QPoint(newW, newW)
            else:
                resStart = resEnd + QPoint(-newW, -newW)
        elif self.maskRect.bottom() >= self.screenBottom:
            newW = self.screenBottom - mTop
            if vX > 0:
                resEnd = resStart + QPoint(newW, newW)
            else:
                resEnd = QPoint(mRight, self.screenBottom)
                resStart = resEnd + QPoint(-newW, -newW)
        self.maskRect = QRectF(resStart, resEnd)

    def toAdjust(self):

        mRect = self.maskRect_backup
        mStart = mRect.topLeft()
        mStartX = mStart.x()
        mStartY = mStart.y()
        mEnd = mRect.bottomRight()
        mEndX = mEnd.x()
        mEndY = mEnd.y()
        resStart = mStart
        resEnd = mEnd
        if not self.isShifting:

            if self.mousePos == 'TL':
                resStart = self.end
            elif self.mousePos == 'BL':
                resStart = QPoint(self.end.x(), mStartY)
                resEnd = QPoint(mEndX, self.end.y())
            elif self.mousePos == 'TR':
                resStart = QPoint(mStartX, self.end.y())
                resEnd = QPoint(self.end.x(), mEndY)
            elif self.mousePos == 'BR':
                resEnd = self.end
            elif self.mousePos == 'T':
                resStart = QPoint(mStartX, self.end.y())
            elif self.mousePos == 'B':
                resEnd = QPoint(mEndX, self.end.y())
            elif self.mousePos == 'L':
                resStart = QPoint(self.end.x(), mStartY)
            elif self.mousePos == 'R':
                resEnd = QPoint(self.end.x(), mEndY)
        else:
            print(self.mousePos)
            if self.mousePos == 'T':
                resStart = QPoint(mStartX, self.end.y())
                newW = mEndY - self.end.y()
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'B':
                newW = self.end.y() - mStartY
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'L':
                resStart = QPoint(self.end.x(), mStartY)
                newW = mEndX - self.end.x()
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'R':
                newW = self.end.x() - mStartX
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'TL':
                newW = mEndX - self.end.x()
                newH = mEndY - self.end.y()
                newW = newW if newW > newH else newH
                resStart = resEnd + QPoint(-newW, -newW)
            elif self.mousePos == 'BR':
                newW = self.end.x() - mStartX
                newH = self.end.y() - mStartY
                newW = newW if newW > newH else newH
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'TR':
                newW = self.end.x() - mStartX
                newH = mEndY - self.end.y()
                newW = newW if newW > newH else newH
                resStart = mRect.bottomLeft()
                resEnd = resStart + QPoint(newW, -newW)
            elif self.mousePos == 'BL':
                newW = mEndX - self.end.x()
                newH = self.end.y() - mStartY
                newW = newW if newW > newH else newH
                resStart = mRect.topRight()
                resEnd = resStart + QPoint(-newW, newW)

        self.maskRect = normalizeRect(QRectF(resStart, resEnd))

        self.fixCollision()

        self.updateMaskInfo()
        self.update()

    def toMove(self):
        mStart = self.maskRect_backup.topLeft()
        mStartX = mStart.x()
        mStartY = mStart.y()
        mEnd = self.maskRect_backup.bottomRight()
        mEndX = mEnd.x()
        mEndY = mEnd.y()
        mWidth = self.maskRect_backup.width()
        mHeight = self.maskRect_backup.height()
        mWHPoint = QPoint(mWidth, mHeight)
        vector = self.end - self.start
        vX = vector.x()
        vY = vector.y()

        resStart = mStart + vector
        resStartX = resStart.x()
        resStartY = resStart.y()
        resEnd = mEnd + vector
        resEndX = resEnd.x()
        resEndY = resEnd.y()

        if resStartX <= self.screenLeft and resStartY <= self.screenTop:
            resStart = self.screenTopLeft
            resEnd = resStart + mWHPoint
        elif resEndX >= self.screenRight and resEndY >= self.screenBottom:
            resEnd = self.screenBottomRight
            resStart = resEnd - mWHPoint
        elif resStartX <= self.screenLeft and resEndY >= self.screenBottom:
            resStart = QPoint(self.screenLeft, self.screenBottom - mHeight)
            resEnd = resStart + mWHPoint
        elif resEndX >= self.screenRight and resStartY <= self.screenTop:
            resStart = QPoint(self.screenRight - mWidth, self.screenTop)
            resEnd = resStart + mWHPoint
        elif resStartX <= self.screenLeft:
            resStart = QPoint(self.screenLeft, mStartY + vY)
            resEnd = resStart + mWHPoint
        elif resStartY <= self.screenTop:
            resStart = QPoint(mStartX + vX, self.screenTop)
            resEnd = resStart + mWHPoint
        elif resEndX >= self.screenRight:
            resEnd = QPoint(self.screenRight, mEndY + vY)
            resStart = resEnd - mWHPoint
        elif resEndY >= self.screenBottom:
            resEnd = QPoint(mEndX + vX, self.screenBottom)
            resStart = resEnd - mWHPoint
        self.maskRect = normalizeRect(QRectF(resStart, resEnd))
        self.updateMaskInfo()
        self.update()

    def mousePressEvent(self, QMouseEvent):
        if self.ignore: 
            return
        if QMouseEvent.button() == Qt.LeftButton:
            self.start = QMouseEvent.pos()
            self.end = self.start
            if self.hasMask:
                self.maskRect_backup = self.maskRect
                if self.mousePos == 'mask':
                    self.isMoving = True
                else:
                    self.isAdjusting = True
            else:
                self.isMasking = True

        if QMouseEvent.button() == Qt.RightButton:
            if self.isMasking or self.hasMask:
                self.isMasking = False
                self.hasMask = False
                self.maskRect = QRectF(0, 0, 0, 0)
                self.updateMaskInfo()
                self.update()
            else:
                self.close()

    def mouseReleaseEvent(self, QMouseEvent):
        if self.ignore: 
            return
        if QMouseEvent.button() == Qt.LeftButton:
            self.isMasking = False
            self.isMoving = False
            self.isAdjusting = False
            self.isDrawing = False

    def mouseDoubleClickEvent(self, QMouseEvent):
        if self.ignore: 
            return
        if QMouseEvent.button() == Qt.LeftButton:
            if self.mousePos == 'mask':
                self.capture()
                self.close()

    def mouseMoveEvent(self, QMouseEvent):
        if self.ignore: 
            return
        pos = QMouseEvent.pos()
        self.end = pos

        if self.isMasking:
            self.hasMask = True
            self.toMask()
        elif self.isMoving:
            self.toMove()
        elif self.isAdjusting:
            self.toAdjust()

        # 设置鼠标样式
        if self.isDrawing:
            pass
        else:
            if self.hasMask:
                if self.isMoving:
                    self.setCursor(Qt.SizeAllCursor)
                elif self.isAdjusting:
                    pass
                else:
                    self.setMouseShape(pos)
            else:
                self.mousePos = ''
                self.setCursor(Qt.CrossCursor)  # 设置鼠标样式 十字

    def setMouseShape(self, pos):
        # 设置鼠标样式
        if self.rectTopLeft.contains(pos):
            self.setCursor(Qt.SizeFDiagCursor)
            self.mousePos = 'TL'
        elif self.rectBottomLeft.contains(pos):
            self.setCursor(Qt.SizeBDiagCursor)
            self.mousePos = 'BL'
        elif self.rectBottomRight.contains(pos):
            self.setCursor(Qt.SizeFDiagCursor)
            self.mousePos = 'BR'
        elif self.rectTopRight.contains(pos):
            self.setCursor(Qt.SizeBDiagCursor)
            self.mousePos = 'TR'
        elif self.rectLeft.contains(pos):
            self.setCursor(Qt.SizeHorCursor)
            self.mousePos = 'L'
        elif self.rectTop.contains(pos):
            self.setCursor(Qt.SizeVerCursor)
            self.mousePos = 'T'
        elif self.rectBottom.contains(pos):
            self.setCursor(Qt.SizeVerCursor)
            self.mousePos = 'B'
        elif self.rectRight.contains(pos):
            self.setCursor(Qt.SizeHorCursor)
            self.mousePos = 'R'
        elif self.maskRect.contains(pos):
            self.setCursor(Qt.SizeAllCursor)
            self.mousePos = 'mask'

    def updateMaskInfo(self):
        # 蒙版点
        self.maskTopLeft = self.maskRect.topLeft()
        self.maskBottomLeft = self.maskRect.bottomLeft()
        self.maskTopRight = self.maskRect.topRight()
        self.maskBottomRight = self.maskRect.bottomRight()
        self.maskTopMid = (self.maskTopLeft + self.maskTopRight) / 2
        self.maskBottomMid = (self.maskBottomLeft + self.maskBottomRight) / 2
        self.maskLeftMid = (self.maskTopLeft + self.maskBottomLeft) / 2
        self.maskRightMid = (self.maskTopRight + self.maskBottomRight) / 2
        # 除蒙版区外的 8 个区域
        self.rectTopLeft = QRectF(self.screenTopLeft, self.maskTopLeft)
        self.rectBottomLeft = QRectF(self.screenBottomLeft, self.maskBottomLeft)
        self.rectTopRight = QRectF(self.screenTopRight, self.maskTopRight)
        self.rectBottomRight = QRectF(self.screenBottomRight, self.maskBottomRight)
        self.rectTop = QRectF(QPoint(self.maskRect.left(), self.screenTop), self.maskTopRight)
        self.rectBottom = QRectF(self.maskBottomLeft, QPoint(self.maskRect.right(), self.screenBottom))
        self.rectLeft = QRectF(QPoint(self.screenLeft, self.maskRect.top()), self.maskBottomLeft)
        self.rectRight = QRectF(self.maskTopRight, QPoint(self.screenRight, self.maskRect.bottom()))

    def paintEvent(self, QPaintEvent):
        if self.ignore: 
            return
        painter = QPainter()

        # 开始在 画布层 上绘画。如果正在绘画，绘制图案, 否则不绘制
        if self.isDrawing:
            if self.hasPattern:
                self.canvas = self.canvas_saved.copy()
            else:
                self.canvas = self.canvas_original.copy()
            painter.begin(self.canvas)
            self.paintCanvas(painter)
            painter.end()
            # 把 画布层 绘画到窗口上
            painter.begin(self)
            painter.drawPixmap(self.screenRect, self.canvas)
            painter.end()

        # 开始在 空白调节器层 上绘画。如果有蒙版，绘制调节器形状, 否则不绘制
        else:
            self.adjustment = self.adjustment_original.copy()
            painter.begin(self.adjustment)
            self.paintAdjustment(painter)
            painter.end()
            # 把 调节器层 绘画到窗口上
            painter.begin(self)
            painter.drawPixmap(toRect(self.screenRect), self.adjustment)
            painter.end()

    def paintAdjustment(self, painter):
        if self.hasMask:
            painter.setRenderHint(QPainter.Antialiasing, True)  # 反走样
            painter.setPen(Qt.NoPen)
            # 在蒙版区绘制屏幕背景
            painter.setBrush(QBrush(self.screen))
            painter.drawRect(self.maskRect)
            # 绘制线框
            lineWidth = self.adjustmentLineWidth
            painter.setBrush(self.blue)
            painter.drawRect(
                QRectF(
                    self.maskTopLeft + QPoint(-lineWidth, -lineWidth),
                    self.maskTopRight + QPoint(lineWidth, 0))
            )
            painter.drawRect(
                QRectF(
                    self.maskBottomLeft + QPoint(-lineWidth, 0),
                    self.maskBottomRight + QPoint(lineWidth, lineWidth)
                )
            )
            painter.drawRect(
                QRectF(
                    self.maskTopLeft + QPoint(-lineWidth, -lineWidth),
                    self.maskBottomLeft + QPoint(0, lineWidth)
                )
            )
            painter.drawRect(
                QRectF(
                    self.maskTopRight + QPoint(0, -lineWidth),
                    self.maskBottomRight + QPoint(lineWidth, lineWidth)
                )
            )
            if self.maskRect.width() >= 150 and self.maskRect.height() >= 150:
                # 绘制点
                points = [
                    self.maskTopLeft, self.maskTopRight, self.maskBottomLeft, self.maskBottomRight,
                    self.maskLeftMid, self.maskRightMid, self.maskTopMid, self.maskBottomMid
                ]
                # -白点
                whiteDotRadiusPoint = QPoint(self.adjustmentWhiteDotRadius, self.adjustmentWhiteDotRadius)
                painter.setBrush(Qt.white)
                for point in points:
                    painter.drawEllipse(QRectF(point - whiteDotRadiusPoint, point + whiteDotRadiusPoint))
                # -蓝点
                blueDotRadius = QPoint(self.adjustmentBlueDotRadius, self.adjustmentBlueDotRadius)
                painter.setBrush(self.blue)
                for point in points:
                    painter.drawEllipse(QRectF(point - blueDotRadius, point + blueDotRadius))

            # 绘制尺寸
            maskSize = (abs(int(self.maskRect.width())), abs(int(self.maskRect.height())))
            painter.setFont(QFont('Monaco', 7, QFont.Bold))
            painter.setPen(Qt.transparent)  # 透明获得字体Rect
            textRect = painter.drawText(
                QRectF(self.maskTopLeft.x() + 10, self.maskTopLeft.y() - 25, 100, 20),
                Qt.AlignLeft | Qt.AlignVCenter,
                '{} x {}'.format(*maskSize)
            )
            painter.setBrush(QColor(0, 0, 0, 128))  # 黑底
            padding = 5
            painter.drawRect(
                QRectF(
                    textRect.x() - padding,
                    textRect.y() - padding * 0.4,
                    textRect.width() + padding * 2,
                    textRect.height() + padding * 0.4
                )
            )
            painter.setPen(Qt.white)
            painter.drawText(
                textRect,
                Qt.AlignLeft | Qt.AlignVCenter,
                '{} x {}'.format(*maskSize)
            )
            painter.setPen(Qt.NoPen)

    def paintCanvas(self, painter):
        pass

    def keyPressEvent(self, QKeyEvent):
        if self.ignore: 
            return
        if QKeyEvent.key() == Qt.Key_Escape:
            self.close()
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:  # 大键盘、小键盘回车
            if self.hasMask:
                self.capture()
            self.close()
        if QKeyEvent.modifiers() & Qt.ShiftModifier:
            self.isShifting = True

    def keyReleaseEvent(self, QKeyEvent):
        if self.ignore: 
            return
        if QKeyEvent.key() == Qt.Key_Shift:
            self.isShifting = False

    def capture(self):
        self.output = self.screen.copy()
        if self.hasPattern:
            painter = QPainter(self.output)
            painter.drawPixmap(self.canvas)
        self.output = self.output.copy(toRect(self.maskRect))
        self.captured.emit()


class Dialog(QDialog, Ui_Dialog):
    """docstring for Dialog"""
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('登陆远程仓库')
        self._p = parent
        self.lineEdit.setText(self._p.token)
        self.lineEdit_2.setText(self._p.repo)

    def on_buttonBox_accepted(self):
        self._p.repo = self.lineEdit_2.text()
        self._p.token = self.lineEdit.text()
        try:
            g = Github(self._p.token)
            repo = g.get_repo(self._p.repo)
        except Exception as e:
            QMessageBox.warning(self, "Error", "Cannot content to your repo!")
 

class LoadThread(QThread):

    loaded = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, parent):
        super(LoadThread, self).__init__()
        self._p = parent
        self.contents = None

    def run(self):
        self.contents = None
        try:
            g = Github(self._p._p.token)
            repo = g.get_repo(self._p._p.repo)
            self.contents = repo.get_contents('.')
        except Exception as e:
            print('update failed: please check the network connection or login key.')
            self.error.emit()
        self.loaded.emit()


class DeleteThread(QThread):
    """docstring for DeleteThread"""

    deleted = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, parent):
        super(DeleteThread, self).__init__()
        self.items = None
        self._p = parent

    def run(self):
        try:
            g = Github(self._p._p.token)
            repo = g.get_repo(self._p._p.repo)
            for i in self.items:
                content = repo.get_contents(i.text())
                repo.delete_file(i.text(), "Delete an image.", content.sha)
        except Exception as e:
            print('delete failed: please check the network connection or login key.')
            self.error.emit()
          
        self.deleted.emit()
        

class Dialog2(QDialog, Ui_Dialog2):
    """docstring for Dialog"""
    def __init__(self, parent=None):
        super(Dialog2, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('浏览远程仓库')
        self._p = parent
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 600)
        self.thread = DeleteThread(self)
        self.thread2 = LoadThread(self)
        self.thread.deleted.connect(self.handleDeleted)
        self.thread2.loaded.connect(self.handleLoaded)
        self.thread.error.connect(self.handleDeletedError)
        self.thread2.error.connect(self.handleLoadError)

    def handleDeletedError(self):
        QMessageBox.warning(self, 'Error', 'delete failed: please check the network connection or login key.')

    def handleLoadError(self):
        QMessageBox.warning(self, 'Error', 'update failed: please check the network connection or login key.')

    def handleDeleted(self):
        self.thread2.start()

    def handleLoaded(self):
        contents = self.thread2.contents
        if contents is None:
            self.tableWidget.setRowCount(0)
        else:
            self.tableWidget.setRowCount(len(contents))
            for i, file in enumerate(contents):
                name = file.name
                link = file.download_url
                self.tableWidget.setItem(i, 0, QTableWidgetItem(name))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(link))
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)

    def on_pushButton_2_clicked(self):
        self.thread2.start()
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)

    def on_pushButton_clicked(self):
        """handle delete button clicked"""
        items = self.tableWidget.selectedItems()
        if len(items)==0: return
        self.thread.items = items
        self.thread.start()
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)


class UploadThread(QThread):
    """docstring for UploadThread"""
    uploaded = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, parent):
        super(UploadThread, self).__init__()
        self._p = parent
        self.pixmap = QPixmap()
        self.imgName = ''

    def run(self):
        try:
            ba = QByteArray()
            buff = QBuffer(ba)
            buff.open(QIODevice.WriteOnly) 
            ok = self.pixmap.save(buff, "PNG")
            pixmap_bytes = ba.data()
            g = Github(self._p.token)
            repo = g.get_repo(self._p.repo)
            repo.create_file(self.imgName, message="Add an image.", content=pixmap_bytes)
        except Exception as e:
            print("upload failed: please check the network connection or login key.")
            self.error.emit()
        
        self.uploaded.emit()


class MyWindow(QMainWindow, Ui_MainWindow):
    """docstring for MyWindow"""
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('便捷截图')
        self.repo = 'Username/reponame'
        self.token = '****'
        conf = self.loadConfig()
        if conf is not None:
            self.repo = conf.get('repo', self.repo)
            self.token = conf.get('token', self.token)
            self.lineEdit.setText(conf.get('prefix', ''))
            self.lineEdit_2.setText(conf.get('path', '.'))
        self.picQuality = 10
        self.lineEdit_3.setText(str(self.picQuality))
        self.lineEdit_3.setMaximumWidth(40)
        self.label_4.setOpenExternalLinks(True)
        self.label_4.setText('<a href="https://github.com/settings/tokens">token</a>')
        self.label_4.setToolTip("Apply for a token on github.")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        self.d = Dialog(self)
        self.d2 = Dialog2(self)
        self.ws = WScreenshot()
        self.thread = UploadThread(self)

        self.ws.captured.connect(self.handleCaptured)
        self.thread.uploaded.connect(self.handleUploaded)
        self.thread.error.connect(self.handleUploadedError)

        self.setStyleSheet(styleSheet)      

    def closeEvent(self, event):
        conf = {
        'token': self.token,
        'repo': self.repo,
        'path': self.lineEdit_2.text(),
        'prefix': self.lineEdit.text()
        }
        with open('.config', 'w', encoding='utf-8') as f:
            json.dump(conf, f)

    def loadConfig(self): 
        if not os.path.exists('.config'):
            return None
        with open('.config', 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception as e:
                return None

    def handleUploadedError(self):
        QMessageBox.warning(self, 'Error', 'upload failed: please check the network connection or login key.')

    def handleUploaded(self):
        self.pushButton.setEnabled(True)

    def handleCaptured(self):
        pixmap = self.ws.output
        prefix = self.lineEdit.text()
        if len(prefix)==0:
            imgName = "{}.png".format(generateName())
        else:
            imgName = "{}_{}.png".format(prefix, generateName())

        if not self.actionremote.isChecked():
            folder = self.lineEdit_2.text()
            fullName = "{}{}{}".format(folder, os.path.sep, imgName)
            if self.comboBox.currentText()=='full':
                copyName = fullName
            elif self.comboBox.currentText()=='-1':
                copyName = fullName.split(os.path.sep)[-1]
            elif self.comboBox.currentText()=='-2':
                copyName = '/'.join(fullName.split(os.path.sep)[-2:])
            copyLink = '<center><img src="{}" width="600px"></center>'.format(copyName)
            QApplication.clipboard().setText(copyLink)
            pixmap.save(fullName, 'PNG', self.picQuality)
        else:
            copyLink = '<center><img src="https://github.com/{}/blob/master/{}?raw=true" \
            width="600px"></center>'.format(self.repo, imgName)
            QApplication.clipboard().setText(copyLink)
            self.thread.pixmap = pixmap
            self.thread.imgName = imgName
            self.thread.start()
            self.pushButton.setEnabled(False);

        self.ws.ignore = True

    def on_pushButton_clicked(self):
        self.ws.launch()
        self.ws.show()
        self.ws.ignore = False

    def on_actionlogin_triggered(self):
        self.d.show()

    def on_actionimages_triggered(self):
        self.d2.show()
        self.d2.thread2.start()
        self.d2.pushButton.setEnabled(False)
        self.d2.pushButton_2.setEnabled(False)

    def on_lineEdit_3_textChanged(self, s):
        try: 
            self.picQuality = max(min(int(s), 100), 1)
        except Exception as e:
            print("input error: the quality input must be a int number ranging in 0~100.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
