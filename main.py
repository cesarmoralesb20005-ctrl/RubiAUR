import sys, subprocess, requests, threading, concurrent.futures, random, os, json, re, math, shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QFrame, QComboBox, QStackedWidget, QScrollArea, QGridLayout,
                             QMessageBox, QGraphicsOpacityEffect, QListWidget, QListWidgetItem,
                             QGraphicsDropShadowEffect, QStyledItemDelegate, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QObject, QPropertyAnimation, QEasingCurve, QSize, QPoint, QTimer, QSequentialAnimationGroup
from PySide6.QtGui import QFont, QPixmap, QImage, QPainter, QPainterPath, QIcon, QColor, QPen, QPalette

# --- RUTAS ABSOLUTAS (MAGIA PARA PYINSTALLER/APPIMAGE) ---
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# --- DICCIONARIO MAESTRO DE IDIOMAS ---
TRANSLATIONS = {
    "lang_lbl": {0: "Idioma de la Interfaz", 1: "Interface Language"},
    "lang_desc": {0: "Selecciona el idioma principal de RubiAUR.", 1: "Select the main language for RubiAUR."},
    "theme_lbl": {0: "Tema Visual", 1: "Visual Theme"},
    "theme_desc": {0: "Elige el aspecto de la aplicación.", 1: "Choose the appearance of the application."},
    "aur_lbl": {0: "Backend de AUR", 1: "AUR Backend"},
    "aur_desc": {0: "Herramienta que se utilizará para compilar y descargar.", 1: "Tool that will be used to compile and download."},
    "up_lbl": {0: "Actualizaciones del Sistema", 1: "System Updates"},
    "up_desc": {0: "Comportamiento del escáner de nuevas versiones.", 1: "Behavior of the new version scanner."},
    "settings_title": {0: "Configuración", 1: "Settings"},
    "reset_btn": {0: "Restablecer predeterminados", 1: "Reset to defaults"},
    "cache_lbl": {0: "Gestión de Caché", 1: "Cache Management"},
    "cache_desc": {0: "Elimina los archivos residuales tras instalar una aplicación.", 1: "Removes residual files after installing an application."},
    "search_placeholder": {0: "Buscar aplicaciones, juegos...", 1: "Search apps, games..."},
    "installed_btn": {0: " Instaladas", 1: " Installed"},
    "discover_title": {0: "Descubre en Arch Linux", 1: "Discover on Arch Linux"},
    "back_btn": {0: " Volver", 1: " Back"},
    "load_more": {0: " Cargar más aplicaciones", 1: " Load more applications"},
    "recent_visits": {0: "TUS VISITAS RECIENTES", 1: "YOUR RECENT VISITS"},
    "suggestions": {0: "SUGERENCIAS PARA TI", 1: "SUGGESTIONS FOR YOU"},
    "no_results": {0: "No se encontraron resultados", 1: "No results found"},
    "results_for": {0: "Resultados para '{}'", 1: "Results for '{}'"},
    "cat_Accesorios": {0: "Accesorios", 1: "Accessories"},
    "cat_Desarrollo": {0: "Desarrollo", 1: "Development"},
    "cat_Educación": {0: "Educación", 1: "Education"},
    "cat_Juegos": {0: "Juegos", 1: "Games"},
    "cat_Gráficos y Fotografía": {0: "Gráficos y Fotografía", 1: "Graphics & Photography"},
    "cat_Internet": {0: "Internet", 1: "Internet"},
    "cat_Multimedia": {0: "Multimedia", 1: "Multimedia"},
    "cat_Productividad": {0: "Productividad", 1: "Productivity"},
    "cat_Sistema": {0: "Sistema", 1: "System"},
    "cat_Utilidades": {0: "Utilidades", 1: "Utilities"},
    "inst_title": {0: "Aplicaciones Instaladas", 1: "Installed Applications"},
    "analyzing": {0: "Analizando sistema...", 1: "Analyzing system..."},
    "clean_sys": {0: "Limpiar Sistema", 1: "Clean System"},
    "check_sys": {0: "Buscar Actualizaciones", 1: "Check for Updates"},
    "inst_sys": {0: "Instalar Actualizaciones", 1: "Install Updates"},
    "sys_updated": {0: "Sistema actualizado", 1: "System up to date"},
    "filter_inst": {0: "Filtrar instalaciones...", 1: "Filter installations..."},
    "loading": {0: "Cargando...", 1: "Loading..."},
    "fetching_info": {0: "Obteniendo información del paquete...", 1: "Fetching package information..."},
    "size_est": {0: "Tamaño estimado: {}", 1: "Estimated size: {}"},
    "get_btn": {0: "Obtener", 1: "Get"},
    "uninstall_btn": {0: "Desinstalar", 1: "Uninstall"},
    "check_up_btn": {0: "Buscar actualización", 1: "Check for update"},
    "update_btn": {0: "Actualizar", 1: "Update"},
    "open_btn": {0: "Abrir", 1: "Open"},
    "cancel_btn": {0: "Cancelar", 1: "Cancel"},
    "comm_info": {0: "Información de la Comunidad", 1: "Community Information"},
    "src_pacman": {0: " Oficial (Pacman)", 1: " Official (Pacman)"},
    "src_aur": {0: " Comunidad (AUR)", 1: " Community (AUR)"},
    "pop_exc": {0: "Popularidad: Excepcional", 1: "Popularity: Exceptional"},
    "pop_vhigh": {0: "Popularidad: Muy Alta", 1: "Popularity: Very High"},
    "pop_high": {0: "Popularidad: Alta", 1: "Popularity: High"},
    "pop_mod": {0: "Popularidad: Moderada", 1: "Popularity: Moderate"},
    "pop_new": {0: "Popularidad: Nueva / Desconocida", 1: "Popularity: New / Unknown"},
    "qual_off": {0: "Calidad: Paquete Oficial", 1: "Quality: Official Package"},
    "opt_auto": {0: "Automático", 1: "Automatic"},
    "opt_light": {0: "Claro", 1: "Light"},
    "opt_dark": {0: "Oscuro", 1: "Dark"},
    "opt_clean_auto": {0: "Limpieza Automática", 1: "Automatic Cleanup"},
    "opt_clean_man": {0: "Manual", 1: "Manual"},
    "opt_up_start": {0: "Buscar al iniciar", 1: "Check on startup"},
    "opt_up_no": {0: "No buscar automáticamente", 1: "Do not check automatically"},
    "installing_yay": {0: "Instalando dependencias necesarias (yay)...", 1: "Installing required dependencies (yay)..."}
}

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

# --- WIDGETS PERSONALIZADOS ---
class ToastNotification(QFrame):
    def __init__(self, parent, title, message, is_dark):
        super().__init__(parent)
        self.setObjectName("Notification")
        self.setFixedSize(350, 70)
        
        bg_color = "#2C2C2E" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#1D1D1F"
        border_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.05)"
        
        self.setStyleSheet(f"""
            #Notification {{ background-color: {bg_color}; border-radius: 20px; border: 1px solid {border_color}; }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        self.icon_lbl = QLabel()
        pix = QPixmap(30, 30)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#0071E3"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, 30, 30)
        p.setPen(QPen(Qt.white, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawLine(15, 8, 15, 22)
        p.drawLine(15, 22, 9, 16)
        p.drawLine(15, 22, 21, 16)
        p.end()
        self.icon_lbl.setPixmap(pix)
        layout.addWidget(self.icon_lbl)
        
        text_lay = QVBoxLayout()
        text_lay.setSpacing(2)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 14px;")
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet("color: #8E8E93; font-size: 12px;")
        
        text_lay.addWidget(title_lbl)
        text_lay.addWidget(msg_lbl)
        layout.addLayout(text_lay)
        layout.addStretch()
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30 if not is_dark else 80))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_anim)
        
    def show_anim(self):
        parent_w = self.parent().width()
        x = (parent_w - self.width()) // 2
        start_y = -self.height() - 20
        end_y = 20
        self.setGeometry(x, start_y, self.width(), self.height())
        self.show()
        self.raise_()
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(400)
        self.anim.setStartValue(QPoint(x, start_y))
        self.anim.setEndValue(QPoint(x, end_y))
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()
        self.timer.start(5000)
        
    def hide_anim(self):
        self.timer.stop()
        x = self.x()
        start_y = self.y()
        end_y = -self.height() - 20
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(400)
        self.anim.setStartValue(QPoint(x, start_y))
        self.anim.setEndValue(QPoint(x, end_y))
        self.anim.setEasingCurve(QEasingCurve.InBack)
        self.anim.finished.connect(self.deleteLater)
        self.anim.start()

class LoadingSpinner(QWidget):
    def __init__(self, parent=None, size=24):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.color = QColor("#1D1D1F")

    def update_theme(self, is_dark):
        self.color = QColor("#FFFFFF") if is_dark else QColor("#1D1D1F")
        self.update()

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def start(self):
        self.show()
        self.timer.start(80) 

    def stop(self):
        self.hide()
        self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        for i in range(12):
            alpha = int(255 - (i * 255 / 12))
            pen = QPen(QColor(self.color.red(), self.color.green(), self.color.blue(), alpha))
            pen.setWidth(max(2, self.width() // 10))
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(0, self.width() // 4, 0, self.width() // 2)
            painter.rotate(-30)
        painter.end()

class PacmanProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setFixedWidth(150)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_anim)
        self.mouth_open = 0
        self.mouth_dir = 1
        self.pacman_x = 0
        self.is_active = False
        self.is_dark = False

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        self.update()

    def start(self):
        self.is_active = True
        self.show()
        self.timer.start(40)

    def stop(self):
        self.is_active = False
        self.hide()
        self.timer.stop()

    def update_anim(self):
        self.mouth_open += 5 * self.mouth_dir
        if self.mouth_open >= 35: self.mouth_dir = -1
        elif self.mouth_open <= 0: self.mouth_dir = 1
        self.pacman_x = (self.pacman_x + 3)
        if self.pacman_x > self.width() + 20: 
            self.pacman_x = -20
        self.update()

    def paintEvent(self, e):
        if not self.is_active: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        dot_color = QColor("#FFFFFF") if self.is_dark else QColor("#1D1D1F")
        painter.setBrush(dot_color)
        painter.setPen(Qt.NoPen)
        for i in range(10, self.width(), 20):
            if i > self.pacman_x + 10 or self.pacman_x > self.width():
                painter.drawEllipse(i, 15, 6, 6)
        painter.setBrush(QColor("#FFCC00"))
        span_angle = (360 - self.mouth_open * 2) * 16
        start_angle = self.mouth_open * 16
        painter.drawPie(int(self.pacman_x), 6, 24, 24, start_angle, span_angle)
        painter.end()

class SearchLineEdit(QLineEdit):
    clicked = Signal()
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()

class FadeStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.next_index = 0
        self.effect = None
        self.anim = None

    def set_current_index_animated(self, index):
        if index == self.currentIndex(): return
        self.next_index = index
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(150)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.finished.connect(self._on_fade_out_finished)
        self.anim.start()

    def _on_fade_out_finished(self):
        self.anim.finished.disconnect(self._on_fade_out_finished)
        super().setCurrentIndex(self.next_index)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.finished.connect(self._on_fade_in_finished)
        self.anim.start()
        
    def _on_fade_in_finished(self):
        self.anim.finished.disconnect(self._on_fade_in_finished)
        self.setGraphicsEffect(None)

# --- TRABAJADOR INSTALADOR YAY ---
class AurInstallerWorker(QObject):
    finished = Signal(bool, str)
    def run(self):
        def execute():
            try:
                # 1. Update and install dependencies using pkexec (GUI prompt)
                subprocess.run(["pkexec", "pacman", "-Syu", "--needed", "--noconfirm", "base-devel", "git"], check=True)
                
                # 2. Clone into ~/.cache to avoid permission issues
                build_dir = os.path.expanduser("~/.cache/rubiaur_yay_build")
                subprocess.run(["rm", "-rf", build_dir])
                subprocess.run(["git", "clone", "https://aur.archlinux.org/yay-bin.git", build_dir], check=True)
                
                # 3. Build package. PACMAN_AUTH prevents sudo from hanging the GUI
                env = os.environ.copy()
                env["PACMAN_AUTH"] = "pkexec"
                
                subprocess.run(["makepkg", "-s", "--noconfirm"], cwd=build_dir, env=env, check=True)
                
                # 4. Find the built package and install it explicitly with pkexec
                import glob
                pkg_files = glob.glob(os.path.join(build_dir, "*.pkg.tar.zst"))
                if not pkg_files:
                    raise Exception("El paquete no se generó.")
                
                subprocess.run(["pkexec", "pacman", "-U", "--noconfirm", pkg_files[0]], check=True)
                
                self.finished.emit(True, "Yay instalado correctamente")
            except Exception as e:
                self.finished.emit(False, str(e))
        threading.Thread(target=execute).start()

# --- CATÁLOGO CON DICCIONARIOS INTERNOS ---
HOME_CATEGORIES = {
    "Accesorios": [
        ("flameshot", {0: "Potente herramienta de captura de pantalla con anotaciones.", 1: "Powerful screenshot tool with annotations."}),
        ("copyq", {0: "Avanzado gestor de portapapeles con historial de copiado.", 1: "Advanced clipboard manager with copy history."}),
        ("galculator", {0: "Calculadora científica y algebraica fácil de usar.", 1: "Easy to use scientific and algebraic calculator."}),
        ("xpad", {0: "Aplicación de notas adhesivas para el escritorio.", 1: "Sticky note application for the desktop."})
    ],
    "Desarrollo": [
        ("visual-studio-code-bin", {0: "Editor de código fuente ligero y potente.", 1: "Lightweight and powerful source code editor."}),
        ("podman", {0: "Herramienta para gestionar contenedores.", 1: "Tool for managing containers (Docker alternative)."}),
        ("docker", {0: "Plataforma de contenedores para desarrollo.", 1: "Container platform for development and deployment."}),
        ("postman-bin", {0: "Plataforma para el desarrollo y prueba de APIs.", 1: "Platform for API development and testing."})
    ],
    "Educación": [
        ("stellarium", {0: "Planetario 3D de código abierto para tu computadora.", 1: "Open source 3D planetarium for your computer."}),
        ("kstars", {0: "Software de astronomía de escritorio del proyecto KDE.", 1: "Desktop astronomy software by the KDE project."}),
        ("anki", {0: "Programa de tarjetas de memoria para el aprendizaje.", 1: "Flashcard program for learning."}),
        ("geogebra", {0: "Software de matemáticas dinámicas.", 1: "Dynamic mathematics software for all levels."})
    ],
    "Juegos": [
        ("steam", {0: "La plataforma de distribución de juegos de Valve.", 1: "Valve's game distribution platform."}),
        ("lutris", {0: "Plataforma abierta para gestionar y jugar en Linux.", 1: "Open platform for gaming on Linux."}),
        ("retroarch", {0: "Frontend para emuladores, motores de juegos y reproductores.", 1: "Frontend for emulators, game engines and players."}),
        ("minecraft-launcher", {0: "Lanzador oficial para jugar Minecraft.", 1: "Official launcher to play Minecraft."})
    ],
    "Gráficos y Fotografía": [
        ("gimp", {0: "Poderoso editor de imágenes libre.", 1: "Powerful free image editor (GNU)."}),
        ("inkscape", {0: "Editor de gráficos vectoriales profesional libre.", 1: "Professional free vector graphics editor."}),
        ("krita", {0: "Software de pintura digital e ilustración.", 1: "Digital painting and illustration software."}),
        ("darktable", {0: "Flujo de trabajo de fotografía de código abierto y revelador RAW.", 1: "Open source photography workflow and RAW developer."})
    ],
    "Internet": [
        ("google-chrome", {0: "El navegador rápido y seguro de Google.", 1: "Fast and secure web browser by Google."}),
        ("firefox", {0: "Navegador web libre y enfocado en la privacidad.", 1: "Free and privacy-focused web browser."}),
        ("discord", {0: "Chat de voz, video y texto para comunidades.", 1: "Voice, video and text chat for communities."}),
        ("telegram-desktop", {0: "Aplicación de mensajería rápida, segura y sincronizada.", 1: "Fast, secure and synced messaging app."})
    ],
    "Multimedia": [
        ("vlc", {0: "El reproductor multimedia definitivo.", 1: "The ultimate cross-platform media player."}),
        ("spotify", {0: "Servicio de streaming de música líder.", 1: "Leading music streaming service."}),
        ("obs-studio", {0: "Software libre para grabación y streaming.", 1: "Free software for video recording and live streaming."}),
        ("kdenlive", {0: "Editor de video no lineal potente.", 1: "Powerful non-linear video editor."})
    ],
    "Productividad": [
        ("libreoffice-fresh", {0: "La suite de oficina de código abierto más popular.", 1: "The most popular open source office suite."}),
        ("obsidian", {0: "Base de conocimientos Markdown local.", 1: "Powerful knowledge base built on local Markdown files."}),
        ("notion-app-bin", {0: "Espacio de trabajo todo en uno.", 1: "All-in-one workspace for notes and tasks."}),
        ("evince", {0: "Visor de documentos ligero (PDF, XPS, etc.).", 1: "Lightweight document viewer (PDF, XPS, etc.)."})
    ],
    "Sistema": [
        ("htop", {0: "Visor de procesos interactivo en modo texto.", 1: "Interactive text-mode process viewer."}),
        ("btop", {0: "Monitor de recursos con interfaz interactiva.", 1: "Resource monitor with an attractive interface."}),
        ("timeshift", {0: "Utilidad de restauración del sistema.", 1: "System restore utility (backups)."}),
        ("gparted", {0: "Editor de particiones de disco gráfico.", 1: "Graphical disk partition editor."})
    ],
    "Utilidades": [
        ("peazip", {0: "Herramienta de compresión de archivos.", 1: "File compression tool."}),
        ("file-roller", {0: "Gestor de archivos comprimidos.", 1: "Archive manager."}),
        ("alacritty", {0: "Emulador de terminal acelerado por GPU ultrarrápido.", 1: "Ultra-fast GPU-accelerated terminal emulator."}),
        ("kitty", {0: "Emulador de terminal moderno y rápido.", 1: "Modern and fast terminal emulator."})
    ]
}

# --- 2. TRABAJADORES EN SEGUNDO PLANO ---
class AutocompleteWorker(QObject):
    results_ready = Signal(list, str)
    def search(self, query):
        def run():
            query_clean = query.lower().strip()
            if not query_clean: return
            pacman_pkgs = set()
            aur_pkgs = set()
            try:
                proc = subprocess.run(['pacman', '-Ssq', f"^{query_clean}"], capture_output=True, text=True)
                if proc.returncode == 0: pacman_pkgs = set(p for p in proc.stdout.strip().split('\n') if p)
            except: pass
            try:
                url = f"https://aur.archlinux.org/rpc/?v=5&type=suggest&arg={query_clean}"
                res = requests.get(url, timeout=2).json()
                if isinstance(res, list): aur_pkgs = set(res)
            except: pass
            all_pkgs = pacman_pkgs.union(aur_pkgs)
            combined = []
            for pkg in all_pkgs:
                combined.append({"name": pkg, "has_pacman": pkg in pacman_pkgs, "has_aur": pkg in aur_pkgs})
            def sort_logic(x):
                name = x["name"].lower()
                if name == query_clean: return 0
                if name.startswith(query_clean): return 1
                return 2
            combined.sort(key=lambda x: (sort_logic(x), len(x["name"]), x["name"]))
            self.results_ready.emit(combined[:10], query)
        threading.Thread(target=run).start()

class CheckUpdateWorker(QObject):
    app_result = Signal(bool, str)
    sys_result = Signal(int)

    def check_app(self, pkg):
        def run():
            has_up = False
            ver = ""
            try:
                out_aur = subprocess.run(['yay', '-Qua'], capture_output=True, text=True).stdout or ""
                out_repo = subprocess.run(['checkupdates'], capture_output=True, text=True).stdout or ""
                out_local = subprocess.run(['yay', '-Qu'], capture_output=True, text=True).stdout or ""
                all_lines = out_aur.split('\n') + out_repo.split('\n') + out_local.split('\n')
                for line in all_lines:
                    line = line.strip()
                    if ' -> ' in line and line.startswith(pkg + " "):
                        has_up = True
                        parts = line.split(' -> ')
                        if len(parts) >= 2: ver = parts[1].split()[0]
                        break
            except Exception: pass
            self.app_result.emit(has_up, ver)
        threading.Thread(target=run).start()

    def check_sys(self):
        def run():
            count = 0
            try:
                proc_repo = subprocess.run(['checkupdates'], capture_output=True, text=True)
                if proc_repo.stdout:
                    lines = [l for l in proc_repo.stdout.strip().split('\n') if ' -> ' in l]
                    count += len(lines)
            except Exception: pass
            try:
                proc_aur = subprocess.run(['yay', '-Qua'], capture_output=True, text=True)
                if proc_aur.stdout:
                    lines = [l for l in proc_aur.stdout.strip().split('\n') if ' -> ' in l]
                    count += len(lines)
            except Exception: pass
            if count == 0:
                try:
                    proc_local = subprocess.run(['yay', '-Qu'], capture_output=True, text=True)
                    if proc_local.stdout:
                        lines = [l for l in proc_local.stdout.strip().split('\n') if ' -> ' in l]
                        count = len(lines)
                except Exception: pass
            self.sys_result.emit(count)
        threading.Thread(target=run).start()

class InstallWorker(QObject):
    finished = Signal(bool, str, str)
    progress = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.process = None
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True
        if self.process:
            try:
                self.process.terminate()
            except:
                pass

    def run_command(self, action, source, pkg=None, aur_backend="yay"):
        self.is_cancelled = False
        def execute():
            try:
                if action in ["install", "update_app"]:
                    if source == "pacman": cmd = ["pkexec", "pacman", "-S", "--noconfirm", pkg]
                    else: cmd = [aur_backend, "-S", "--noconfirm", "--sudo", "pkexec", pkg]
                elif action == "uninstall": 
                    if source == "pacman": cmd = ["pkexec", "pacman", "-Rns", "--noconfirm", pkg]
                    else: cmd = [aur_backend, "-Rns", "--noconfirm", "--sudo", "pkexec", pkg]
                elif action == "update_sys": cmd = [aur_backend, "-Syu", "--noconfirm", "--sudo", "pkexec"]
                elif action == "clean_sys": cmd = [aur_backend, "-Yc", "--noconfirm", "--sudo", "pkexec"]
                
                self.process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
                )
                
                for line in iter(self.process.stdout.readline, ''):
                    if self.is_cancelled: break
                    if line: self.progress.emit(line.strip(), action)
                
                self.process.stdout.close()
                return_code = self.process.wait()
                
                if self.is_cancelled:
                    self.finished.emit(False, "Operación cancelada por el usuario.", action)
                elif return_code == 0: 
                    self.finished.emit(True, "Éxito", action)
                else: 
                    self.finished.emit(False, "Ocurrió un error. Revisa la consola o verifica tu conexión.", action)
            except Exception as e:
                if not self.is_cancelled:
                    self.finished.emit(False, str(e), action)
        threading.Thread(target=execute).start()

class InstalledAppsWorker(QObject):
    finished = Signal(list)
    def load(self):
        def run():
            try:
                proc_explicit = subprocess.run(['pacman', '-Qeq'], capture_output=True, text=True)
                explicit_pkgs = set(proc_explicit.stdout.strip().split('\n'))
            except: explicit_pkgs = set()
            known_apps = {app[0] for cat in HOME_CATEGORIES.values() for app in cat}
            valid_pkgs = explicit_pkgs.union(known_apps)

            proc = subprocess.run(['pacman', '-Qi'], capture_output=True, text=True)
            results = []
            if proc.returncode == 0:
                blocks = proc.stdout.strip().split('\n\n')
                for block in blocks:
                    lines = block.split('\n')
                    name, desc = "", ""
                    for line in lines:
                        if line.startswith("Name") or line.startswith("Nombre"):
                            name = line.split(":", 1)[1].strip()
                        elif line.startswith("Description") or line.startswith("Descripción"):
                            desc = line.split(":", 1)[1].strip()
                    
                    if name and name in valid_pkgs:
                        cat = "Otras Aplicaciones"
                        n_l = name.lower()
                        d_l = desc.lower()
                        if any(k in n_l or k in d_l for k in ['browser', 'navegador', 'web', 'internet', 'mail', 'email', 'chat', 'messenger', 'discord', 'telegram', 'network']): cat = "Internet"
                        elif any(k in n_l or k in d_l for k in ['game', 'juego', 'emulator', 'steam', 'arcade', 'play']): cat = "Juegos"
                        elif any(k in n_l or k in d_l for k in ['media', 'audio', 'video', 'player', 'music', 'sound']): cat = "Multimedia"
                        elif any(k in n_l or k in d_l for k in ['image', 'photo', 'graphic', 'draw', 'paint', '3d']): cat = "Gráficos y Fotografía"
                        elif any(k in n_l or k in d_l for k in ['develop', 'compiler', 'ide', 'editor', 'docker', 'podman', 'git', 'program', 'code']): cat = "Desarrollo"
                        elif any(k in n_l or k in d_l for k in ['office', 'document', 'pdf', 'note', 'task', 'producti', 'text']): cat = "Productividad"
                        elif any(k in n_l or k in d_l for k in ['education', 'science', 'math', 'learn', 'astro']): cat = "Educación"
                        elif any(k in n_l or k in d_l for k in ['system', 'monitor', 'manager', 'driver', 'kernel', 'desktop', 'theme', 'config', 'boot', 'backup']): cat = "Sistema"
                        elif any(k in n_l or k in d_l for k in ['util', 'tool', 'archive', 'compress', 'zip', 'extract']): cat = "Utilidades"
                        elif any(k in n_l or k in d_l for k in ['accessory', 'calc', 'clip', 'desk', 'clock']): cat = "Accesorios"
                        if cat == "Otras Aplicaciones" and (name.startswith('lib') or name.endswith('-lib')): continue
                        results.append({
                            "name": name, "desc": desc if desc else "Aplicación del sistema",
                            "has_pacman": True, "has_aur": False, "votes": 9999, "category": cat
                        })
            results.sort(key=lambda x: x['name'])
            self.finished.emit(results)
        threading.Thread(target=run).start()

class CategoryWorker(QObject):
    finished = Signal(list, str)
    def load_category(self, app_list, cat_name):
        def run():
            results = {}
            for app in app_list:
                results[app] = {"name": app, "desc": "Cargando...", "has_pacman": False, "has_aur": False, "votes": 0}
                try:
                    proc = subprocess.run(['pacman', '-Si', app], capture_output=True, text=True)
                    if proc.returncode == 0:
                        lines = proc.stdout.split('\n')
                        desc = next((l for l in lines if l.startswith('Descripción') or l.startswith('Description')), "Desc: ").split(': ', 1)[-1]
                        results[app]["has_pacman"] = True
                        results[app]["desc"] = desc
                        results[app]["votes"] = 9999
                except: pass
            try:
                url = "https://aur.archlinux.org/rpc/?v=5&type=info"
                for app in app_list: url += f"&arg[]={app}"
                res = requests.get(url).json()
                if res.get('results'):
                    for item in res['results']:
                        name = item['Name']
                        if name in results:
                            results[name]["has_aur"] = True
                            if not results[name]["has_pacman"]: results[name]["desc"] = item.get('Description', 'Sin descripción')
                            results[name]["votes"] = item.get('NumVotes', 0)
            except: pass
            self.finished.emit([results[app] for app in app_list], cat_name)
        threading.Thread(target=run).start()

class IconWorker(QObject):
    icon_data_ready = Signal(str, bytes)
    def load_icons(self, apps_list):
        def fetch_single(app_name):
            icon_url = None
            search_term = app_name.replace("-bin", "").replace("-git", "").replace("-launcher", "").replace("-desktop", "").replace("-", " ")
            try:
                res = requests.get(f"https://itunes.apple.com/search?term={search_term}&entity=software&limit=1", timeout=3).json()
                if res['resultCount'] > 0: icon_url = res['results'][0]['artworkUrl100'].replace('100x100', '256x256')
            except: pass
            if icon_url:
                try:
                    img_data = requests.get(icon_url, timeout=3).content
                    self.icon_data_ready.emit(app_name, img_data)
                except: pass
        def run():
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(fetch_single, apps_list)
        threading.Thread(target=run).start()

class SearchListWorker(QObject):
    finished = Signal(list)
    def search(self, query):
        def run():
            query_clean = query.lower().strip()
            results = {} 
            try:
                proc = subprocess.run(['pacman', '-Ss', query_clean], capture_output=True, text=True)
                if proc.returncode == 0:
                    lines = proc.stdout.strip().split('\n')
                    for i in range(0, len(lines), 2):
                        if i+1 < len(lines):
                            header = lines[i].strip()
                            desc = lines[i+1].strip()
                            pkg_name = header.split(' ')[0].split('/')[1]
                            results[pkg_name] = {"name": pkg_name, "desc": desc, "has_pacman": True, "has_aur": False, "votes": 9999}
            except: pass
            try:
                res = requests.get(f"https://aur.archlinux.org/rpc/?v=5&type=search&arg={query_clean}").json()
                if res.get('results'):
                    for item in res['results']:
                        pkg_name = item['Name']
                        if pkg_name in results: results[pkg_name]["has_aur"] = True
                        else: results[pkg_name] = {"name": pkg_name, "desc": item.get('Description', 'Sin descripción'), "has_pacman": False, "has_aur": True, "votes": item.get('NumVotes', 0)}
            except: pass
            result_list = list(results.values())
            def sort_key(x):
                name = x['name'].lower()
                if name == query_clean: return 0
                if name in [f"{query_clean}-bin", f"{query_clean}-launcher", f"{query_clean}-git", f"{query_clean}-desktop"]: return 1
                if name.startswith(query_clean): return 2
                return 3
            result_list.sort(key=lambda x: (sort_key(x), -x.get('votes', 0)))
            self.finished.emit(result_list[:30])
        threading.Thread(target=run).start()

class DetailWorker(QObject):
    finished = Signal(dict)
    def load_details(self, app_data):
        def run():
            name = app_data['name']
            check = subprocess.run(['pacman', '-Qq', name], capture_output=True)
            app_data["is_installed"] = (check.returncode == 0)

            app_data["icon_url"] = None
            search_term = name.replace("-bin", "").replace("-git", "").replace("-launcher", "").replace("-desktop", "").replace("-", " ")
            try:
                itunes_url = f"https://itunes.apple.com/search?term={search_term}&entity=software&limit=1"
                res = requests.get(itunes_url).json()
                if res['resultCount'] > 0: app_data["icon_url"] = res['results'][0]['artworkUrl100'].replace('100x100', '256x256')
            except: pass

            app_data["size"] = "Variable"
            if app_data['has_pacman']:
                try:
                    proc = subprocess.run(['pacman', '-Si', name], capture_output=True, text=True)
                    lines = proc.stdout.split('\n')
                    app_data["size"] = next((l for l in lines if 'Tamaño' in l or 'Installed Size' in l), "Size: ").split(': ', 1)[-1]
                except: pass

            app_data["comments"] = []
            if app_data['has_aur']:
                try:
                    aur_page = requests.get(f"https://aur.archlinux.org/packages/{name}", timeout=3).text
                    matches = re.findall(r'<div class="article-content">\s*<p>(.*?)</p>\s*</div>', aur_page, re.IGNORECASE | re.DOTALL)
                    if matches: app_data["comments"] = [re.sub(r'<[^>]+>', '', m).strip() for m in matches[:2]]
                except: pass

            self.finished.emit(app_data)
        threading.Thread(target=run).start()

# --- 3. WIDGETS PERSONALIZADOS ---
class HomeAppCard(QFrame):
    clicked = Signal(str)
    def __init__(self, name, desc_dict, lang_idx):
        super().__init__()
        self.app_name = name
        self.desc_dict = desc_dict
        self.setObjectName("HomeCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(90)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.icon_lbl = QLabel(name[0].upper())
        self.icon_lbl.setFixedSize(60, 60)
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setStyleSheet("background-color: #0071E3; color: white; border-radius: 12px; font-weight: bold; font-size: 26px;")
        
        local_pix = get_local_icon(name, 60)
        if local_pix:
            self.icon_lbl.setStyleSheet("background-color: transparent;")
            self.icon_lbl.setPixmap(create_rounded_pixmap(local_pix, 60, 12))
        
        v_lay = QVBoxLayout()
        name_lbl = QLabel(name.replace("-bin", "").replace("-desktop", "").capitalize())
        name_lbl.setFont(QFont("SF Pro Display", 14, QFont.Bold))
        
        self.desc_lbl = QLabel(self.get_desc(lang_idx))
        self.desc_lbl.setStyleSheet("color: #8E8E93; font-size: 12px;")
        self.desc_lbl.setWordWrap(True)
        
        v_lay.addWidget(name_lbl)
        v_lay.addWidget(self.desc_lbl)
        v_lay.addStretch()
        
        layout.addWidget(self.icon_lbl)
        layout.addSpacing(10)
        layout.addLayout(v_lay)

    def get_desc(self, lang_idx):
        desc = self.desc_dict.get(lang_idx, self.desc_dict[0])
        return desc[:65] + "..." if len(desc) > 65 else desc

    def update_lang(self, lang_idx):
        self.desc_lbl.setText(self.get_desc(lang_idx))

    def set_icon(self, pixmap):
        self.icon_lbl.setStyleSheet("background-color: transparent;")
        self.icon_lbl.setPixmap(pixmap)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.app_name)

class AppListItem(QFrame):
    clicked = Signal(dict)
    def __init__(self, data, is_dark, tr_func, parent=None):
        super().__init__(parent)
        self.data = data
        self.is_dark = is_dark
        self.tr = tr_func
        self.setObjectName("ListItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(80)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        self.icon_lbl = QLabel(data['name'][0].upper())
        self.icon_lbl.setFixedSize(50, 50)
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setStyleSheet("background-color: #0071E3; color: white; border-radius: 12px; font-weight: bold; font-size: 24px;")

        local_pix = get_local_icon(data['name'], 50)
        if local_pix:
            self.icon_lbl.setStyleSheet("background-color: transparent;")
            self.icon_lbl.setPixmap(create_rounded_pixmap(local_pix, 50, 12))

        v_lay = QVBoxLayout()
        name_lbl = QLabel(data['name'])
        name_lbl.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        desc_lbl = QLabel(data['desc'][:80] + "..." if len(data['desc']) > 80 else data['desc'])
        desc_lbl.setStyleSheet("color: #8E8E93;")
        v_lay.addWidget(name_lbl)
        v_lay.addWidget(desc_lbl)
        
        tags_lay = QVBoxLayout()
        if data.get('has_pacman'):
            tag_pacman = QFrame()
            tag_pacman.setStyleSheet("background-color: #1D1D1F; padding: 4px 8px; border-radius: 6px;")
            p_lay = QHBoxLayout(tag_pacman); p_lay.setContentsMargins(0,0,0,0); p_lay.setSpacing(5)
            ico = QLabel(); ico.setPixmap(QIcon(get_resource_path("pacman.svg")).pixmap(14, 14)) 
            lbl = QLabel("Pacman")
            lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 11px; border: none; background: transparent;")
            p_lay.addWidget(ico); p_lay.addWidget(lbl)
            tags_lay.addWidget(tag_pacman)

        if data.get('has_aur'):
            tag_aur = QFrame()
            tag_aur.setStyleSheet("background-color: #0071E3; padding: 4px 8px; border-radius: 6px;")
            a_lay = QHBoxLayout(tag_aur); a_lay.setContentsMargins(0,0,0,0); a_lay.setSpacing(5)
            ico = QLabel(); ico.setPixmap(QIcon(get_resource_path("aur.svg")).pixmap(14, 14)) 
            lbl = QLabel("AUR")
            lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 11px; border: none; background: transparent;")
            a_lay.addWidget(ico); a_lay.addWidget(lbl)
            tags_lay.addWidget(tag_aur)
            
        tags_lay.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        layout.addWidget(self.icon_lbl)
        layout.addSpacing(15)
        layout.addLayout(v_lay)
        layout.addStretch()
        layout.addLayout(tags_lay)

    def set_icon(self, pixmap):
        self.icon_lbl.setStyleSheet("background-color: transparent;")
        self.icon_lbl.setPixmap(pixmap)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicked.emit(self.data)
        
    def animate_entry(self, delay=0):
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0.0)
        self.anim_group = QSequentialAnimationGroup(self)
        if delay > 0: self.anim_group.addPause(delay)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim_group.addAnimation(self.anim)
        self.anim_group.finished.connect(lambda: self.setGraphicsEffect(None))
        self.anim_group.start()

# --- 4. INTERFAZ PRINCIPAL ---
class RubiAUR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RubiAUR")
        self.setMinimumSize(750, 550) 
        self.resize(900, 650)
        
        self.last_view = 0
        self.icon_cache = {} 
        self.search_history = []
        # Inglés por defecto
        self.app_settings = {"lang": 1, "aur": 0, "cache": 0, "updates": 0, "theme": 0}
        
        self.active_install_pkg = None
        self.active_install_action = None
        self.active_install_source = None
        
        self.cat_buttons = {} 
        self.settings_labels = [] 
        
        self.load_settings()
        self.load_history()

        theme_val = self.app_settings.get("theme", 0)
        if theme_val == 0:
            self.is_dark = QApplication.palette().color(QPalette.Window).lightness() < 128
        else:
            self.is_dark = (theme_val == 2)
        
        self.search_worker = SearchListWorker()
        self.search_worker.finished.connect(self.populate_list)
        self.category_worker = CategoryWorker()
        self.category_worker.finished.connect(self.populate_category)
        self.installed_worker = InstalledAppsWorker()
        self.installed_worker.finished.connect(self.populate_installed)
        self.detail_worker = DetailWorker()
        self.detail_worker.finished.connect(self.update_detail_ui)
        self.icon_worker = IconWorker()
        self.icon_worker.icon_data_ready.connect(self.apply_icon)
        
        self.autocomplete_worker = AutocompleteWorker()
        self.autocomplete_worker.results_ready.connect(self.show_autocomplete_results)
        
        self.install_worker = InstallWorker()
        self.install_worker.finished.connect(self.on_install_finished)
        self.install_worker.progress.connect(self.update_install_progress) 
        
        self.check_worker = CheckUpdateWorker()
        self.check_worker.app_result.connect(self.on_app_update_checked)
        self.check_worker.sys_result.connect(self.on_sys_update_checked)
        
        self.current_app_data = {}
        self.home_cards_refs = {} 
        self.list_items_refs = {} 
        
        self.all_installed_results = []
        self.filtered_installed_results = []
        self.current_inst_index = 0
        self.inst_load_more_container = None

        self.current_cat_name = ""
        self.current_cat_apps = []
        self.current_cat_index = 0
        self.cat_load_more_container = None

        self.light_style = """
            QMainWindow, #CentralWidget, #MainBg { background-color: #F5F5F7; }
            #Header { background-color: #FFFFFF; border-bottom: 1px solid rgba(0,0,0,0.05); }
            #AppCard, #ListContainer { background-color: white; border-radius: 20px; border: 1px solid rgba(0,0,0,0.05); }
            #HomeCard { background-color: white; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); }
            #HomeCard:hover { background-color: #F2F2F7; }
            .ActionBtn { font-weight: bold; font-size: 14px; border-radius: 16px; padding: 0px 20px; border: none; }
            #InstallBtn { background-color: #0071E3; color: white; }
            #UninstallBtn { background-color: #F2F2F7; color: #FF3B30; }
            #BackBtn { background-color: transparent; color: #0071E3; font-weight: bold; font-size: 14px; text-align: left; border: none; }
            #BackBtn:hover { text-decoration: underline; }
            #LogoBtn { background-color: transparent; color: #1D1D1F; font-size: 20px; font-weight: bold; text-align: left; border: none; padding: 6px 12px; border-radius: 12px;}
            #LogoBtn:hover { background-color: #F2F2F7; }
            #LogoBtn[active="true"] { background-color: #E6F0FF; color: #0071E3; }
            #HeaderActionBtn { background-color: transparent; color: #0071E3; font-size: 14px; font-weight: bold; border: none; padding: 8px 15px; border-radius: 12px; }
            #HeaderActionBtn:hover { background-color: #F2F2F7; }
            #HeaderActionBtn[active="true"] { background-color: #E6F0FF; color: #0071E3; }
            #IconBtn { background-color: transparent; border: none; border-radius: 12px; }
            #IconBtn:hover { background-color: #F2F2F7; }
            #IconBtn[active="true"] { background-color: #E6F0FF; }
            #CategoryTitleBtn { text-align: left; font-size: 22px; font-weight: bold; background: transparent; border: none; padding: 5px 0px; margin: 0; color: #1D1D1F; }
            #CategoryTitleBtn:hover { color: #0071E3; }
            #ListItem { background-color: white; border-radius: 12px; border: none; border-bottom: 1px solid rgba(0,0,0,0.05); }
            #ListItem:hover { background-color: #F2F2F7; }
            QComboBox { background-color: #F2F2F7; color: #1D1D1F; border-radius: 12px; padding: 0px 15px; font-weight: bold; border: none; }
            QComboBox:hover { background-color: #E8E8ED; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView { background-color: #FFFFFF; border: 1px solid rgba(0,0,0,0.1); selection-background-color: #F2F2F7; selection-color: #0071E3; outline: none; }
            QComboBox QAbstractItemView::item { min-height: 35px; padding: 0px 10px; }
            QScrollArea { border: none; background-color: transparent; }
            QLabel { color: #1D1D1F; } 
            QLineEdit { background-color: #E8E8ED; color: #1D1D1F; border-radius: 12px; padding: 10px; border: none; }
            #ReviewBox { background-color: #F2F2F7; border-radius: 12px; padding: 15px; }
            #SeparatorLine { background-color: rgba(0,0,0,0.08); border: none; }
            #SearchPopup { background-color: white; border: 1px solid rgba(0,0,0,0.1); padding: 5px; outline: none; }
            #SearchPopup::item { padding: 8px 12px; border-radius: 8px; font-size: 14px; color: #1D1D1F; }
            #SearchPopup::item:hover { background-color: #F2F2F7; }
            #SearchPopup::item:disabled { background-color: transparent; color: #8E8E93; font-weight: bold; font-size: 12px; padding-top: 15px; }
            #CancelBtn { background-color: #FFE5E5; color: #FF3B30; border-radius: 16px; padding: 0px 20px; font-weight: bold;}
            #CancelBtn:hover { background-color: #FFCCCC; }
            #LoadMoreBtn { background-color: #E8E8ED; color: #1D1D1F; border-radius: 18px; font-weight: bold; font-size: 14px; padding: 12px; }
            #LoadMoreBtn:hover { background-color: #D1D1D6; }
        """
        
        self.dark_style = """
            QMainWindow, #CentralWidget, #MainBg { background-color: #000000; }
            #Header { background-color: #1D1D1F; border-bottom: 1px solid rgba(255,255,255,0.05); }
            #AppCard, #ListContainer { background-color: #1C1C1E; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); }
            #HomeCard { background-color: #1C1C1E; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); }
            #HomeCard:hover { background-color: #2C2C2E; }
            .ActionBtn { font-weight: bold; font-size: 14px; border-radius: 16px; padding: 0px 20px; border: none; }
            #InstallBtn { background-color: #0A84FF; color: white; }
            #UninstallBtn { background-color: #2C2C2E; color: #FF453A; }
            #BackBtn { background-color: transparent; color: #0A84FF; font-weight: bold; font-size: 14px; text-align: left; border: none; }
            #BackBtn:hover { text-decoration: underline; }
            #LogoBtn { background-color: transparent; color: #FFFFFF; font-size: 20px; font-weight: bold; text-align: left; border: none; padding: 6px 12px; border-radius: 12px;}
            #LogoBtn:hover { background-color: #2C2C2E; }
            #LogoBtn[active="true"] { background-color: #1A2A40; color: #0A84FF; }
            #HeaderActionBtn { background-color: transparent; color: #0A84FF; font-size: 14px; font-weight: bold; border: none; padding: 8px 15px; border-radius: 12px; }
            #HeaderActionBtn:hover { background-color: #2C2C2E; }
            #HeaderActionBtn[active="true"] { background-color: #1A2A40; color: #0A84FF; }
            #IconBtn { background-color: transparent; border: none; border-radius: 12px; }
            #IconBtn:hover { background-color: #2C2C2E; }
            #IconBtn[active="true"] { background-color: #1A2A40; }
            #CategoryTitleBtn { text-align: left; font-size: 22px; font-weight: bold; background: transparent; border: none; padding: 5px 0px; margin: 0; color: #FFFFFF; }
            #CategoryTitleBtn:hover { color: #0A84FF; }
            #ListItem { background-color: #1C1C1E; border-radius: 12px; border: none; border-bottom: 1px solid rgba(255,255,255,0.05); }
            #ListItem:hover { background-color: #2C2C2E; }
            QComboBox { background-color: #2C2C2E; color: #FFFFFF; border-radius: 12px; padding: 0px 15px; font-weight: bold; border: none; }
            QComboBox:hover { background-color: #3A3A3C; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView { background-color: #1C1C1E; border: 1px solid rgba(255,255,255,0.1); selection-background-color: #2C2C2E; selection-color: #0A84FF; outline: none; }
            QComboBox QAbstractItemView::item { min-height: 35px; padding: 0px 10px; }
            QScrollArea { border: none; background-color: transparent; }
            QLabel { color: #FFFFFF; }
            QLineEdit { background-color: #2C2C2E; color: white; border-radius: 12px; padding: 10px; border: none; }
            #ReviewBox { background-color: #2C2C2E; border-radius: 12px; padding: 15px; }
            #SeparatorLine { background-color: rgba(255,255,255,0.15); border: none; }
            #SearchPopup { background-color: #1C1C1E; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); padding: 5px; outline: none; }
            #SearchPopup::item { padding: 8px 12px; border-radius: 8px; font-size: 14px; color: #FFFFFF; }
            #SearchPopup::item:hover { background-color: #2C2C2E; }
            #SearchPopup::item:disabled { background-color: transparent; color: #8E8E93; font-weight: bold; font-size: 12px; padding-top: 15px; }
            #CancelBtn { background-color: #3A1A1A; color: #FF453A; border-radius: 16px; padding: 0px 20px; font-weight: bold;}
            #CancelBtn:hover { background-color: #4A1A1A; }
            #LoadMoreBtn { background-color: #2C2C2E; color: #FFFFFF; border-radius: 18px; font-weight: bold; font-size: 14px; padding: 12px; }
            #LoadMoreBtn:hover { background-color: #3A3A3C; }
        """
        
        self.init_ui()
        self.apply_theme()
        
        apps_to_load = [app[0] for apps in HOME_CATEGORIES.values() for app in apps[:4] if not get_local_icon(app[0], 60)]
        self.request_icons(apps_to_load)
        self.update_all_texts() 
        
        self.check_dependencies()

    def check_dependencies(self):
        if not shutil.which("yay") and not shutil.which("paru"):
            self.header_frame.hide()
            self.stacked.setCurrentIndex(5)
            self.aur_installer = AurInstallerWorker()
            self.aur_installer.finished.connect(self.on_aur_installed)
            self.aur_installer.run()
        else:
            self.finish_startup()

    def on_aur_installed(self, success, msg):
        if success:
            self.app_settings["aur"] = 0
            self.save_settings()
        self.finish_startup()

    def finish_startup(self):
        self.header_frame.show()
        self.navigate_to(0)
        if self.app_settings.get("updates", 0) == 0:
            self.startup_check_worker = CheckUpdateWorker()
            self.startup_check_worker.sys_result.connect(self.on_startup_update_checked)
            self.startup_check_worker.check_sys()

    def tr(self, text_key):
        lang_idx = self.app_settings.get("lang", 1)
        return TRANSLATIONS.get(text_key, {}).get(lang_idx, TRANSLATIONS.get(text_key, {}).get(0, text_key))

    def update_all_texts(self):
        self.search_bar.setPlaceholderText(self.tr("search_placeholder"))
        self.installed_btn.setText(f" {self.tr('installed_btn')}")
        
        self.home_title_lbl.setText(self.tr("discover_title"))
        for cat_key, btn in self.cat_buttons.items():
            btn.setText(f"{self.tr(cat_key)}  >")
            
        for app_name, card in self.home_cards_refs.items():
            card.update_lang(self.app_settings.get("lang", 1))
            
        self.list_back_btn.setText(f" {self.tr('back_btn')}")
        self.back_btn.setText(f" {self.tr('back_btn')}")
        self.reviews_label.setText(self.tr("comm_info"))
        self.cancel_install_btn.setText(self.tr("cancel_btn"))
        
        if self.install_btn.text() in ["Obtener", "Get"]: self.install_btn.setText(self.tr("get_btn"))
        if self.install_btn.text() in ["Desinstalar", "Uninstall"]: self.install_btn.setText(self.tr("uninstall_btn"))
        self.open_btn.setText(self.tr("open_btn"))
        if self.check_app_btn.text() in ["Buscar actualización", "Check for update"]: self.check_app_btn.setText(self.tr("check_up_btn"))
        if self.check_app_btn.text() in ["Actualizado", "Up to date"]: self.check_app_btn.setText(self.tr("app_updated"))
        
        self.inst_back_btn.setText(f" {self.tr('back_btn')}")
        
        if hasattr(self, 'all_installed_results'):
            self.inst_title.setText(f"{self.tr('inst_title')} ({len(self.all_installed_results)})")
        else:
            self.inst_title.setText(self.tr("inst_title"))
            
        self.clean_sys_btn.setText(self.tr("clean_sys"))
        if self.check_sys_btn.text() in ["Buscar Actualizaciones", "Check for Updates"]: self.check_sys_btn.setText(self.tr("check_sys"))
        if self.check_sys_btn.text() in ["Sistema actualizado", "System up to date"]: self.check_sys_btn.setText(self.tr("sys_updated"))
        if self.update_sys_btn.text() in ["Instalar Actualizaciones", "Install Updates"]: self.update_sys_btn.setText(self.tr("inst_sys"))
        self.inst_search_bar.setPlaceholderText(self.tr("filter_inst"))
        
        self.set_back_btn.setText(f" {self.tr('back_btn')}")
        self.settings_title.setText(self.tr("settings_title"))
        self.reset_btn.setText(self.tr("reset_btn"))
        
        for lbl, title_key, desc_key in self.settings_labels:
            lbl[0].setText(self.tr(title_key))
            lbl[1].setText(self.tr(desc_key))
            
        self.refresh_combo_box(self.theme_cb, ["opt_auto", "opt_light", "opt_dark"])
        self.refresh_combo_box(self.clean_cb, ["opt_clean_auto", "opt_clean_man"])
        self.refresh_combo_box(self.up_cb, ["opt_up_start", "opt_up_no"])
        self.setup_lbl.setText(self.tr("installing_yay"))

    def refresh_combo_box(self, cb, translation_keys):
        cb.blockSignals(True)
        idx = max(0, cb.currentIndex())
        cb.clear()
        cb.addItems([self.tr(k) for k in translation_keys])
        cb.setCurrentIndex(idx)
        cb.blockSignals(False)

    def create_dynamic_setting_row(self, layout, title_key, desc_key, widget):
        row_widget = QWidget()
        row_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 5, 0, 5)
        
        text_ly = QVBoxLayout()
        t_lbl = QLabel(self.tr(title_key))
        t_lbl.setFont(QFont("SF Pro Text", 15, QFont.Bold))
        t_lbl.setWordWrap(True)
        
        d_lbl = QLabel(self.tr(desc_key))
        d_lbl.setStyleSheet("color: #8E8E93; font-size: 12px;")
        d_lbl.setWordWrap(True)
        
        text_ly.addWidget(t_lbl)
        text_ly.addWidget(d_lbl)
        
        row.addLayout(text_ly, 1) 
        row.addSpacing(15)
        row.addWidget(widget, 0, Qt.AlignVCenter)
        
        layout.addWidget(row_widget)
        sep = QFrame(); sep.setObjectName("SeparatorLine"); sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        self.settings_labels.append(( (t_lbl, d_lbl), title_key, desc_key ))
        return t_lbl, d_lbl

    def live_update_settings_language(self, index):
        self.update_setting("lang", index)
        self.update_all_texts()

    def navigate_to(self, index):
        if self.stacked.currentIndex() != index:
            self.last_view = self.stacked.currentIndex()
            self.stacked.set_current_index_animated(index)

    def update_nav_state(self, index):
        self.logo_btn.setProperty("active", index == 0)
        self.installed_btn.setProperty("active", index == 3)
        self.settings_btn.setProperty("active", index == 4)
        
        for btn in [self.logo_btn, self.installed_btn, self.settings_btn]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def load_settings(self):
        config_dir = os.path.expanduser("~/.config/rubiaur")
        os.makedirs(config_dir, exist_ok=True)
        self.settings_file = os.path.join(config_dir, "settings.json")
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.app_settings.update(json.load(f))
            except Exception: pass

    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_settings, f)
        except Exception: pass

    def update_setting(self, key, index):
        self.app_settings[key] = index
        self.save_settings()
        if key == "theme":
            self.apply_theme()

    def reset_settings(self):
        reply = QMessageBox.question(self, self.tr("settings_title"), self.tr("reset_btn") + "?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.lang_cb.blockSignals(True)
            self.aur_cb.blockSignals(True)
            self.clean_cb.blockSignals(True)
            self.up_cb.blockSignals(True)
            self.theme_cb.blockSignals(True)
            
            self.lang_cb.setCurrentIndex(1)
            self.aur_cb.setCurrentIndex(0)
            self.clean_cb.setCurrentIndex(0)
            self.up_cb.setCurrentIndex(0)
            self.theme_cb.setCurrentIndex(0)
            
            self.lang_cb.blockSignals(False)
            self.aur_cb.blockSignals(False)
            self.clean_cb.blockSignals(False)
            self.up_cb.blockSignals(False)
            self.theme_cb.blockSignals(False)
            
            self.app_settings = {"lang": 1, "aur": 0, "cache": 0, "updates": 0, "theme": 0}
            self.save_settings()
            self.apply_theme()
            self.update_all_texts()
            
            self.toast = ToastNotification(self.centralWidget(), "Success", "Defaults applied.", self.is_dark)
            self.toast.show_anim()

    def on_startup_update_checked(self, count):
        if count > 0:
            self.toast = ToastNotification(self.centralWidget(), "Updates Available" if self.app_settings.get("lang", 1) == 1 else "Actualizaciones Disponibles", f"You have {count} pending system updates." if self.app_settings.get("lang", 1) == 1 else f"Tienes {count} actualizaciones pendientes en el sistema.", self.is_dark)
            self.toast.show_anim()

    def load_history(self):
        config_dir = os.path.expanduser("~/.config/rubiaur")
        if not os.path.exists(config_dir):
            try: os.makedirs(config_dir)
            except: pass
        self.history_file = os.path.join(config_dir, "history.json")
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.search_history = json.load(f)
            except Exception:
                self.search_history = []

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f)
        except Exception: pass

    def request_icons(self, apps_list):
        to_download = []
        for app in apps_list:
            if app in self.icon_cache:
                self.apply_icon(app, self.icon_cache[app])
            else:
                to_download.append(app)
        if to_download:
            self.icon_worker.load_icons(to_download)

    def init_ui(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0,0,0,0)

        self.header_frame = QFrame()
        self.header_frame.setObjectName("Header")
        self.header_frame.setFixedHeight(80)
        h_layout = QHBoxLayout(self.header_frame)
        h_layout.setContentsMargins(30, 0, 30, 0)
        
        left_ly = QHBoxLayout()
        left_ly.setContentsMargins(0,0,0,0)
        self.logo_btn = QPushButton(" RubiAUR")
        self.logo_btn.setIcon(QIcon(get_resource_path("logo.svg")))
        self.logo_btn.setIconSize(QSize(32, 32))
        self.logo_btn.setObjectName("LogoBtn")
        self.logo_btn.setCursor(Qt.PointingHandCursor)
        self.logo_btn.clicked.connect(lambda: self.navigate_to(0))
        left_ly.addWidget(self.logo_btn)
        left_ly.addStretch()

        center_ly = QHBoxLayout()
        center_ly.setContentsMargins(0,0,0,0)
        center_ly.setAlignment(Qt.AlignCenter)
        
        self.search_bar = SearchLineEdit()
        self.search_bar.setFixedWidth(400)
        self.search_bar.setFixedHeight(38)
        self.search_bar.returnPressed.connect(self.start_search)
        self.search_bar.clicked.connect(self.handle_search_interaction)
        self.search_bar.textChanged.connect(self.handle_search_interaction)
        center_ly.addWidget(self.search_bar)

        right_ly = QHBoxLayout()
        right_ly.setContentsMargins(0,0,0,0)
        right_ly.addStretch()
        self.installed_btn = QPushButton()
        self.installed_btn.setIconSize(QSize(20, 20))
        self.installed_btn.setObjectName("HeaderActionBtn")
        self.installed_btn.setCursor(Qt.PointingHandCursor)
        self.installed_btn.clicked.connect(self.open_installed)
        
        self.settings_btn = QPushButton()
        self.settings_btn.setIconSize(QSize(22, 22))
        self.settings_btn.setObjectName("IconBtn")
        self.settings_btn.setFixedSize(38, 38)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_settings)
        
        right_ly.addWidget(self.installed_btn)
        right_ly.addWidget(self.settings_btn)

        h_layout.addLayout(left_ly, 1)
        h_layout.addLayout(center_ly, 1)
        h_layout.addLayout(right_ly, 1)
        layout.addWidget(self.header_frame)

        self.search_popup = QListWidget(self.centralWidget())
        self.search_popup.setObjectName("SearchPopup")
        self.search_popup.setIconSize(QSize(24, 24))
        self.search_popup.hide()
        self.search_popup.itemClicked.connect(self.on_popup_item_clicked)

        self.stacked = FadeStackedWidget()
        self.stacked.currentChanged.connect(self.update_nav_state)
        
        # --- PANTALLA 0: INICIO ---
        self.page_home = QWidget(); self.page_home.setObjectName("MainBg")
        home_layout = QVBoxLayout(self.page_home)
        home_layout.setContentsMargins(0,0,0,0)
        home_scroll = QScrollArea()
        home_scroll.setWidgetResizable(True)
        home_content = QWidget(); home_content.setObjectName("MainBg")
        hc_layout = QVBoxLayout(home_content)
        hc_layout.setContentsMargins(50, 40, 50, 40)
        
        self.home_title_lbl = QLabel()
        self.home_title_lbl.setFont(QFont("SF Pro Display", 32, QFont.Bold))
        hc_layout.addWidget(self.home_title_lbl)
        hc_layout.addSpacing(20)
        
        for cat_name, apps in HOME_CATEGORIES.items():
            cat_key = f"cat_{cat_name}"
            cat_btn = QPushButton()
            cat_btn.setObjectName("CategoryTitleBtn")
            cat_btn.setCursor(Qt.PointingHandCursor)
            cat_btn.clicked.connect(lambda checked, c=cat_name: self.open_category(c))
            hc_layout.addWidget(cat_btn)
            self.cat_buttons[cat_key] = cat_btn
            
            grid = QGridLayout()
            grid.setSpacing(15)
            row, col = 0, 0
            
            for app_name, desc_dict in apps[:4]:
                card = HomeAppCard(app_name, desc_dict, self.app_settings.get("lang", 1))
                card.clicked.connect(self.quick_search)
                self.home_cards_refs[app_name] = card
                grid.addWidget(card, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1
            hc_layout.addLayout(grid)
            hc_layout.addSpacing(40)
            
        hc_layout.addStretch()
        home_scroll.setWidget(home_content)
        home_layout.addWidget(home_scroll)
        self.stacked.addWidget(self.page_home)

        # --- PANTALLA 1: RESULTADOS ---
        self.page_list = QWidget(); self.page_list.setObjectName("MainBg")
        list_page_layout = QVBoxLayout(self.page_list)
        list_page_layout.setContentsMargins(50, 10, 50, 40)
        
        self.list_back_btn = QPushButton()
        self.list_back_btn.setIconSize(QSize(18, 18))
        self.list_back_btn.setObjectName("BackBtn")
        self.list_back_btn.setCursor(Qt.PointingHandCursor)
        self.list_back_btn.clicked.connect(self.go_home_from_list)
        list_page_layout.addWidget(self.list_back_btn)

        status_lay = QHBoxLayout()
        self.status_lbl = QLabel("")
        self.status_lbl.setFont(QFont("SF Pro Text", 18, QFont.Bold))
        self.list_spinner = LoadingSpinner(size=24)
        self.list_spinner.hide()
        status_lay.addWidget(self.status_lbl)
        status_lay.addWidget(self.list_spinner)
        status_lay.addStretch()
        list_page_layout.addLayout(status_lay)
        
        list_page_layout.addSpacing(10)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.list_container = QFrame()
        self.list_container.setObjectName("ListContainer")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.list_container)
        list_page_layout.addWidget(self.scroll_area)
        self.stacked.addWidget(self.page_list)

        # --- PANTALLA 2: DETALLES ---
        self.page_detail = QWidget(); self.page_detail.setObjectName("MainBg")
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail_content = QWidget(); detail_content.setObjectName("MainBg")
        detail_layout = QVBoxLayout(detail_content)
        detail_layout.setContentsMargins(50, 10, 50, 40)
        
        self.back_btn = QPushButton()
        self.back_btn.setIconSize(QSize(18, 18))
        self.back_btn.setObjectName("BackBtn")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.go_back)
        detail_layout.addWidget(self.back_btn)

        self.card = QFrame(); self.card.setObjectName("AppCard")
        self.card_lay = QVBoxLayout(self.card)
        self.card_lay.setContentsMargins(40,40,40,40)
        
        top_row = QHBoxLayout()
        self.icon_lab = QLabel()
        self.icon_lab.setFixedSize(120, 120)
        
        v_info = QVBoxLayout()
        
        name_lay = QHBoxLayout()
        self.name_lab = QLabel("")
        self.name_lab.setFont(QFont("SF Pro Display", 32, QFont.Bold))
        self.detail_spinner = LoadingSpinner(size=28)
        self.detail_spinner.hide()
        name_lay.addWidget(self.name_lab)
        name_lay.addWidget(self.detail_spinner)
        name_lay.addStretch()
        
        self.size_lab = QLabel("")
        self.size_lab.setStyleSheet("color: #8E8E93; font-size: 14px;")
        
        self.stars_lab = QLabel("")
        self.stars_lab.setStyleSheet("color: #8E8E93; font-size: 14px; font-weight: bold;")
        
        v_info.addLayout(name_lay)
        v_info.addWidget(self.stars_lab)
        v_info.addWidget(self.size_lab)
        v_info.addStretch()
        
        top_row.addWidget(self.icon_lab)
        top_row.addSpacing(30)
        top_row.addLayout(v_info)
        top_row.addStretch()

        self.btn_row_container = QWidget()
        btn_row = QHBoxLayout(self.btn_row_container)
        btn_row.setContentsMargins(0,0,0,0)
        btn_row.setSpacing(12)
        btn_row.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.install_btn = QPushButton()
        self.install_btn.setProperty("class", "ActionBtn")
        self.install_btn.setObjectName("InstallBtn")
        self.install_btn.setFixedHeight(36)
        self.install_btn.setCursor(Qt.PointingHandCursor)
        self.install_btn.clicked.connect(self.install_app)

        self.check_app_btn = QPushButton()
        self.check_app_btn.setProperty("class", "ActionBtn")
        self.check_app_btn.setStyleSheet("background-color: #F2F2F7; color: #0071E3;")
        self.check_app_btn.setFixedHeight(36)
        self.check_app_btn.setCursor(Qt.PointingHandCursor)
        self.check_app_btn.clicked.connect(self.run_check_app)
        self.check_app_btn.hide()

        self.update_app_btn = QPushButton()
        self.update_app_btn.setProperty("class", "ActionBtn")
        self.update_app_btn.setStyleSheet("background-color: #0071E3; color: white;")
        self.update_app_btn.setFixedHeight(36)
        self.update_app_btn.setCursor(Qt.PointingHandCursor)
        self.update_app_btn.clicked.connect(self.run_update_app)
        self.update_app_btn.hide()

        self.open_btn = QPushButton()
        self.open_btn.setProperty("class", "ActionBtn")
        self.open_btn.setStyleSheet("background-color: #0071E3; color: white;")
        self.open_btn.setFixedHeight(36)
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.clicked.connect(self.launch_app)
        self.open_btn.hide()

        self.source_selector = QComboBox()
        self.source_selector.setItemDelegate(QStyledItemDelegate())
        self.source_selector.setFixedHeight(36)
        
        btn_row.addWidget(self.install_btn)
        btn_row.addWidget(self.check_app_btn)
        btn_row.addWidget(self.update_app_btn)
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(self.source_selector)

        self.progress_container = QWidget()
        self.progress_container.hide()
        prog_lay = QHBoxLayout(self.progress_container)
        prog_lay.setContentsMargins(0,0,0,0)
        prog_lay.setSpacing(15)
        prog_lay.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.pacman_anim = PacmanProgress()
        self.pacman_anim.hide()
        
        self.install_status_lbl = QLabel()
        self.install_status_lbl.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        
        self.cancel_install_btn = QPushButton()
        self.cancel_install_btn.setObjectName("CancelBtn")
        self.cancel_install_btn.setFixedHeight(36)
        self.cancel_install_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_install_btn.clicked.connect(self.cancel_installation)

        prog_lay.addWidget(self.pacman_anim)
        prog_lay.addWidget(self.install_status_lbl)
        prog_lay.addWidget(self.cancel_install_btn)
        
        self.desc_lab = QLabel("")
        self.desc_lab.setWordWrap(True)
        self.desc_lab.setFont(QFont("SF Pro Text", 14))

        self.reviews_label = QLabel()
        self.reviews_label.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        self.comments_container = QVBoxLayout()
        self.comments_container.setSpacing(10)
        
        self.card_lay.addLayout(top_row)
        self.card_lay.addSpacing(30)
        self.card_lay.addWidget(self.btn_row_container)
        self.card_lay.addWidget(self.progress_container) 
        self.card_lay.addSpacing(30)
        
        self.separator_line = QFrame()
        self.separator_line.setObjectName("SeparatorLine")
        self.separator_line.setFixedHeight(1)
        self.card_lay.addWidget(self.separator_line)
        self.card_lay.addSpacing(20)
        
        self.card_lay.addWidget(self.desc_lab)
        self.card_lay.addSpacing(40)
        self.card_lay.addWidget(self.reviews_label)
        self.card_lay.addSpacing(10)
        self.card_lay.addLayout(self.comments_container)
        self.card_lay.addStretch()

        detail_layout.addWidget(self.card)
        detail_scroll.setWidget(detail_content)
        
        page_detail_lay = QVBoxLayout(self.page_detail)
        page_detail_lay.setContentsMargins(0,0,0,0)
        page_detail_lay.addWidget(detail_scroll)
        self.stacked.addWidget(self.page_detail)

        # --- PANTALLA 3: INSTALADAS ---
        self.page_inst = QWidget(); self.page_inst.setObjectName("MainBg")
        inst_page_layout = QVBoxLayout(self.page_inst)
        inst_page_layout.setContentsMargins(50, 10, 50, 40)
        
        self.inst_back_btn = QPushButton()
        self.inst_back_btn.setIconSize(QSize(18, 18))
        self.inst_back_btn.setObjectName("BackBtn")
        self.inst_back_btn.setCursor(Qt.PointingHandCursor)
        self.inst_back_btn.clicked.connect(lambda: self.navigate_to(0))
        inst_page_layout.addWidget(self.inst_back_btn)

        inst_header_lay = QHBoxLayout()
        
        inst_title_lay = QHBoxLayout()
        self.inst_title = QLabel()
        self.inst_title.setFont(QFont("SF Pro Display", 32, QFont.Bold))
        self.inst_spinner = LoadingSpinner(size=28)
        self.inst_spinner.hide()
        inst_title_lay.addWidget(self.inst_title)
        inst_title_lay.addWidget(self.inst_spinner)
        
        self.clean_sys_btn = QPushButton()
        self.clean_sys_btn.setStyleSheet("background-color: #F2F2F7; color: #1D1D1F; border-radius: 14px; font-weight: bold; font-size: 13px; padding: 8px 20px; border: none;")
        self.clean_sys_btn.setCursor(Qt.PointingHandCursor)
        self.clean_sys_btn.clicked.connect(self.run_system_clean)

        self.check_sys_btn = QPushButton()
        self.check_sys_btn.setStyleSheet("background-color: #F2F2F7; color: #0071E3; border-radius: 14px; font-weight: bold; font-size: 13px; padding: 8px 20px; border: none;")
        self.check_sys_btn.setCursor(Qt.PointingHandCursor)
        self.check_sys_btn.clicked.connect(self.run_check_sys)
        
        self.update_sys_btn = QPushButton()
        self.update_sys_btn.setStyleSheet("background-color: #0071E3; color: white; border-radius: 14px; font-weight: bold; font-size: 13px; padding: 8px 20px; border: none;")
        self.update_sys_btn.setCursor(Qt.PointingHandCursor)
        self.update_sys_btn.clicked.connect(self.run_system_update)
        self.update_sys_btn.hide()

        inst_header_lay.addLayout(inst_title_lay)
        inst_header_lay.addStretch()
        inst_header_lay.addWidget(self.clean_sys_btn)
        inst_header_lay.addSpacing(10)
        inst_header_lay.addWidget(self.check_sys_btn)
        inst_header_lay.addSpacing(10)
        inst_header_lay.addWidget(self.update_sys_btn)
        
        inst_page_layout.addLayout(inst_header_lay)
        inst_page_layout.addSpacing(10)
        
        self.inst_search_bar = QLineEdit()
        self.inst_search_bar.setFixedHeight(38)
        self.inst_search_bar.textChanged.connect(self.filter_installed)
        inst_page_layout.addWidget(self.inst_search_bar)
        inst_page_layout.addSpacing(10)
        
        self.inst_scroll = QScrollArea()
        self.inst_scroll.setWidgetResizable(True)
        self.inst_container = QFrame()
        self.inst_container.setObjectName("ListContainer")
        self.inst_layout = QVBoxLayout(self.inst_container)
        self.inst_layout.setAlignment(Qt.AlignTop)
        self.inst_scroll.setWidget(self.inst_container)
        inst_page_layout.addWidget(self.inst_scroll)
        self.stacked.addWidget(self.page_inst)

        # --- PANTALLA 4: CONFIGURACIÓN ---
        self.page_settings = QWidget(); self.page_settings.setObjectName("MainBg")
        settings_page_layout = QVBoxLayout(self.page_settings)
        settings_page_layout.setContentsMargins(50, 10, 50, 40)
        
        self.set_back_btn = QPushButton()
        self.set_back_btn.setIconSize(QSize(18, 18))
        self.set_back_btn.setObjectName("BackBtn")
        self.set_back_btn.setCursor(Qt.PointingHandCursor)
        self.set_back_btn.clicked.connect(lambda: self.navigate_to(0))
        settings_page_layout.addWidget(self.set_back_btn)

        self.settings_title = QLabel()
        self.settings_title.setFont(QFont("SF Pro Display", 32, QFont.Bold))
        settings_page_layout.addWidget(self.settings_title)
        settings_page_layout.addSpacing(20)

        set_scroll = QScrollArea()
        set_scroll.setWidgetResizable(True)
        set_container = QFrame()
        set_container.setObjectName("ListContainer")
        set_lay = QVBoxLayout(set_container)
        set_lay.setContentsMargins(30, 30, 30, 30)
        set_lay.setSpacing(20)
        set_lay.setAlignment(Qt.AlignTop)

        self.lang_cb = QComboBox()
        self.lang_cb.setItemDelegate(QStyledItemDelegate())
        self.lang_cb.addItems(["Español", "English", "Français", "Deutsch"])
        self.lang_cb.setMinimumWidth(150)
        self.lang_cb.setMaximumWidth(220)
        self.lang_cb.setFixedHeight(36)
        self.lang_cb.setCurrentIndex(self.app_settings.get("lang", 1))
        self.lang_cb.currentIndexChanged.connect(self.live_update_settings_language)
        self.create_dynamic_setting_row(set_lay, "lang_lbl", "lang_desc", self.lang_cb)

        self.theme_cb = QComboBox()
        self.theme_cb.setItemDelegate(QStyledItemDelegate())
        self.theme_cb.setMinimumWidth(150)
        self.theme_cb.setMaximumWidth(220)
        self.theme_cb.setFixedHeight(36)
        self.theme_cb.currentIndexChanged.connect(lambda i: self.update_setting("theme", i))
        self.create_dynamic_setting_row(set_lay, "theme_lbl", "theme_desc", self.theme_cb)

        self.aur_cb = QComboBox()
        self.aur_cb.setItemDelegate(QStyledItemDelegate())
        self.aur_cb.addItems(["yay", "paru"])
        self.aur_cb.setMinimumWidth(150)
        self.aur_cb.setMaximumWidth(220)
        self.aur_cb.setFixedHeight(36)
        self.aur_cb.setCurrentIndex(self.app_settings.get("aur", 0))
        self.aur_cb.currentIndexChanged.connect(lambda i: self.update_setting("aur", i))
        self.create_dynamic_setting_row(set_lay, "aur_lbl", "aur_desc", self.aur_cb)

        self.clean_cb = QComboBox()
        self.clean_cb.setItemDelegate(QStyledItemDelegate())
        self.clean_cb.setMinimumWidth(150)
        self.clean_cb.setMaximumWidth(220)
        self.clean_cb.setFixedHeight(36)
        self.clean_cb.currentIndexChanged.connect(lambda i: self.update_setting("cache", i))
        self.create_dynamic_setting_row(set_lay, "cache_lbl", "cache_desc", self.clean_cb)

        self.up_cb = QComboBox()
        self.up_cb.setItemDelegate(QStyledItemDelegate())
        self.up_cb.setMinimumWidth(150)
        self.up_cb.setMaximumWidth(220)
        self.up_cb.setFixedHeight(36)
        self.up_cb.currentIndexChanged.connect(lambda i: self.update_setting("updates", i))
        self.create_dynamic_setting_row(set_lay, "up_lbl", "up_desc", self.up_cb)

        self.reset_btn = QPushButton()
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.setStyleSheet("background-color: transparent; color: #FF3B30; font-weight: bold; font-size: 14px; text-decoration: underline; border: none; padding: 10px;")
        self.reset_btn.clicked.connect(self.reset_settings)
        set_lay.addSpacing(10)
        set_lay.addWidget(self.reset_btn, alignment=Qt.AlignCenter)

        ver_row = QHBoxLayout()
        ver_lbl = QLabel("RubiAUR Versión 1.0.0 (Arch Linux)")
        ver_lbl.setStyleSheet("color: #8E8E93; font-size: 13px; font-weight: bold;")
        ver_row.addStretch()
        ver_row.addWidget(ver_lbl)
        ver_row.addStretch()
        set_lay.addSpacing(20)
        set_lay.addLayout(ver_row)

        set_scroll.setWidget(set_container)
        settings_page_layout.addWidget(set_scroll)
        self.stacked.addWidget(self.page_settings)

        # --- PANTALLA 5: INSTALANDO DEPENDENCIA (YAY) ---
        self.page_setup = QWidget(); self.page_setup.setObjectName("MainBg")
        setup_lay = QVBoxLayout(self.page_setup)
        setup_lay.setAlignment(Qt.AlignCenter)
        
        self.setup_spinner = LoadingSpinner(size=64)
        self.setup_spinner.start()
        
        self.setup_lbl = QLabel()
        self.setup_lbl.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        self.setup_lbl.setAlignment(Qt.AlignCenter)
        
        setup_lay.addWidget(self.setup_spinner, alignment=Qt.AlignCenter)
        setup_lay.addSpacing(20)
        setup_lay.addWidget(self.setup_lbl)
        
        self.stacked.addWidget(self.page_setup)
        layout.addWidget(self.stacked)

    def apply_theme(self):
        theme_val = self.app_settings.get("theme", 0)
        if theme_val == 0:
            self.is_dark = QApplication.palette().color(QPalette.Window).lightness() < 128
        else:
            self.is_dark = (theme_val == 2)
            
        self.setStyleSheet(self.dark_style if self.is_dark else self.light_style)

        if hasattr(self, 'logo_btn'): self.logo_btn.setIcon(QIcon(get_resource_path("logo.svg")))
        if hasattr(self, 'installed_btn'): self.installed_btn.setIcon(get_ui_icon("installed", self.is_dark))
        if hasattr(self, 'settings_btn'): self.settings_btn.setIcon(get_ui_icon("settings", self.is_dark))
        if hasattr(self, 'list_back_btn'): self.list_back_btn.setIcon(get_ui_icon("back", self.is_dark))
        if hasattr(self, 'back_btn'): self.back_btn.setIcon(get_ui_icon("back", self.is_dark))
        if hasattr(self, 'inst_back_btn'): self.inst_back_btn.setIcon(get_ui_icon("back", self.is_dark))
        if hasattr(self, 'set_back_btn'): self.set_back_btn.setIcon(get_ui_icon("back", self.is_dark))
        
        if hasattr(self, 'list_spinner') and self.list_spinner: self.list_spinner.update_theme(self.is_dark)
        if hasattr(self, 'inst_spinner') and self.inst_spinner: self.inst_spinner.update_theme(self.is_dark)
        if hasattr(self, 'detail_spinner') and self.detail_spinner: self.detail_spinner.update_theme(self.is_dark)
        if hasattr(self, 'pacman_anim') and self.pacman_anim: self.pacman_anim.update_theme(self.is_dark)
        if hasattr(self, 'setup_spinner') and self.setup_spinner: self.setup_spinner.update_theme(self.is_dark)
        
        if hasattr(self, 'inst_bottom_spinner') and self.inst_bottom_spinner:
            self.inst_bottom_spinner.update_theme(self.is_dark)
        if hasattr(self, 'cat_bottom_spinner') and self.cat_bottom_spinner:
            self.cat_bottom_spinner.update_theme(self.is_dark)
            
        if hasattr(self, 'cat_load_more_btn') and self.cat_load_more_btn:
            self.cat_load_more_btn.setIcon(get_ui_icon("down_arrow", self.is_dark))
        if hasattr(self, 'inst_load_more_btn') and self.inst_load_more_btn:
            self.inst_load_more_btn.setIcon(get_ui_icon("down_arrow", self.is_dark))

    def mousePressEvent(self, event):
        if hasattr(self, 'search_popup') and self.search_popup.isVisible():
            popup_rect = self.search_popup.geometry()
            if not popup_rect.contains(event.position().toPoint()):
                self.search_popup.hide()
                self.search_bar.clearFocus()
        super().mousePressEvent(event)

    def handle_search_interaction(self):
        query = self.search_bar.text().strip()
        if not query:
            self.show_default_popup()
        else:
            self.autocomplete_worker.search(query)

    def show_default_popup(self):
        self.search_popup.clear()
        
        if self.search_history:
            hist_title = QListWidgetItem(self.tr("recent_visits"))
            hist_title.setFlags(Qt.NoItemFlags) 
            self.search_popup.addItem(hist_title)
            
            for app_name in reversed(self.search_history[-5:]):
                item = QListWidgetItem("  " + app_name)
                item.setData(Qt.UserRole, app_name)
                pix = get_local_icon(app_name, 24)
                if pix: 
                    item.setIcon(QIcon(pix))
                else:
                    item.setIcon(get_ui_icon("history", self.is_dark))
                self.search_popup.addItem(item)
                
        rec_title = QListWidgetItem(self.tr("suggestions"))
        rec_title.setFlags(Qt.NoItemFlags)
        self.search_popup.addItem(rec_title)
        
        pool_sugerencias = [
            "docker", "visual-studio-code-bin", "steam", "htop", 
            "minecraft-launcher", "pycharm-community-edition", "vlc", 
            "arduino-ide", "discord", "obsidian", "btop", 
            "intellij-idea-community-edition", "lutris", "wireshark-qt",
            "spotify", "gimp", "alacritty"
        ]
        
        recomendaciones = random.sample(pool_sugerencias, 5)
        
        for r in recomendaciones:
            if r not in self.search_history: 
                item = QListWidgetItem("  " + r)
                item.setData(Qt.UserRole, r)
                pix = get_local_icon(r, 24)
                if pix: 
                    item.setIcon(QIcon(pix))
                else:
                    item.setIcon(get_ui_icon("star", self.is_dark))
                self.search_popup.addItem(item)
        
        self.adjust_popup_size()

    def show_autocomplete_results(self, results, query):
        if self.search_bar.text().strip() != query: 
            return
            
        if not self.search_bar.hasFocus():
            return
            
        self.search_popup.clear()
        if not results:
            self.search_popup.hide()
            return
            
        for pkg_data in results:
            pkg_name = pkg_data["name"]
            
            item = QListWidgetItem()
            item.setData(Qt.UserRole, pkg_name)
            item.setSizeHint(QSize(0, 44))
            self.search_popup.addItem(item)
            
            row_widget = QWidget()
            row_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            row_widget.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(10, 0, 10, 0)
            row_layout.setSpacing(10)
            
            pix = get_local_icon(pkg_name, 24)
            ico_lbl = QLabel()
            if pix:
                ico_lbl.setPixmap(pix)
            else:
                ico_lbl.setFixedSize(24, 24)
                
            name_lbl = QLabel(pkg_name)
            name_color = "#FFFFFF" if self.is_dark else "#1D1D1F"
            name_lbl.setStyleSheet(f"color: {name_color}; font-size: 14px; font-weight: 500;")
            
            row_layout.addWidget(ico_lbl)
            row_layout.addWidget(name_lbl)
            row_layout.addStretch()
            
            if pkg_data.get('has_pacman'):
                tag_pacman = QFrame()
                tag_pacman.setStyleSheet("background-color: #1D1D1F; padding: 2px 6px; border-radius: 6px;")
                p_lay = QHBoxLayout(tag_pacman); p_lay.setContentsMargins(0,0,0,0); p_lay.setSpacing(4)
                ico_p = QLabel(); ico_p.setPixmap(QIcon(get_resource_path("pacman.svg")).pixmap(12, 12)) 
                lbl_p = QLabel("Pacman")
                lbl_p.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 10px; border: none; background: transparent;")
                p_lay.addWidget(ico_p); p_lay.addWidget(lbl_p)
                row_layout.addWidget(tag_pacman)

            if pkg_data.get('has_aur'):
                tag_aur = QFrame()
                tag_aur.setStyleSheet("background-color: #0071E3; padding: 2px 6px; border-radius: 6px;")
                a_lay = QHBoxLayout(tag_aur); a_lay.setContentsMargins(0,0,0,0); a_lay.setSpacing(4)
                ico_a = QLabel(); ico_a.setPixmap(QIcon(get_resource_path("aur.svg")).pixmap(12, 12)) 
                lbl_a = QLabel("AUR")
                lbl_a.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 10px; border: none; background: transparent;")
                a_lay.addWidget(ico_a); a_lay.addWidget(lbl_a)
                row_layout.addWidget(tag_aur)
                
            self.search_popup.setItemWidget(item, row_widget)
            
        self.adjust_popup_size()

    def adjust_popup_size(self):
        pos = self.search_bar.mapTo(self.centralWidget(), QPoint(0, self.search_bar.height()))
        total_items = self.search_popup.count()
        height = min(total_items * 44 + 10, 350) 
        
        self.search_popup.setGeometry(pos.x(), pos.y() + 5, self.search_bar.width(), height)
        self.search_popup.show()
        self.search_popup.raise_()

    def on_popup_item_clicked(self, item):
        if item.flags() == Qt.NoItemFlags:
            return
        texto = item.data(Qt.UserRole)
        if texto:
            self.search_popup.hide()
            self.search_bar.setText(texto)
            self.start_search()

    def go_home_from_list(self):
        self.search_bar.clear()
        self.navigate_to(0)

    def go_back(self):
        self.navigate_to(self.last_view)

    def open_settings(self):
        self.navigate_to(4)
        self.search_popup.hide()
        self.search_bar.clearFocus()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None: widget.deleteLater()
                else: self.clear_layout(item.layout())

    def apply_icon(self, app_name, img_data):
        self.icon_cache[app_name] = img_data
        image = QImage.fromData(img_data)
        pixmap = QPixmap.fromImage(image)
        
        if app_name in self.home_cards_refs:
            self.home_cards_refs[app_name].set_icon(create_rounded_pixmap(pixmap, 60, 12))

        if hasattr(self, 'list_items_refs') and app_name in self.list_items_refs:
            self.list_items_refs[app_name].set_icon(create_rounded_pixmap(pixmap, 50, 12))
            
        if hasattr(self, 'current_app_data') and self.current_app_data.get('name') == app_name:
            self.icon_lab.setStyleSheet("background-color: transparent;")
            self.icon_lab.setPixmap(create_rounded_pixmap(pixmap, 120, 25))

    def set_placeholder_icon(self, letter):
        app_name = self.current_app_data.get('name', 'a')
        
        local_pix = get_local_icon(app_name, 120)
        if local_pix:
            self.icon_lab.setStyleSheet("background-color: transparent;")
            self.icon_lab.setPixmap(create_rounded_pixmap(local_pix, 120, 25))
            return

        canvas = QPixmap(120, 120)
        canvas.fill(Qt.transparent)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, 120, 120, 25, 25)
        painter.fillPath(path, Qt.blue if not self.is_dark else Qt.darkBlue)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 40, QFont.Bold))
        painter.drawText(canvas.rect(), Qt.AlignCenter, letter.upper())
        painter.end()
        self.icon_lab.setPixmap(canvas)

    def open_installed(self):
        self.navigate_to(3)
        self.search_bar.clear()
        self.inst_search_bar.clear()
        self.inst_title.setText(self.tr("analyzing"))
        self.inst_spinner.start()
        self.search_popup.hide()
        
        self.inst_load_more_container = None 
        self.clear_layout(self.inst_layout)
        
        self.check_sys_btn.setText(self.tr("check_sys"))
        self.check_sys_btn.setEnabled(True)
        self.check_sys_btn.show()
        self.update_sys_btn.hide()
        
        self.installed_worker.load()

    def populate_installed(self, results):
        self.inst_spinner.stop()
        self.inst_title.setText(f"{self.tr('inst_title')} ({len(results)})")
        self.all_installed_results = results 
        self.filtered_installed_results = results 
        self.current_inst_index = 0
        self.list_items_refs = {}
        
        self.inst_load_more_container = None
        self.clear_layout(self.inst_layout)
        self.load_more_installed_apps()

    def filter_installed(self, text):
        text = text.lower().strip()
        if not text:
            self.filtered_installed_results = self.all_installed_results
        else:
            self.filtered_installed_results = [
                app for app in self.all_installed_results 
                if text in app['name'].lower() or text in app['desc'].lower()
            ]
        
        self.current_inst_index = 0
        
        self.inst_load_more_container = None
        self.clear_layout(self.inst_layout)
        self.load_more_installed_apps()

    def handle_load_more_inst_click(self):
        self.inst_load_more_btn.hide()
        self.inst_bottom_spinner.start()
        QTimer.singleShot(200, self.load_more_installed_apps)

    def load_more_installed_apps(self):
        if hasattr(self, 'inst_load_more_container') and self.inst_load_more_container:
            try:
                self.inst_layout.removeWidget(self.inst_load_more_container)
                self.inst_load_more_container.deleteLater()
            except RuntimeError:
                pass
            self.inst_load_more_container = None

        chunk = self.filtered_installed_results[self.current_inst_index : self.current_inst_index + 30]
        self.current_inst_index += len(chunk)
        
        for i, app_data in enumerate(chunk):
            item_widget = AppListItem(app_data, self.is_dark, self.tr)
            item_widget.clicked.connect(self.open_app_details_from_list)
            self.inst_layout.addWidget(item_widget)
            self.list_items_refs[app_data['name']] = item_widget
            item_widget.animate_entry(delay=i * 30)

        if self.current_inst_index < len(self.filtered_installed_results):
            self.inst_load_more_container = QWidget()
            lay = QVBoxLayout(self.inst_load_more_container)
            lay.setContentsMargins(0, 20, 0, 20)
            lay.setAlignment(Qt.AlignCenter)
            
            self.inst_load_more_btn = QPushButton(self.tr("load_more"))
            self.inst_load_more_btn.setObjectName("LoadMoreBtn")
            self.inst_load_more_btn.setIcon(get_ui_icon("down_arrow", self.is_dark))
            self.inst_load_more_btn.setIconSize(QSize(14, 14))
            self.inst_load_more_btn.setCursor(Qt.PointingHandCursor)
            self.inst_load_more_btn.setFixedWidth(280)
            self.inst_load_more_btn.clicked.connect(self.handle_load_more_inst_click)
            
            self.inst_bottom_spinner = LoadingSpinner(size=28)
            self.inst_bottom_spinner.update_theme(self.is_dark)
            self.inst_bottom_spinner.hide()
            
            lay.addWidget(self.inst_load_more_btn, alignment=Qt.AlignCenter)
            lay.addWidget(self.inst_bottom_spinner, alignment=Qt.AlignCenter)
            
            self.inst_layout.addWidget(self.inst_load_more_container)
            
        apps_to_load = [app['name'] for app in chunk if not get_local_icon(app['name'], 50)]
        self.request_icons(apps_to_load)

    def open_category(self, cat_name):
        self.navigate_to(1)
        self.search_bar.clear() 
        self.search_popup.hide()
        
        self.cat_load_more_container = None
        self.clear_layout(self.list_layout)
        
        self.current_cat_name = cat_name
        self.current_cat_apps = [app[0] for app in HOME_CATEGORIES[cat_name]]
        self.current_cat_index = 0
        self.list_items_refs = {}
        
        self.list_spinner.start()
        self.load_more_category_apps()

    def handle_cat_load_more_click(self):
        self.cat_load_more_btn.hide()
        self.cat_bottom_spinner.start()
        self.load_more_category_apps()

    def load_more_category_apps(self):
        apps_to_fetch = self.current_cat_apps[self.current_cat_index : self.current_cat_index + 10]
        if not apps_to_fetch: return

        self.status_lbl.setText(f"{self.tr(f'cat_{self.current_cat_name}')}")
        self.category_worker.load_category(apps_to_fetch, self.current_cat_name)

    def populate_category(self, results, cat_name):
        self.list_spinner.stop()
        if hasattr(self, 'cat_load_more_container') and self.cat_load_more_container:
            try:
                self.list_layout.removeWidget(self.cat_load_more_container)
                self.cat_load_more_container.deleteLater()
            except RuntimeError:
                pass
            self.cat_load_more_container = None

        self.current_cat_index += len(results)
        
        for i, app_data in enumerate(results):
            item_widget = AppListItem(app_data, self.is_dark, self.tr)
            item_widget.clicked.connect(self.open_app_details_from_list)
            self.list_layout.addWidget(item_widget)
            self.list_items_refs[app_data['name']] = item_widget
            item_widget.animate_entry(delay=i * 30)

        if self.current_cat_index < len(self.current_cat_apps):
            self.cat_load_more_container = QWidget()
            lay = QVBoxLayout(self.cat_load_more_container)
            lay.setContentsMargins(0, 20, 0, 20)
            lay.setAlignment(Qt.AlignCenter)
            
            self.cat_load_more_btn = QPushButton(self.tr("load_more"))
            self.cat_load_more_btn.setObjectName("LoadMoreBtn")
            self.cat_load_more_btn.setIcon(get_ui_icon("down_arrow", self.is_dark))
            self.cat_load_more_btn.setIconSize(QSize(14, 14))
            self.cat_load_more_btn.setCursor(Qt.PointingHandCursor)
            self.cat_load_more_btn.setFixedWidth(280)
            self.cat_load_more_btn.clicked.connect(self.handle_cat_load_more_click)
            
            self.cat_bottom_spinner = LoadingSpinner(size=28)
            self.cat_bottom_spinner.update_theme(self.is_dark)
            self.cat_bottom_spinner.hide()
            
            lay.addWidget(self.cat_load_more_btn, alignment=Qt.AlignCenter)
            lay.addWidget(self.cat_bottom_spinner, alignment=Qt.AlignCenter)
            
            self.list_layout.addWidget(self.cat_load_more_container)
        
        apps_to_load = [app['name'] for app in results if not get_local_icon(app['name'], 50)]
        self.request_icons(apps_to_load)

    def start_search(self):
        query = self.search_bar.text().strip()
        if query:
            self.navigate_to(1)
            self.status_lbl.setText(self.tr("results_for").format(query))
            
            self.search_popup.hide()
            self.search_bar.clearFocus()
            
            self.cat_load_more_container = None
            self.clear_layout(self.list_layout)
            
            self.list_spinner.start()
            self.search_worker.search(query)

    def populate_list(self, results):
        self.list_spinner.stop()
        if not results:
            self.status_lbl.setText(self.tr("no_results"))
            return
        self.list_items_refs = {}
        for i, app_data in enumerate(results):
            item_widget = AppListItem(app_data, self.is_dark, self.tr)
            item_widget.clicked.connect(self.open_app_details_from_list)
            self.list_layout.addWidget(item_widget)
            self.list_items_refs[app_data['name']] = item_widget
            item_widget.animate_entry(delay=i * 30)
        
        apps_to_load = [app['name'] for app in results if not get_local_icon(app['name'], 50)]
        self.request_icons(apps_to_load)

    def quick_search(self, query):
        self.navigate_to(2)
        self.search_bar.clear() 
        self.name_lab.setText(self.tr("loading"))
        self.desc_lab.setText(self.tr("fetching_info"))
        self.size_lab.setText("")
        self.stars_lab.setText("")
        self.set_placeholder_icon("?")
        
        self.btn_row_container.hide()
        self.progress_container.hide()
        
        self.detail_spinner.start()
        
        def fetch_exact():
            res_dict = {}
            proc = subprocess.run(['pacman', '-Si', query], capture_output=True, text=True)
            if proc.returncode == 0:
                desc = next((l for l in proc.stdout.split('\n') if l.startswith('Descripción') or l.startswith('Description')), "Desc: ").split(': ', 1)[-1]
                res_dict = {"name": query, "desc": desc, "has_pacman": True, "has_aur": False, "votes": 9999}
            else:
                aur_res = requests.get(f"https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={query}").json()
                if aur_res.get('results'):
                    item = aur_res['results'][0]
                    res_dict = {"name": item['Name'], "desc": item.get('Description',''), "has_pacman": False, "has_aur": True, "votes": item.get('NumVotes',0)}
            
            if res_dict:
                self.detail_worker.load_details(res_dict)
                class UIUpdater(QObject):
                    update_signal = Signal(dict)
                updater = UIUpdater()
                updater.update_signal.connect(self._prepare_detail_view)
                updater.update_signal.emit(res_dict)
                
        threading.Thread(target=fetch_exact).start()

    def open_app_details_from_list(self, data):
        self.navigate_to(2)
        self.detail_spinner.start()
        self.btn_row_container.hide()
        self.progress_container.hide()
        self._prepare_detail_view(data)
        self.detail_worker.load_details(data)

    def _prepare_detail_view(self, data):
        self.current_app_data = data
        self.name_lab.setText(data['name'])
        self.desc_lab.setText(data['desc'])
        self.size_lab.setText(self.tr("loading"))
        self.set_placeholder_icon(data['name'][0])
        
        app_name = data['name']
        if app_name in self.search_history:
            self.search_history.remove(app_name)
        self.search_history.append(app_name)
        if len(self.search_history) > 10:
            self.search_history.pop(0)
        self.save_history()
        
        votes = data.get('votes', 0)
        if data.get('has_pacman'): 
            self.stars_lab.setText(self.tr("qual_off"))
        else:
            if votes > 1000: self.stars_lab.setText(self.tr("pop_exc"))
            elif votes > 500: self.stars_lab.setText(self.tr("pop_vhigh"))
            elif votes > 50: self.stars_lab.setText(self.tr("pop_high"))
            elif votes > 10: self.stars_lab.setText(self.tr("pop_mod"))
            else: self.stars_lab.setText(self.tr("pop_new"))

        self.source_selector.blockSignals(True)
        self.source_selector.clear()
        
        if data.get('has_pacman'): 
            self.source_selector.addItem(QIcon(get_resource_path("pacman.svg")), self.tr("src_pacman"), "pacman")
        if data.get('has_aur'): 
            self.source_selector.addItem(QIcon(get_resource_path("aur.svg")), self.tr("src_aur"), "aur")
            
        self.source_selector.blockSignals(False)
        self.source_selector.setCurrentIndex(0)
        
        is_active_install = (self.active_install_pkg == app_name)
        
        if is_active_install:
            self.btn_row_container.hide()
            self.progress_container.show()
            if self.active_install_action in ["install", "update_app"] and self.active_install_source == "pacman":
                self.pacman_anim.start()
            else:
                self.pacman_anim.hide()
        else:
            self.btn_row_container.show()
            self.progress_container.hide()
            self.pacman_anim.stop()
            
            self.install_btn.setText(self.tr("loading"))
            self.install_btn.setObjectName("InstallBtn")
            self.install_btn.style().unpolish(self.install_btn)
            self.install_btn.style().polish(self.install_btn)
            self.open_btn.hide()
            self.check_app_btn.hide()
            self.update_app_btn.hide()
        
        while self.comments_container.count():
            w = self.comments_container.takeAt(0).widget()
            if w: w.deleteLater()

    def update_detail_ui(self, detailed_data):
        self.detail_spinner.stop()
        self.current_app_data.update(detailed_data)
        
        if "size" in detailed_data: self.size_lab.setText(self.tr("size_est").format(detailed_data['size']))

        is_active_install = (self.active_install_pkg == detailed_data['name'])
        
        if is_active_install:
            self.btn_row_container.hide()
            self.progress_container.show()
        else:
            self.btn_row_container.show() 
            self.progress_container.hide() 
            
            is_installed = detailed_data.get('is_installed', False)
            
            self.check_app_btn.hide()
            self.update_app_btn.hide()

            if is_installed:
                self.install_btn.setText(self.tr("uninstall_btn"))
                self.install_btn.setObjectName("UninstallBtn")
                self.open_btn.show()
                self.check_app_btn.setText(self.tr("check_up_btn"))
                self.check_app_btn.setEnabled(True)
                self.check_app_btn.show()
            else:
                self.install_btn.setText(self.tr("get_btn"))
                self.install_btn.setObjectName("InstallBtn")
                self.open_btn.hide()
                
            self.install_btn.style().unpolish(self.install_btn)
            self.install_btn.style().polish(self.install_btn)

        while self.comments_container.count():
            w = self.comments_container.takeAt(0).widget()
            if w: w.deleteLater()

        if detailed_data.get('has_pacman'):
            self.add_comment("Arch Linux", "Este paquete oficial ha sido verificado garantizando máxima estabilidad." if self.app_settings.get("lang",1)==0 else "This official package has been verified ensuring maximum stability.")
        elif detailed_data.get('comments'):
            for i, comment in enumerate(detailed_data['comments']):
                self.add_comment(f"Usuario AUR #{i+1}" if self.app_settings.get("lang",1)==0 else f"AUR User #{i+1}", comment[:300] + "..." if len(comment) > 300 else comment)
        else:
            self.add_comment("AUR", "No hay información adicional." if self.app_settings.get("lang",1)==0 else "No additional information available.")

        if detailed_data.get('icon_url') and not get_local_icon(detailed_data['name'], 120):
            app_name = detailed_data['name']
            if app_name in self.icon_cache:
                self.apply_icon(app_name, self.icon_cache[app_name])
            else:
                try:
                    img_data = requests.get(detailed_data['icon_url'], timeout=3).content
                    self.apply_icon(app_name, img_data)
                except: pass

    def add_comment(self, user, text):
        box = QFrame()
        box.setObjectName("ReviewBox")
        lay = QVBoxLayout(box)
        u_lab = QLabel(user)
        u_lab.setFont(QFont("SF Pro Text", 13, QFont.Bold))
        t_lab = QLabel(text)
        t_lab.setWordWrap(True)
        lay.addWidget(u_lab)
        lay.addSpacing(5)
        lay.addWidget(t_lab)
        self.comments_container.addWidget(box)

    def install_app(self):
        idx = self.source_selector.currentIndex()
        if idx < 0: return
        source_type = self.source_selector.itemData(idx)
        pkg = self.current_app_data["name"]
        is_installed = self.current_app_data.get("is_installed", False)
        
        action = "uninstall" if is_installed else "install"
        
        self.active_install_pkg = pkg
        self.active_install_action = action
        self.active_install_source = source_type
        
        self.btn_row_container.hide()
        self.progress_container.show()
        
        if action == "install" and source_type == "pacman":
            self.install_status_lbl.setText("Preparando instalación..." if self.app_settings.get("lang",1)==0 else "Preparing installation...")
            self.pacman_anim.start()
        elif action == "install":
            self.pacman_anim.hide()
            self.install_status_lbl.setText("Instalando desde AUR..." if self.app_settings.get("lang",1)==0 else "Installing from AUR...")
        else:
            self.pacman_anim.hide()
            self.install_status_lbl.setText("Desinstalando..." if self.app_settings.get("lang",1)==0 else "Uninstalling...")

        aur_backend = self.aur_cb.currentText()
        self.install_worker.run_command(action, source_type, pkg, aur_backend=aur_backend)

    def cancel_installation(self):
        self.install_worker.cancel()
        self.install_status_lbl.setText("Cancelando..." if self.app_settings.get("lang",1)==0 else "Cancelling...")

    def update_install_progress(self, text, action):
        clean_text = text.replace('\n', '').strip()
        if not clean_text or clean_text.startswith('['): return 
        if any(keyword in clean_text for keyword in ["Dload", "Xferd", "Received", "Total    %", "Average Speed"]): return
        if re.match(r'^[\d\s\.\%KMGTPBkmg/s\:\-\|]+$', clean_text): return

        if clean_text.startswith("::"): clean_text = clean_text.replace("::", "").strip()
        elif clean_text.startswith("->"): clean_text = clean_text.replace("->", "").strip()
        elif clean_text.startswith("==>"): clean_text = clean_text.replace("==>", "").strip()
            
        display_text = clean_text[:40] + "..." if len(clean_text) > 40 else clean_text
        
        if action in ["install", "uninstall", "update_app"]:
            self.install_status_lbl.setText(display_text)
        elif action == "update_sys":
            self.update_sys_btn.setText(display_text)
        elif action == "clean_sys":
            self.clean_sys_btn.setText(display_text)

    def on_install_finished(self, success, message, action):
        self.pacman_anim.stop()
        if self.active_install_pkg == self.current_app_data.get("name"):
            self.progress_container.hide()
            self.btn_row_container.show()
        self.active_install_pkg = None
        self.active_install_action = None
        self.active_install_source = None

        if success:
            if action in ["install", "uninstall", "update_app"]:
                self.detail_spinner.start()
                self.btn_row_container.hide()
                self.detail_worker.load_details(self.current_app_data)
                if self.app_settings.get("cache", 0) == 0:
                    self.install_worker.run_command("clean_sys", "yay", aur_backend=self.aur_cb.currentText())
            elif action == "clean_sys":
                if self.stacked.currentIndex() == 3:
                    self.toast = ToastNotification(self.centralWidget(), "Éxito" if self.app_settings.get("lang",1)==0 else "Success", self.tr("clean_sys") + " OK", self.is_dark)
                    self.toast.show_anim()
            else:
                self.toast = ToastNotification(self.centralWidget(), "Éxito" if self.app_settings.get("lang",1)==0 else "Success", "OK", self.is_dark)
                self.toast.show_anim()
                if action == "update_sys" and self.stacked.currentIndex() == 3:
                    self.open_installed()
        else:
            if action != "clean_sys":
                self.toast = ToastNotification(self.centralWidget(), "Error", "Error de red" if self.app_settings.get("lang",1)==0 else "Network Error", self.is_dark)
                self.toast.show_anim()
                if action in ["install", "uninstall", "update_app"]:
                    self.detail_spinner.start()
                    self.btn_row_container.hide()
                    self.detail_worker.load_details(self.current_app_data)

    def run_check_app(self):
        self.check_app_btn.setEnabled(False)
        self.check_app_btn.setText("Buscando..." if self.app_settings.get("lang",1)==0 else "Searching...")
        self.check_worker.check_app(self.current_app_data['name'])
        
    def on_app_update_checked(self, has_up, ver):
        if has_up:
            self.check_app_btn.hide()
            self.update_app_btn.setText(f"{self.tr('update_btn')} (v{ver})")
            self.update_app_btn.show()
        else:
            self.check_app_btn.setText(self.tr("app_updated"))

    def run_check_sys(self):
        self.check_sys_btn.setEnabled(False)
        self.check_sys_btn.setText("Buscando..." if self.app_settings.get("lang",1)==0 else "Searching...")
        self.check_worker.check_sys()
        
    def on_sys_update_checked(self, count):
        if count > 0:
            self.check_sys_btn.hide()
            self.update_sys_btn.setText(f"{self.tr('inst_sys')} ({count})")
            self.update_sys_btn.show()
        else:
            self.check_sys_btn.setText(self.tr("sys_updated"))

    def run_update_app(self):
        idx = self.source_selector.currentIndex()
        if idx < 0: return
        source_type = self.source_selector.itemData(idx)
        pkg = self.current_app_data["name"]
        
        self.active_install_pkg = pkg
        self.active_install_action = "update_app"
        self.active_install_source = source_type
        
        self.btn_row_container.hide()
        self.progress_container.show()
        
        if source_type == "pacman":
            self.install_status_lbl.setText("Preparando..." if self.app_settings.get("lang",1)==0 else "Preparing...")
            self.pacman_anim.start()
        else:
            self.pacman_anim.hide()
            self.install_status_lbl.setText("Actualizando desde AUR..." if self.app_settings.get("lang",1)==0 else "Updating from AUR...")

        self.install_worker.run_command("update_app", source_type, pkg, aur_backend=self.aur_cb.currentText())

    def run_system_update(self):
        self.update_sys_btn.setEnabled(False)
        self.update_sys_btn.setText("Iniciando..." if self.app_settings.get("lang",1)==0 else "Starting...")
        self.install_worker.run_command("update_sys", "yay", aur_backend=self.aur_cb.currentText())

    def run_system_clean(self):
        reply = QMessageBox.question(self, self.tr("clean_sys"), self.tr("cache_desc"), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.clean_sys_btn.setEnabled(False)
            self.clean_sys_btn.setText("Limpiando..." if self.app_settings.get("lang",1)==0 else "Cleaning...")
            self.install_worker.run_command("clean_sys", "yay", aur_backend=self.aur_cb.currentText())

    def launch_app(self):
        app_name = self.current_app_data.get("name", "")
        clean_name = app_name.lower().replace("-bin", "").replace("-git", "").replace("-desktop", "").replace("-stable", "")
        try:
            subprocess.Popen([clean_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = RubiAUR()
    window.show()
    sys.exit(app.exec())