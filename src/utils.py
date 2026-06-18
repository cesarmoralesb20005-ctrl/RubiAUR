import sys
import os
import glob
import math
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QPen, QIcon
import shutil

def is_aur_helper_installed():
    """Devuelve True si yay o paru están instalados en el sistema."""
    return bool(shutil.which("yay") or shutil.which("paru"))

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    # Buscar en la carpeta assets un nivel arriba de src
    base_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base_path, "..", "assets", relative_path)
    if os.path.exists(asset_path):
        return asset_path
    return os.path.join(base_path, relative_path)


def get_ui_icon(icon_name, is_dark, custom_color=None):
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Si recibimos un color personalizado, lo usamos. Si no, usamos blanco/negro según el tema.
    if custom_color:
        color = QColor(custom_color)
    else:
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
    # NUEVO: Globo terráqueo dibujado
    elif icon_name == "web":
        painter.translate(32, 32)
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawEllipse(-20, -20, 40, 40)
        painter.drawEllipse(-10, -20, 20, 40)
        painter.drawLine(-20, 0, 20, 0)
        painter.resetTransform()
    # NUEVO: Caja/Paquete dibujado
    elif icon_name == "package":
        painter.translate(32, 32)
        pen.setWidth(4)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawRoundedRect(-20, -12, 40, 28, 4, 4)
        painter.drawLine(-20, -1, 20, -1)
        painter.drawLine(0, -1, 0, 16)
        painter.resetTransform()
        
    painter.end()
    return QIcon(pixmap)

def get_local_icon(app_name, size=64):
    clean = app_name.lower().replace("-bin", "").replace("-git", "").replace("-desktop", "").replace("-stable", "").replace("-launcher", "")
    
    # Intento 1: Nombre directo
    icon = QIcon.fromTheme(clean)
    if not icon.isNull(): return icon.pixmap(size, size)
    
    # Intento 2: Buscar en archivos .desktop
    desktop_dirs = ['/usr/share/applications', os.path.expanduser('~/.local/share/applications')]
    for d in desktop_dirs:
        if not os.path.exists(d): continue
        for f_path in glob.glob(os.path.join(d, f"*{clean}*.desktop")) + glob.glob(os.path.join(d, f"*{clean.split('-')[0]}*.desktop")):
            try:
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if line.startswith('Icon='):
                            icon_name = line.strip().split('=')[1]
                            icon = QIcon.fromTheme(icon_name)
                            if not icon.isNull(): 
                                return icon.pixmap(size, size)
            except Exception:
                pass
                
    # Intento 3: Partes del nombre
    parts = clean.split('-')
    if len(parts) > 1:
        icon = QIcon.fromTheme(parts[0])
        if not icon.isNull(): return icon.pixmap(size, size)
        
    # Intento 4: Mapeos manuales fuertes
    mappings = {
        "visual-studio-code": "code", "google-chrome": "google-chrome", "discord": "discord",
        "spotify": "spotify-client", "heroic-games": "heroic", "minecraft": "minecraft-launcher",
        "intellij-idea-community-edition": "intellij-idea", "pycharm-community-edition": "pycharm",
        "libreoffice-fresh": "libreoffice-main", "flameshot": "flameshot", "copyq": "copyq",
        "galculator": "galculator", "docker": "docker", "postman": "postman", "podman": "podman"
    }
    for key, val in mappings.items():
        if key in clean:
            icon = QIcon.fromTheme(val)
            if not icon.isNull(): return icon.pixmap(size, size)
            
    # Intento 5: Búsqueda manual profunda en el sistema de archivos
    themes = ["Tela", "Tela-dark", "breeze", "breeze-dark", "hicolor"]
    sizes_dirs = ["scalable/apps", "apps/scalable", "64x64/apps", "apps/64", "48x48/apps", "apps/48"]
    search_names = [clean]
    if clean in mappings:
        search_names.append(mappings[clean])
    
    for theme in themes:
        for size_dir in sizes_dirs:
            for sname in search_names:
                for ext in ["svg", "png"]:
                    p = f"/usr/share/icons/{theme}/{size_dir}/{sname}.{ext}"
                    if os.path.exists(p):
                        return QIcon(p).pixmap(size, size)
                        
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