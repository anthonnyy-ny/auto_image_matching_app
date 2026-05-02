# -*- coding: utf-8 -*-

import math

from PyQt6 import QtCore, QtWidgets


class AnimatedBackgroundWidget(QtWidgets.QWidget):
    """Stable background widget.

    Uses low-frequency stylesheet pulses instead of custom QPainter rendering.
    This keeps the AI/neon feel without the Windows painter warning loop.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self._phase = 0.0
        self._timer = QtCore.QTimer(self)
        self._timer.setTimerType(QtCore.Qt.TimerType.CoarseTimer)
        self._timer.timeout.connect(self._pulse_background)

    def start_ai_motion(self):
        self._pulse_background()
        if not self._timer.isActive():
            self._timer.start(180)

    def stop_ai_motion(self):
        self._timer.stop()

    def showEvent(self, event):
        super().showEvent(event)
        self.start_ai_motion()

    def hideEvent(self, event):
        self.stop_ai_motion()
        super().hideEvent(event)

    def _pulse_background(self):
        self._phase = (self._phase + 0.055) % (math.pi * 2)
        blush = int(210 + math.sin(self._phase) * 18)
        rose = int(118 + math.cos(self._phase * 0.8) * 16)
        violet = int(150 + math.sin(self._phase * 0.6 + 1.2) * 18)
        self.setStyleSheet(f"""
QWidget#centralwidget {{
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 rgb(48, 31, 70),
        stop:0.30 rgb(126, 70, {violet}),
        stop:0.62 rgb({blush}, {rose}, 176),
        stop:0.84 rgb(242, 188, 220),
        stop:1 rgb(255, 247, 252)
    );
}}
""")


class GlowButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
