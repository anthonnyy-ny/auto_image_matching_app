# -*- coding: utf-8 -*-

import math
import time

from PyQt5 import QtCore, QtGui, QtWidgets


class AnimatedBackgroundWidget(QtWidgets.QWidget):
    """Animated painted background for PyQt windows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._start_time = time.monotonic()
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(33)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect()
        elapsed = time.monotonic() - self._start_time

        gradient = QtGui.QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QtGui.QColor(25, 29, 52))
        gradient.setColorAt(0.35, QtGui.QColor(82, 50, 104))
        gradient.setColorAt(0.68, QtGui.QColor(210, 88, 158))
        gradient.setColorAt(1.0, QtGui.QColor(255, 246, 252))
        painter.fillRect(rect, gradient)

        self._paint_grid(painter, rect, elapsed)
        self._paint_light_ribbons(painter, rect, elapsed)
        self._paint_scanlines(painter, rect, elapsed)

    def _paint_grid(self, painter, rect, elapsed):
        spacing = 42
        offset = int((elapsed * 18) % spacing)
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 22), 1)
        painter.setPen(pen)
        for x in range(-spacing + offset, rect.width() + spacing, spacing):
            painter.drawLine(x, 0, x + rect.height() // 3, rect.height())
        for y in range(offset, rect.height() + spacing, spacing):
            painter.drawLine(0, y, rect.width(), y - rect.width() // 5)

    def _paint_light_ribbons(self, painter, rect, elapsed):
        width = rect.width()
        height = rect.height()
        for index, color in enumerate((
            QtGui.QColor(88, 238, 234, 72),
            QtGui.QColor(255, 255, 255, 58),
            QtGui.QColor(255, 118, 192, 66),
        )):
            path = QtGui.QPainterPath()
            base_y = height * (0.22 + index * 0.2)
            wave = math.sin(elapsed * (0.9 + index * 0.2)) * 34
            path.moveTo(-80, base_y + wave)
            path.cubicTo(
                width * 0.22,
                base_y - 120 - wave,
                width * 0.62,
                base_y + 160 + wave,
                width + 90,
                base_y - 35,
            )
            pen = QtGui.QPen(color, 42 - index * 8)
            pen.setCapStyle(QtCore.Qt.RoundCap)
            painter.setPen(pen)
            painter.drawPath(path)

    def _paint_scanlines(self, painter, rect, elapsed):
        band_height = 92
        y = int((elapsed * 90) % (rect.height() + band_height)) - band_height
        scan = QtGui.QLinearGradient(0, y, 0, y + band_height)
        scan.setColorAt(0.0, QtGui.QColor(255, 255, 255, 0))
        scan.setColorAt(0.5, QtGui.QColor(255, 255, 255, 34))
        scan.setColorAt(1.0, QtGui.QColor(255, 255, 255, 0))
        painter.fillRect(QtCore.QRect(0, y, rect.width(), band_height), scan)


class GlowButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(18)
        self._shadow.setOffset(0, 6)
        self._shadow.setColor(QtGui.QColor(71, 232, 235, 100))
        self.setGraphicsEffect(self._shadow)
        self._animation = QtCore.QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._animation.setDuration(170)

    def enterEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self._shadow.blurRadius())
        self._animation.setEndValue(34)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self._shadow.blurRadius())
        self._animation.setEndValue(18)
        self._animation.start()
        super().leaveEvent(event)
