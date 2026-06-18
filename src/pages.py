from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, 
    QScrollArea, QComboBox, QStyledItemDelegate
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QIcon
from utils import get_resource_path, get_ui_icon

class SettingsPage(QWidget):
    # Definición de señales para comunicarse con main.py
    back_requested = Signal()
    setting_changed = Signal(str, int) # key, index
    check_update_requested = Signal()
    reset_requested = Signal()
    about_requested = Signal()

    def __init__(self, app_settings, main_window):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("MainBg")
        self.app_settings = app_settings
        self.main_window = main_window # Referencia para tr() y utilidades si es necesario
        self._init_ui()

    def _init_ui(self):
        settings_page_layout = QVBoxLayout(self)
        settings_page_layout.setContentsMargins(50, 10, 50, 40)
        
        self.set_back_btn = QPushButton()
        self.set_back_btn.setIconSize(QSize(18, 18))
        self.set_back_btn.setObjectName("BackBtn")
        self.set_back_btn.setCursor(Qt.PointingHandCursor)
        self.set_back_btn.clicked.connect(self.back_requested.emit)
        settings_page_layout.addWidget(self.set_back_btn)

        self.settings_title = QLabel()
        self.settings_title.setFont(QFont("SF Pro Display", 32, QFont.Bold))
        settings_page_layout.addWidget(self.settings_title)
        settings_page_layout.addSpacing(20)

        set_scroll = QScrollArea()
        set_scroll.setWidgetResizable(True)
        set_container = QFrame()
        set_container.setObjectName("ListContainer")
        self.set_lay = QVBoxLayout(set_container)
        self.set_lay.setContentsMargins(30, 30, 30, 30)
        self.set_lay.setSpacing(20)
        self.set_lay.setAlignment(Qt.AlignTop)

        self.lang_cb = QComboBox()
        self.lang_cb.setItemDelegate(QStyledItemDelegate())
        self.lang_cb.addItems(["Español", "English", "Français", "Deutsch"])
        self.lang_cb.setMinimumWidth(150)
        self.lang_cb.setMaximumWidth(220)
        self.lang_cb.setFixedHeight(36)
        self.lang_cb.setCurrentIndex(self.app_settings.get("lang", 1))
        self.lang_cb.currentIndexChanged.connect(lambda i: self.setting_changed.emit("lang", i))
        self._create_dynamic_setting_row("lang_lbl", "lang_desc", self.lang_cb)

        self.theme_cb = QComboBox()
        self.theme_cb.setItemDelegate(QStyledItemDelegate())
        self.theme_cb.setMinimumWidth(150)
        self.theme_cb.setMaximumWidth(220)
        self.theme_cb.setFixedHeight(36)
        self.theme_cb.currentIndexChanged.connect(lambda i: self.setting_changed.emit("theme", i))
        self._create_dynamic_setting_row("theme_lbl", "theme_desc", self.theme_cb)

        self.aur_cb = QComboBox()
        self.aur_cb.setItemDelegate(QStyledItemDelegate())
        self.aur_cb.addItems(["yay", "paru"])
        self.aur_cb.setMinimumWidth(150)
        self.aur_cb.setMaximumWidth(220)
        self.aur_cb.setFixedHeight(36)
        self.aur_cb.setCurrentIndex(self.app_settings.get("aur", 0))
        self.aur_cb.currentIndexChanged.connect(lambda i: self.setting_changed.emit("aur", i))
        self._create_dynamic_setting_row("aur_lbl", "aur_desc", self.aur_cb)

        self.clean_cb = QComboBox()
        self.clean_cb.setItemDelegate(QStyledItemDelegate())
        self.clean_cb.setMinimumWidth(150)
        self.clean_cb.setMaximumWidth(220)
        self.clean_cb.setFixedHeight(36)
        self.clean_cb.currentIndexChanged.connect(lambda i: self.setting_changed.emit("cache", i))
        self._create_dynamic_setting_row("cache_lbl", "cache_desc", self.clean_cb)

        self.up_cb = QComboBox()
        self.up_cb.setItemDelegate(QStyledItemDelegate())
        self.up_cb.setMinimumWidth(150)
        self.up_cb.setMaximumWidth(220)
        self.up_cb.setFixedHeight(36)
        self.up_cb.currentIndexChanged.connect(lambda i: self.setting_changed.emit("updates", i))
        self._create_dynamic_setting_row("up_lbl", "up_desc", self.up_cb)

        self.app_update_btn = QPushButton()
        self.app_update_btn.setCursor(Qt.PointingHandCursor)
        self.app_update_btn.setStyleSheet("background-color: #0071E3; color: white; border-radius: 12px; font-weight: bold; font-size: 13px; padding: 8px 15px; border: none;")
        self.app_update_btn.setMinimumWidth(150)
        self.app_update_btn.clicked.connect(self.check_update_requested.emit)
        
        self._create_dynamic_setting_row("app_up_title", "app_up_desc", self.app_update_btn)

        self.reset_btn = QPushButton()
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.setStyleSheet("background-color: transparent; color: #FF3B30; font-weight: bold; font-size: 14px; text-decoration: underline; border: none; padding: 10px;")
        self.reset_btn.clicked.connect(self.reset_requested.emit)
        
        self.about_btn = QPushButton()
        self.about_btn.setCursor(Qt.PointingHandCursor)
        self.about_btn.setStyleSheet("background-color: #0071E3; color: white; border-radius: 14px; font-weight: bold; font-size: 13px; padding: 8px 20px; border: none;")
        self.about_btn.clicked.connect(self.about_requested.emit)

        self.set_lay.addSpacing(10)
        self.set_lay.addWidget(self.reset_btn, alignment=Qt.AlignCenter)
        self.set_lay.addSpacing(5)
        self.set_lay.addWidget(self.about_btn, alignment=Qt.AlignCenter)

        self.company_logo_lbl = QLabel()
        self.company_logo_lbl.setAlignment(Qt.AlignCenter)
        self.set_lay.addSpacing(20)
        self.set_lay.addWidget(self.company_logo_lbl, alignment=Qt.AlignCenter)

        set_scroll.setWidget(set_container)
        settings_page_layout.addWidget(set_scroll)

    def _create_dynamic_setting_row(self, title_key, desc_key, widget):
        row_widget = QWidget()
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0,0,0,0)
        text_ly = QVBoxLayout()
        text_ly.setSpacing(2)
        t_lbl = QLabel()
        t_lbl.setFont(QFont("SF Pro Display", 15, QFont.Bold))
        t_lbl.setProperty("trans_key", title_key)
        
        d_lbl = QLabel()
        d_lbl.setFont(QFont("SF Pro Display", 12))
        d_lbl.setStyleSheet("color: #8E8E93;")
        d_lbl.setWordWrap(True)
        d_lbl.setProperty("trans_key", desc_key)
        
        text_ly.addWidget(t_lbl)
        text_ly.addWidget(d_lbl)
        row.addLayout(text_ly)
        row.addStretch()
        row.addWidget(widget, 0, Qt.AlignVCenter)
        
        self.set_lay.addWidget(row_widget)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setObjectName("SeparatorLine")
        self.set_lay.addWidget(sep)

    def update_texts(self, tr_func):
        self.set_back_btn.setText(f" {tr_func('back_btn')}")
        self.settings_title.setText(tr_func("settings_title"))
        self.reset_btn.setText(tr_func("reset_btn"))
        self.about_btn.setText(tr_func("about_btn"))
        self.app_update_btn.setText(tr_func("app_up_btn"))
        
        # Actualizar labels dinámicos
        for i in range(self.set_lay.count()):
            item = self.set_lay.itemAt(i)
            if item.widget():
                row_w = item.widget()
                if row_w.layout():
                    text_ly = row_w.layout().itemAt(0)
                    if text_ly and text_ly.layout():
                        t_lbl = text_ly.layout().itemAt(0).widget()
                        d_lbl = text_ly.layout().itemAt(1).widget()
                        if t_lbl and t_lbl.property("trans_key"):
                            t_lbl.setText(tr_func(t_lbl.property("trans_key")))
                        if d_lbl and d_lbl.property("trans_key"):
                            d_lbl.setText(tr_func(d_lbl.property("trans_key")))
                            
    def update_theme(self, is_dark):
        logo_name = "moralesb7-logo-vector-dark.svg" if is_dark else "moralesb7-logo-vector.svg"
        self.company_logo_lbl.setPixmap(QIcon(get_resource_path(logo_name)).pixmap(180, 60))
        self.set_back_btn.setIcon(get_ui_icon("back", is_dark))
