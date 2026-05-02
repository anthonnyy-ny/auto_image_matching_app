# -*- coding: utf-8 -*-

from collections import OrderedDict
import hashlib
import os
from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets

from app_paths import thumbnail_cache_dir


class ManualGroup:
    def __init__(self, images=None):
        self.same = list(images or [])
        self.img_count = len(self.same)


class ProjectImage:
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename


class ThumbnailWorkerSignals(QtCore.QObject):
    ready = QtCore.pyqtSignal(str, str)
    failed = QtCore.pyqtSignal(str)


class ThumbnailWorker(QtCore.QRunnable):
    def __init__(self, source_path, cache_path, size):
        super().__init__()
        self.source_path = source_path
        self.cache_path = cache_path
        self.size = size
        self.signals = ThumbnailWorkerSignals()

    def run(self):
        try:
            reader = QtGui.QImageReader(self.source_path)
            reader.setAutoTransform(True)
            image_size = reader.size()
            if image_size.isValid():
                image_size.scale(self.size, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
                reader.setScaledSize(image_size)
            image = reader.read()
            if image.isNull():
                raise ValueError(reader.errorString() or "thumbnail read failed")

            canvas = QtGui.QImage(self.size, QtGui.QImage.Format.Format_ARGB32)
            canvas.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(canvas)
            painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
            target = QtCore.QRect(QtCore.QPoint(0, 0), image.size())
            target.moveCenter(QtCore.QRect(QtCore.QPoint(0, 0), self.size).center())
            painter.drawImage(target, image)
            painter.end()

            cache_path = Path(self.cache_path)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = cache_path.with_suffix(".tmp")
            if not canvas.save(str(tmp_path), "PNG"):
                raise ValueError("thumbnail cache write failed")
            os.replace(tmp_path, cache_path)
            self.signals.ready.emit(self.source_path, self.cache_path)
        except Exception:
            self.signals.failed.emit(self.source_path)


class ThumbnailManager(QtCore.QObject):
    thumbnailReady = QtCore.pyqtSignal(str)

    def __init__(self, max_items=420, size=QtCore.QSize(136, 112), parent=None):
        super().__init__(parent)
        self.max_items = max_items
        self.size = size
        self._cache = OrderedDict()
        self._pending = set()
        self._failed = set()
        self._cache_dir = thumbnail_cache_dir()
        self._pool = QtCore.QThreadPool.globalInstance()

    def request(self, path):
        key = str(path)
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached

        cache_path = self._disk_cache_path(key)
        if cache_path is not None and cache_path.exists():
            pixmap = QtGui.QPixmap(str(cache_path))
            if not pixmap.isNull():
                self._remember(key, pixmap)
                return pixmap

        if key not in self._pending and key not in self._failed and cache_path is not None:
            self._pending.add(key)
            worker = ThumbnailWorker(key, str(cache_path), self.size)
            worker.signals.ready.connect(self._thumbnail_ready)
            worker.signals.failed.connect(self._thumbnail_failed)
            self._pool.start(worker)
        return None

    def _remember(self, key, pixmap):
        self._cache[key] = pixmap
        if len(self._cache) > self.max_items:
            self._cache.popitem(last=False)

    def _disk_cache_path(self, path):
        try:
            resolved = str(Path(path).resolve())
            stat = os.stat(resolved)
        except OSError:
            return None
        signature = resolved + "|" + str(stat.st_size) + "|" + str(stat.st_mtime_ns) + "|" + str(self.size.width()) + "x" + str(self.size.height())
        digest = hashlib.sha1(signature.encode("utf-8", errors="ignore")).hexdigest()
        return self._cache_dir / (digest + ".png")

    def _thumbnail_ready(self, source_path, cache_path):
        self._pending.discard(source_path)
        pixmap = QtGui.QPixmap(cache_path)
        if not pixmap.isNull():
            self._remember(source_path, pixmap)
        self.thumbnailReady.emit(source_path)

    def _thumbnail_failed(self, source_path):
        self._pending.discard(source_path)
        self._failed.add(source_path)
        self.thumbnailReady.emit(source_path)

    def clear_memory(self):
        self._cache.clear()
        self._failed.clear()


class ResultTableModel(QtCore.QAbstractTableModel):
    ImagePathRole = QtCore.Qt.ItemDataRole.UserRole
    GroupNameRole = QtCore.Qt.ItemDataRole.UserRole.value + 1

    def __init__(self, groups=None, parent=None):
        super().__init__(parent)
        self.groups = []
        self.visible_rows = []
        self.filter_text = ""
        self.extra_rows = 0
        self.extra_columns = 0
        self.group_number_width = 2
        self.set_groups(groups or [])

    def set_groups(self, groups):
        self.beginResetModel()
        self.groups = list(groups)
        self.group_number_width = max(2, len(str(len(self.groups))))
        self.visible_rows = self._matching_rows()
        self.extra_rows = 0
        self.extra_columns = 0
        self.endResetModel()

    def set_filter_text(self, text):
        normalized = (text or "").strip().lower()
        if normalized == self.filter_text:
            return
        self.beginResetModel()
        self.filter_text = normalized
        self.visible_rows = self._matching_rows()
        self.extra_rows = 0
        self.extra_columns = 0
        self.endResetModel()

    def _matching_rows(self):
        if not self.filter_text:
            return list(range(len(self.groups)))
        rows = []
        for row, group in enumerate(self.groups):
            group_name = self.group_name(row).lower()
            filenames = " ".join(getattr(image, "filename", "") for image in group.same).lower()
            if self.filter_text in group_name or self.filter_text in filenames:
                rows.append(row)
        return rows

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return max(1, len(self.visible_rows) + self.extra_rows)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        visible_groups = [self.groups[row] for row in self.visible_rows]
        max_group_size = max((len(group.same) for group in visible_groups), default=1)
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
            source_row = self.source_row(index.row())
            return self.group_name(source_row) if source_row is not None else ""
        if role == QtCore.Qt.ItemDataRole.ToolTipRole:
            return image.name
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Horizontal:
            return str(section + 1)
        if not self.visible_rows:
            return "No result" if section == 0 else ""
        if section >= len(self.visible_rows):
            return ""
        source_row = self.visible_rows[section]
        group = self.groups[source_row]
        return self.group_name(source_row) + " (" + str(group.img_count) + ")"

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        flags = super().flags(index)
        if self.image_at(index.row(), index.column()) is None:
            return flags & ~QtCore.Qt.ItemFlag.ItemIsSelectable
        return flags

    def image_at(self, row, column):
        if row < 0 or column < 0 or row >= len(self.visible_rows):
            return None
        group = self.groups[self.visible_rows[row]]
        if column >= len(group.same):
            return None
        return group.same[column]

    def source_row(self, row):
        if row < 0 or row >= len(self.visible_rows):
            return None
        return self.visible_rows[row]

    def group_name(self, row):
        return "Group" + str(row + 1).zfill(self.group_number_width)

    def refresh_groups(self):
        for group in self.groups:
            group.img_count = len(group.same)
        self.groups = [group for group in self.groups if group.same]
        self.group_number_width = max(2, len(str(len(self.groups))))
        self.visible_rows = self._matching_rows()

    def move_indexes_to_group(self, indexes, target_source_row):
        moves = self._selected_images(indexes)
        if not moves or target_source_row is None or target_source_row < 0 or target_source_row >= len(self.groups):
            return False
        self.beginResetModel()
        target_group = self.groups[target_source_row]
        for source_row, image in moves:
            if source_row == target_source_row:
                continue
            source_group = self.groups[source_row]
            if image in source_group.same:
                source_group.same.remove(image)
                target_group.same.append(image)
        self.refresh_groups()
        self.endResetModel()
        return True

    def create_group_from_indexes(self, indexes):
        moves = self._selected_images(indexes)
        if not moves:
            return False
        self.beginResetModel()
        new_images = []
        for source_row, image in moves:
            source_group = self.groups[source_row]
            if image in source_group.same:
                source_group.same.remove(image)
                new_images.append(image)
        if new_images:
            self.groups.append(ManualGroup(new_images))
        self.refresh_groups()
        self.endResetModel()
        return bool(new_images)

    def merge_source_rows(self, source_rows):
        rows = sorted(set(row for row in source_rows if 0 <= row < len(self.groups)))
        if len(rows) < 2:
            return False
        self.beginResetModel()
        target = self.groups[rows[0]]
        for row in sorted(rows[1:], reverse=True):
            target.same.extend(self.groups[row].same)
            del self.groups[row]
        self.refresh_groups()
        self.endResetModel()
        return True

    def remove_indexes(self, indexes):
        moves = self._selected_images(indexes)
        if not moves:
            return False
        self.beginResetModel()
        for source_row, image in moves:
            if source_row >= len(self.groups):
                continue
            group = self.groups[source_row]
            if image in group.same:
                group.same.remove(image)
        self.refresh_groups()
        self.endResetModel()
        return True

    def _selected_images(self, indexes):
        seen = set()
        moves = []
        for index in indexes:
            if not index.isValid():
                continue
            source_row = self.source_row(index.row())
            image = self.image_at(index.row(), index.column())
            if source_row is None or image is None:
                continue
            key = (source_row, id(image))
            if key in seen:
                continue
            seen.add(key)
            moves.append((source_row, image))
        return sorted(moves, key=lambda item: item[0], reverse=True)

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
    def __init__(self, thumbnail_manager=None, parent=None):
        super().__init__(parent)
        self.thumbnail_manager = thumbnail_manager or ThumbnailManager(parent=self)

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
        pixmap = self.thumbnail_manager.request(image_path)
        if pixmap is not None and not pixmap.isNull():
            scaled = pixmap.scaled(
                pixmap_rect.size(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            target = QtCore.QRect(QtCore.QPoint(0, 0), scaled.size())
            target.moveCenter(pixmap_rect.center())
            painter.drawPixmap(target, scaled)
        else:
            painter.setPen(QtGui.QColor(126, 70, 150, 150))
            painter.drawText(pixmap_rect, QtCore.Qt.AlignmentFlag.AlignCenter, "Loading...")

        text_rect = QtCore.QRect(rect.left() + 8, rect.bottom() - 26, rect.width() - 16, 20)
        painter.setPen(QtGui.QColor(58, 39, 70))
        metrics = option.fontMetrics
        text = metrics.elidedText(Path(index.data()).name, QtCore.Qt.TextElideMode.ElideMiddle, text_rect.width())
        painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(165, 165)
