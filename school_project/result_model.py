# -*- coding: utf-8 -*-

from collections import OrderedDict
from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets


class ThumbnailCache:
    def __init__(self, max_items=320, size=QtCore.QSize(136, 112)):
        self.max_items = max_items
        self.size = size
        self._cache = OrderedDict()

    def pixmap(self, path):
        key = str(path)
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached

        reader = QtGui.QImageReader(key)
        reader.setAutoTransform(True)
        image_size = reader.size()
        if image_size.isValid():
            image_size.scale(self.size, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            reader.setScaledSize(image_size)
        image = reader.read()
        if image.isNull():
            pixmap = QtGui.QPixmap()
        else:
            pixmap = QtGui.QPixmap.fromImage(image)

        self._cache[key] = pixmap
        if len(self._cache) > self.max_items:
            self._cache.popitem(last=False)
        return pixmap

    def clear(self):
        self._cache.clear()


class ResultTableModel(QtCore.QAbstractTableModel):
    ImagePathRole = QtCore.Qt.ItemDataRole.UserRole
    GroupNameRole = QtCore.Qt.ItemDataRole.UserRole.value + 1

    def __init__(self, groups=None, parent=None):
        super().__init__(parent)
        self.groups = []
        self.extra_rows = 0
        self.extra_columns = 0
        self.group_number_width = 2
        self.set_groups(groups or [])

    def set_groups(self, groups):
        self.beginResetModel()
        self.groups = list(groups)
        self.group_number_width = max(2, len(str(len(self.groups))))
        self.extra_rows = 0
        self.extra_columns = 0
        self.endResetModel()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return max(1, len(self.groups) + self.extra_rows)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        max_group_size = max((len(group.same) for group in self.groups), default=1)
        return max(1, max_group_size + self.extra_columns)

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        image = self.image_at(index.row(), index.column())
        if image is None:
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return image.filename
        if role == self.ImagePathRole:
            return image.name
        if role == self.GroupNameRole:
            return self.group_name(index.row())
        if role == QtCore.Qt.ItemDataRole.ToolTipRole:
            return image.name
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Horizontal:
            return str(section + 1)
        if not self.groups:
            return "No result" if section == 0 else ""
        if section >= len(self.groups):
            return ""
        group = self.groups[section]
        return self.group_name(section) + " (" + str(group.img_count) + ")"

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        flags = super().flags(index)
        if self.image_at(index.row(), index.column()) is None:
            return flags & ~QtCore.Qt.ItemFlag.ItemIsSelectable
        return flags

    def image_at(self, row, column):
        if row < 0 or column < 0 or row >= len(self.groups):
            return None
        group = self.groups[row]
        if column >= len(group.same):
            return None
        return group.same[column]

    def group_name(self, row):
        return "Group" + str(row + 1).zfill(self.group_number_width)

    def insert_extra_row(self):
        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.extra_rows += 1
        self.endInsertRows()

    def remove_extra_row(self):
        if self.extra_rows <= 0:
            return
        row = self.rowCount() - 1
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self.extra_rows -= 1
        self.endRemoveRows()

    def insert_extra_column(self):
        column = self.columnCount()
        self.beginInsertColumns(QtCore.QModelIndex(), column, column)
        self.extra_columns += 1
        self.endInsertColumns()

    def remove_extra_column(self):
        if self.extra_columns <= 0:
            return
        column = self.columnCount() - 1
        self.beginRemoveColumns(QtCore.QModelIndex(), column, column)
        self.extra_columns -= 1
        self.endRemoveColumns()


class ThumbnailDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, cache=None, parent=None):
        super().__init__(parent)
        self.cache = cache or ThumbnailCache()

    def paint(self, painter, option, index):
        image_path = index.data(ResultTableModel.ImagePathRole)
        if not image_path:
            super().paint(painter, option, index)
            return

        painter.save()
        rect = option.rect.adjusted(8, 8, -8, -8)
        selected = bool(option.state & QtWidgets.QStyle.StateFlag.State_Selected)
        fill = QtGui.QColor(255, 232, 246, 220) if selected else QtGui.QColor(255, 255, 255, 170)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 211, 238, 180), 1))
        painter.setBrush(fill)
        painter.drawRoundedRect(rect, 12, 12)

        pixmap_rect = rect.adjusted(8, 8, -8, -32)
        pixmap = self.cache.pixmap(image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                pixmap_rect.size(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            target = QtCore.QRect(QtCore.QPoint(0, 0), scaled.size())
            target.moveCenter(pixmap_rect.center())
            painter.drawPixmap(target, scaled)

        text_rect = QtCore.QRect(rect.left() + 8, rect.bottom() - 26, rect.width() - 16, 20)
        painter.setPen(QtGui.QColor(58, 39, 70))
        metrics = option.fontMetrics
        text = metrics.elidedText(Path(index.data()).name, QtCore.Qt.TextElideMode.ElideMiddle, text_rect.width())
        painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(165, 165)
