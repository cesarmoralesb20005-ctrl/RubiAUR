import math
from PySide6.QtWidgets import (QWidget, QFrame, QLabel, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QStackedWidget,
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QEasingCurve, 
                          QPoint, QTimer, QSequentialAnimationGroup)
from PySide6.QtGui import (QFont, QPixmap, QPainter, QPainterPath, 
                         QIcon, QColor, QPen)
from utils import get_local_icon, create_rounded_pixmap, get_resource_path

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


#AQUI SALE YAY Y PARU 
class FeaturedAppCard(QFrame):
    clicked = Signal(str)
    
    # Añadimos badge_text como parámetro
    def __init__(self, name, title, desc, bg_color, badge_text):
        super().__init__()
        self.app_name = name
        self.setObjectName("FeaturedCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(160) 
        
        self.setStyleSheet(f"""
            #FeaturedCard {{
                background-color: {bg_color};
                border-radius: 20px;
            }}
            #FeaturedCard:hover {{
                border: 2px solid rgba(255,255,255,0.3);
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        
        v_lay = QVBoxLayout()

        self.badge_lbl = QLabel(badge_text)
        self.badge_lbl.setStyleSheet("color: rgba(255,255,255,0.8); font-weight: bold; font-size: 12px;")
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")
        
        self.desc_lbl = QLabel(desc)
        self.desc_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 14px;")
        self.desc_lbl.setWordWrap(True)
        
        v_lay.addWidget(self.badge_lbl)
        v_lay.addWidget(self.title_lbl)
        v_lay.addWidget(self.desc_lbl)
        v_lay.addStretch()
        
        icon_lbl = QLabel()
        icon_pix = QIcon(get_resource_path("aur.svg")).pixmap(80, 80)
        icon_lbl.setPixmap(icon_pix)
        
        layout.addLayout(v_lay, 1)
        layout.addWidget(icon_lbl, 0, Qt.AlignVCenter)

    def update_texts(self, new_badge, new_desc):
        self.badge_lbl.setText(new_badge)
        self.desc_lbl.setText(new_desc)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.app_name)