import sys
import os
import math
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QPen, QIcon
import shutil



def is_aur_helper_installed():
    """Devuelve True si yay o paru están instalados en el sistema."""
    return bool(shutil.which("yay") or shutil.which("paru"))

# --- RUTAS ABSOLUTAS (MAGIA PARA PYINSTALLER/APPIMAGE) ---
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def get_ui_icon(icon_name, is_dark):
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    color = QColor("#FFFFFF") if is_dark else QColor("#1D1D1F")
    pen = QPen(color, 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    
    if icon_name == "back":
        path = QPainterPath()
        path.moveTo(40, 14); path.lineTo(22, 32); path.lineTo(40, 50)
        painter.drawPath(path)
    elif icon_name == "installed":
        painter.drawRoundedRect(12, 12, 16, 16, 5, 5)
        painter.drawRoundedRect(36, 12, 16, 16, 5, 5)
        painter.drawRoundedRect(12, 36, 16, 16, 5, 5)
        painter.drawRoundedRect(36, 36, 16, 16, 5, 5)
    elif icon_name == "settings":
        painter.translate(32, 32); painter.setPen(Qt.NoPen); painter.setBrush(color)
        for i in range(8):
            painter.drawRoundedRect(-5, -24, 10, 48, 3, 3); painter.rotate(45)
        painter.drawEllipse(-18, -18, 36, 36)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.drawEllipse(-8, -8, 16, 16)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver); painter.resetTransform()
    elif icon_name == "down_arrow":
        painter.translate(32, 32)
        pen.setWidth(6); painter.setPen(pen)
        path = QPainterPath(); path.moveTo(-14, -6); path.lineTo(0, 6); path.lineTo(14, -6)
        painter.drawPath(path)
        painter.resetTransform()
    elif icon_name == "check":
        painter.translate(32, 32)
        pen.setColor(QColor("#FFFFFF"))
        pen.setWidth(6); painter.setPen(pen)
        path = QPainterPath(); path.moveTo(-12, 0); path.lineTo(-2, 10); path.lineTo(14, -12)
        painter.drawPath(path)
        painter.resetTransform()
    elif icon_name == "history":
        painter.translate(32, 32)
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawEllipse(-18, -18, 36, 36)
        painter.drawLine(0, -10, 0, 0)
        painter.drawLine(0, 0, 8, 8)
        painter.resetTransform()
    elif icon_name == "star":
        painter.translate(32, 32)
        pen.setWidth(4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        path = QPainterPath()
        for i in range(10):
            r = 18 if i % 2 == 0 else 8
            angle = math.radians(i * 36 - 90)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            if i == 0: path.moveTo(x, y)
            else: path.lineTo(x, y)
        path.closeSubpath()
        painter.drawPath(path)
        painter.resetTransform()
    painter.end()
    return QIcon(pixmap)

def get_local_icon(app_name, size):
    clean = app_name.lower().replace("-bin", "").replace("-git", "").replace("-desktop", "").replace("-stable", "").replace("-launcher", "")
    icon = QIcon.fromTheme(clean)
    if not icon.isNull(): return icon.pixmap(size, size)
    parts = clean.split('-')
    if len(parts) > 1:
        icon = QIcon.fromTheme(parts[0])
        if not icon.isNull(): return icon.pixmap(size, size)
    mappings = {
        "visual-studio-code": "code", "google-chrome": "google-chrome", "discord": "discord",
        "spotify": "spotify-client", "heroic-games": "heroic", "minecraft": "minecraft-launcher",
        "intellij-idea-community-edition": "intellij-idea", "pycharm-community-edition": "pycharm",
        "libreoffice-fresh": "libreoffice-main"
    }
    for key, val in mappings.items():
        if key in clean:
            icon = QIcon.fromTheme(val)
            if not icon.isNull(): return icon.pixmap(size, size)
    return None

def create_rounded_pixmap(pixmap, size, radius):
    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)
    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, size, size, radius, radius)
    painter.setClipPath(path)
    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()
    return rounded


def is_aur_helper_installed():
    """Devuelve True si yay o paru están instalados en el sistema."""
    return bool(shutil.which("yay") or shutil.which("paru"))