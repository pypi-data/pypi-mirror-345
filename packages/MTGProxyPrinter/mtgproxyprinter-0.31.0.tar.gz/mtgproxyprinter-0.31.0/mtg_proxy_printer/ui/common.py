#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

import functools
from pathlib import Path
import platform
from typing import Union, Dict

from PyQt5.QtCore import QFile, QObject, QSize, QCoreApplication, Qt, QBuffer, QIODevice
from PyQt5.QtWidgets import QWizard, QWidget, QGraphicsColorizeEffect, QTextEdit
from PyQt5.QtGui import QIcon, QPixmap
# noinspection PyUnresolvedReferences
from PyQt5 import uic

from mtg_proxy_printer.units_and_sizes import OptStr
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "RESOURCE_PATH_PREFIX",
    "ICON_PATH_PREFIX",
    "HAS_COMPILED_RESOURCES",
    "highlight_widget",
    "BlockedSignals",
    "load_ui_from_file",
    "load_file",
    "markdown_to_html",
    "format_size",
    "WizardBase",
    "get_card_image_tooltip",
]

try:
    import mtg_proxy_printer.ui.compiled_resources
except ModuleNotFoundError:
    RESOURCE_PATH_PREFIX = str(Path(__file__).resolve().parent.with_name("resources"))
    ICON_PATH_PREFIX = str(Path(__file__).resolve().parent.with_name("resources") / "icons")
    HAS_COMPILED_RESOURCES = False
else:
    import atexit
    # Compiled resources found, so use it.
    RESOURCE_PATH_PREFIX = ":"
    ICON_PATH_PREFIX = ":/icons"
    HAS_COMPILED_RESOURCES = True
    atexit.register(mtg_proxy_printer.ui.compiled_resources.qCleanupResources)


@functools.lru_cache(maxsize=256)
def get_card_image_tooltip(image: Union[bytes, Path], card_name: OptStr = None, scaling_factor: int = 3) -> str:
    """
    Returns a tooltip string showing a scaled down image for the given path.
    :param image: Filesystem path to the image file or raw image content as bytes
    :param card_name: Optional card name. If given, it is centered above the image
    :param scaling_factor: Scales the source by factor to 1/scaling_factor
    :return: HTML fragment with the image embedded as a base64 encoded PNG
    """
    if isinstance(image, bytes):
        source = QPixmap()
        source.loadFromData(image)
    else:
        source = QPixmap(str(image))
    pixmap = source.scaledToWidth(source.width() // scaling_factor, Qt.TransformationMode.SmoothTransformation)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buffer, "PNG", quality=100)
    image = buffer.data().toBase64().data().decode()
    card_name = f'<p style="text-align:center">{card_name}</p><br>' if card_name else ""
    return f'{card_name}<img src="data:image/png;base64,{image}">'


def highlight_widget(widget: QWidget) -> None:
    """Sets a visual highlight on the given widget to make it stand out"""
    palette = widget.palette()
    highlight_color = palette.color(palette.currentColorGroup(), palette.ColorRole.Highlight)
    effect = QGraphicsColorizeEffect(widget)
    effect.setColor(highlight_color)
    effect.setStrength(0.75)
    widget.setGraphicsEffect(effect)


class BlockedSignals:
    """
    Context manager used to temporarily prevent any QObject-derived object from emitting Qt signals.
    This can be used to break signal trigger loops or unwanted trigger chains.
    """
    def __init__(self, qt_object: QObject):
        self.qt_object = qt_object

    def __enter__(self):
        self.qt_object.blockSignals(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.qt_object.blockSignals(False)


def load_ui_from_file(name: str):
    """
    Returns the Ui class type from uic.loadUiType(), loading the ui file with the given name.

    :param name: Path to the UI file
    :return: class implementing the requested Ui
    :raises FileNotFoundError: If the given ui file does not exist
    """
    file_path = f"{RESOURCE_PATH_PREFIX}/ui/{name}.ui"
    if not QFile.exists(file_path):
        error_message = f"UI file not found: {file_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)
    base_type, _ = uic.loadUiType(file_path, from_imports=True)
    return base_type

def load_icon(name: str) -> QIcon:
    file_path = f"{RESOURCE_PATH_PREFIX}/icons/{name}"
    if not QFile.exists(file_path):
        error_message = f"Icon not found: {file_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)
    icon = QIcon(file_path)
    return icon

def load_file(path: str, parent = None) -> bytes:
    file_path = f"{RESOURCE_PATH_PREFIX}/{path}"
    file = QFile(file_path, parent)
    data = b''
    if file.open(QIODevice.OpenModeFlag.ReadOnly):
        try:
            data = file.readAll().data()
        finally:
            file.close()
            return data
    logger.error(f"Opening {file_path} failed")
    return data

def markdown_to_html(markdown: str) -> str:
    browser = QTextEdit()
    browser.setMarkdown(markdown)
    return browser.toHtml()

def format_size(size: float) -> str:
    template = QCoreApplication.translate(
        "format_size", "{size} {unit}", "A formatted file size in SI bytes")
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB'):
        if -1024 < size < 1024:
            return template.format(size=f"{size:3.2f}", unit=unit)
        size /= 1024
    return template.format(size=f"{size:.2f}", unit="YiB")


class WizardBase(QWizard):
    """Base class for wizards based on QWizard"""
    BUTTON_ICONS: Dict[QWizard.WizardButton, str] = {}

    def __init__(self, window_size: QSize, parent: QWidget, flags):
        super().__init__(parent, flags)
        if platform.system() == "Windows":
            # Avoid Aero style on Windows, which does not support dark mode
            target_style = QWizard.WizardStyle.ModernStyle
            logger.debug(f"Creating a QWizard on Windows, explicitly setting style to {target_style}")
            self.setWizardStyle(target_style)
        self._set_default_size(window_size)
        self._setup_dialog_button_icons()

    def _set_default_size(self, size: QSize):
        if (parent := self.parent()) is not None:
            parent_pos = parent.pos()
            available_space = self.screen().availableGeometry()
            # Clamp size to the available space
            new_width = min(available_space.width(), size.width())
            new_height = min(available_space.height(), size.height())
            # Clamp the window position to the screen so that it avoids
            # positioning the window decoration above the screen border.
            target_x = max(0, min(
                available_space.x()+available_space.width()-new_width,
                parent_pos.x() + (parent.width() - new_width)//2))
            target_y = max(0, min(  # This excludes the window decoration title bar
                available_space.y()+available_space.height()-new_height,
                parent_pos.y() + (parent.height() - new_height)//2))
            style = self.style()
            target_y += style.pixelMetric(style.PixelMetric.PM_TitleBarHeight)
            self.setGeometry(target_x, target_y, new_width, new_height)
        else:
            self.resize(size)

    def _setup_dialog_button_icons(self):
        for role, icon in self.BUTTON_ICONS.items():
            button = self.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))
