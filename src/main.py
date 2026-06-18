import sys, subprocess, requests, threading, concurrent.futures, random, os, json, re, math, shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QFrame, QComboBox, QStackedWidget, QScrollArea, QGridLayout,
                             QMessageBox, QGraphicsOpacityEffect, QListWidget, QListWidgetItem,
                             QGraphicsDropShadowEffect, QStyledItemDelegate, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QObject, QPropertyAnimation, QEasingCurve, QSize, QPoint, QTimer, QSequentialAnimationGroup, QUrl
from PySide6.QtGui import QFont, QPixmap, QImage, QPainter, QPainterPath, QIcon, QColor, QPen, QPalette, QDesktopServices
from constantes import HOME_CATEGORIES
from utils import get_resource_path, get_ui_icon, get_local_icon, create_rounded_pixmap, is_aur_helper_installed
from workers import (AutocompleteWorker, CheckUpdateWorker, InstallWorker, 
                     InstalledAppsWorker, CategoryWorker, IconWorker, 
                     SearchListWorker, DetailWorker, AurInstallerWorker, SelfUpdateWorker, GalleryWorker)
from idiomas import TRANSLATIONS
from widgets import (ToastNotification, SearchLineEdit, FadeStackedWidget)
from config import load_settings, save_settings, load_history, save_history
from style import get_stylesheet
from pages import SettingsPage

# --- 4. INTERFAZ PRINCIPAL ---
class RubiAUR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RubiAUR")
        self.setWindowIcon(QIcon(get_resource_path("logo.svg")))
        self.setMinimumSize(750, 550) 
        self.resize(900, 650)
        
        self.CURRENT_VERSION = "1.3" # La versión actual de tu app
        self.github_update_link = ""
        
        # Iniciamos el worker de actualización propia
        self.self_updater = SelfUpdateWorker()
        self.self_updater.result.connect(self.on_self_update_result)
        self.self_updater.check(self.CURRENT_VERSION) # Verifica en silencio al abrir

        self.last_view = 0
        self.icon_cache = {} 
        
        # Configuraciones y caché
        self.app_settings = load_settings({
            "lang": 1, "aur": 0, "cache": 0, "updates": 0, "theme": 0
        })
        self.search_history = load_history()
        
        self.active_install_pkg = None
        self.active_install_action = None
        self.active_install_source = None
        
                        
        theme_val = self.app_settings.get("theme", 0)
        if theme_val == 0:
            self.is_dark = QApplication.palette().color(QPalette.Window).lightness() < 128
        else:
            self.is_dark = (theme_val == 2)
        
        self.search_worker = SearchListWorker()
        self.search_worker.finished.connect(lambda r: self.page_list.populate_list(r) if hasattr(self, 'page_list') else None)
        self.category_worker = CategoryWorker()
        self.category_worker.finished.connect(lambda r, c: self.page_list.populate_category(r, c) if hasattr(self, 'page_list') else None)
        self.installed_worker = InstalledAppsWorker()
        self.installed_worker.finished.connect(lambda r: self.page_inst.populate_installed(r) if hasattr(self, 'page_inst') else None)
        self.detail_worker = DetailWorker()
        self.detail_worker.finished.connect(lambda r: self.page_detail.update_ui(r) if hasattr(self, 'page_detail') else None)
        self.icon_worker = IconWorker()
        self.icon_worker.icon_data_ready.connect(self.apply_icon)
        
        self.gallery_worker = GalleryWorker()
        self.gallery_worker.image_ready.connect(self.add_gallery_image)
        
        self.autocomplete_worker = AutocompleteWorker()
        self.autocomplete_worker.results_ready.connect(self.show_autocomplete_results)
        
        self.install_worker = InstallWorker()
        self.install_worker.finished.connect(self.on_install_finished)
        self.install_worker.progress.connect(self.update_install_progress) 
        
        self.check_worker = CheckUpdateWorker()
        self.check_worker.app_result.connect(self.on_app_update_checked)
        self.check_worker.sys_result.connect(self.on_sys_update_checked)
        
        self.current_app_data = {}
                        
                                
                                
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

    def save_settings(self):
        save_settings(self.app_settings)

    def save_history(self):
        save_history(self.search_history)

    def check_dependencies(self):
        if not is_aur_helper_installed():
            self.header_frame.hide()
            self.stacked.setCurrentIndex(5) 
            if hasattr(self, 'page_setup'): self.page_setup.set_status(self.tr, "installing_yay")
            
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
        else:
            self.toast = ToastNotification(self.centralWidget(), "Error de Instalación", msg, self.is_dark)
            self.toast.show_anim()
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
        if hasattr(self, 'page_settings'):
            self.page_settings.update_texts(self.tr)
        if hasattr(self, 'page_list'):
            self.page_list.update_texts(self.tr)
        if hasattr(self, 'page_detail'):
            self.page_detail.update_texts(self.tr)
        
        if hasattr(self, 'page_home'):
            self.page_home.update_texts(self.tr)
            self.page_home.update_lang(self.app_settings.get("lang", 1))

        
        if hasattr(self, 'page_inst'):
            if hasattr(self.page_inst, 'all_installed_results'):
                self.page_inst.inst_title.setText(f"{self.tr('inst_title')} ({len(self.page_inst.all_installed_results)})")
            else:
                self.page_inst.inst_title.setText(self.tr("inst_title"))
            self.page_inst.update_texts(self.tr)
        if hasattr(self, 'page_settings'):
            self.refresh_combo_box(self.page_settings.theme_cb, ["opt_auto", "opt_light", "opt_dark"])
            self.refresh_combo_box(self.page_settings.clean_cb, ["opt_clean_auto", "opt_clean_man"])
            self.refresh_combo_box(self.page_settings.up_cb, ["opt_up_start", "opt_up_no"])
        if hasattr(self, 'page_setup'): self.page_setup.set_status(self.tr, "installing_yay")

        if hasattr(self, 'yay_card'):
            self.yay_card.update_texts(self.tr("feat_badge"), self.tr("yay_desc"))
        if hasattr(self, 'paru_card'):
            self.paru_card.update_texts(self.tr("feat_badge"), self.tr("paru_desc"))

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

    def update_setting(self, key, index):
        self.app_settings[key] = index
        self.save_settings()
        if key == "theme":
            self.apply_theme()

    def reset_settings(self):
        reply = QMessageBox.question(self, self.tr("settings_title"), self.tr("reset_btn") + "?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.app_settings = {"lang": 1, "theme": 0, "aur": 0, "cache": 0, "updates": 1}
            self.save_settings()
            
            if hasattr(self, 'page_settings'):
                for cb, idx in [(self.page_settings.lang_cb, 1), (self.page_settings.aur_cb, 0), (self.page_settings.clean_cb, 0), (self.page_settings.up_cb, 1), (self.page_settings.theme_cb, 0)]:
                    cb.blockSignals(True)
                    cb.setCurrentIndex(idx)
                    cb.blockSignals(False)
            
            self.apply_theme()
            self.live_update_settings_language(1)
            
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

        self.settings_badge = QLabel(self.settings_btn)
        self.settings_badge.setFixedSize(12, 12)
        self.settings_badge.setStyleSheet("background-color: #FF3B30; border-radius: 6px;")
        self.settings_badge.move(26, 0)
        self.settings_badge.hide()


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
        from pages import SettingsPage, InstalledPage, HomePage
        # --- PANTALLA 0: INICIO ---
        self.page_home = HomePage(self)
        self.page_home.quick_search_requested.connect(self.quick_search)
        self.page_home.open_category_requested.connect(self.open_category)
        self.stacked.addWidget(self.page_home)

        # --- PANTALLA 1: RESULTADOS ---
        from pages import ListPage
        self.page_list = ListPage(self)
        self.page_list.back_requested.connect(self.go_home_from_list)
        self.page_list.app_selected.connect(self.open_app_details_from_list)
        self.page_list.icons_requested.connect(self.request_icons)
        self.stacked.addWidget(self.page_list)

        # --- PANTALLA 2: DETALLES ---
        from pages import DetailPage
        self.page_detail = DetailPage(self)
        self.page_detail.back_requested.connect(self.go_back)
        self.page_detail.install_requested.connect(self.run_install_action)
        self.page_detail.cancel_requested.connect(self.cancel_installation)
        self.page_detail.check_app_requested.connect(self.run_check_app)
        self.page_detail.launch_requested.connect(self.launch_app)
        self.stacked.addWidget(self.page_detail)

        # --- PANTALLA 3: INSTALADAS ---
        self.page_inst = InstalledPage(self)
        self.page_inst.back_requested.connect(lambda: self.navigate_to(0))
        self.page_inst.app_selected.connect(self.open_app_details_from_list)
        self.page_inst.clean_sys_requested.connect(self.run_system_clean)
        self.page_inst.check_sys_requested.connect(self.run_check_sys)
        self.page_inst.update_sys_requested.connect(self.run_system_update)
        self.stacked.addWidget(self.page_inst)

        # --- PANTALLA 4: CONFIGURACIÓN ---
        # --- PANTALLA 4: AJUSTES ---
        self.page_settings = SettingsPage(self.app_settings, self)
        self.page_settings.back_requested.connect(lambda: self.navigate_to(0))
        self.page_settings.setting_changed.connect(lambda k, i: self.live_update_settings_language(i) if k == "lang" else self.update_setting(k, i))
        self.page_settings.check_update_requested.connect(self.check_self_update)
        self.page_settings.reset_requested.connect(self.reset_settings)
        self.page_settings.about_requested.connect(self.show_about_dialog)
        self.stacked.addWidget(self.page_settings)

        # --- PANTALLA 5: INSTALANDO DEPENDENCIA (YAY) ---
        from pages import SetupPage
        self.page_setup = SetupPage(self)
        self.stacked.addWidget(self.page_setup)
        layout.addWidget(self.stacked)

    def apply_theme(self):
        theme_val = self.app_settings.get("theme", 0)
        if theme_val == 0:
            self.is_dark = QApplication.palette().color(QPalette.Window).lightness() < 128
        else:
            self.is_dark = (theme_val == 2)
            
        self.setStyleSheet(get_stylesheet(self.is_dark))

        if hasattr(self, 'logo_btn'): self.logo_btn.setIcon(QIcon(get_resource_path("logo.svg")))
        if hasattr(self, 'installed_btn'): self.installed_btn.setIcon(get_ui_icon("installed", self.is_dark))
        if hasattr(self, 'settings_btn'): self.settings_btn.setIcon(get_ui_icon("settings", self.is_dark))
        
        if hasattr(self, 'page_settings'): self.page_settings.update_theme(self.is_dark)
        if hasattr(self, 'page_inst'): self.page_inst.update_theme(self.is_dark)
        if hasattr(self, 'page_list'): self.page_list.update_theme(self.is_dark)
        if hasattr(self, 'page_detail'): self.page_detail.update_theme(self.is_dark)
        if hasattr(self, 'page_setup'): self.page_setup.update_theme(self.is_dark)
        
        
        if hasattr(self, 'setup_spinner') and self.setup_spinner: self.setup_spinner.update_theme(self.is_dark)
        
        if hasattr(self, 'page_settings'):
            self.page_settings.update_theme(self.is_dark)
        if hasattr(self, 'page_inst'):
            self.page_inst.update_theme(self.is_dark)
            
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

    def add_gallery_image(self, img_data):
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        if not pixmap.isNull():
            scaled = pixmap.scaledToHeight(270, Qt.SmoothTransformation)
            rounded = QPixmap(scaled.size())
            rounded.fill(Qt.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, scaled.width(), scaled.height(), 16, 16)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, scaled)
            painter.end()
            lbl = QLabel()
            lbl.setPixmap(rounded)
            self.gallery_container_lay.addWidget(lbl)
            
    def apply_icon(self, app_name, img_data):
        self.icon_cache[app_name] = img_data
        image = QImage.fromData(img_data)
        pixmap = QPixmap.fromImage(image)
        
        if hasattr(self, 'page_home') and app_name in self.page_home.home_cards_refs:
            self.page_home.home_cards_refs[app_name].set_icon(create_rounded_pixmap(pixmap, 60, 12))

        if hasattr(self, 'page_list') and app_name in self.page_list.list_items_refs:
            self.page_list.list_items_refs[app_name].set_icon(create_rounded_pixmap(pixmap, 50, 12))
            
        if hasattr(self, 'page_detail') and hasattr(self, 'current_app_data') and self.current_app_data.get('name') == app_name:
            self.page_detail.icon_lab.setStyleSheet("background-color: transparent;")
            self.page_detail.icon_lab.setPixmap(create_rounded_pixmap(pixmap, 120, 25))

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
        self.page_inst.inst_search_bar.clear()
        self.search_popup.hide()
        
        self.page_inst.reload()

    def open_category(self, cat_name):
        self.navigate_to(1)
        self.search_bar.clear() 
        self.search_popup.hide()
        if hasattr(self, 'page_list'):
            self.page_list.prepare_category(cat_name)
            chunk = self.page_list.current_cat_apps[:30]
            self.category_worker.load_category(chunk, cat_name)

    def start_search(self):
        query = self.search_bar.text().strip()
        if query:
            self.navigate_to(1)
            if hasattr(self, 'page_list'):
                self.page_list.prepare_search(query)
            self.search_popup.hide()
            self.search_bar.clearFocus()
            self.search_worker.search(query)

    def quick_search(self, query):
        self.navigate_to(2)
        if hasattr(self, 'page_detail'):
            self.page_detail.name_lab.setText(self.tr("loading"))
            self.page_detail.desc_lab.setText(self.tr("fetching_info"))
            self.page_detail.size_lab.setText("")
            self.page_detail.stars_lab.setText("")
            self.page_detail.set_placeholder_icon("?")
            self.page_detail.btn_row_container.hide()
            self.page_detail.progress_container.hide()
            self.page_detail.detail_spinner.start()
        
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
        if hasattr(self, 'page_detail'):
            self.page_detail.prepare_view(data)
        self.current_app_data = data
        self.detail_worker.load_details(data)

    
    def run_install_action(self, action, source_type, pkg):
        aur_backend = self.page_settings.aur_cb.currentText() if hasattr(self, 'page_settings') else "yay"
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
            
        if any(x in clean_text.lower() for x in ["nada que hacer", "nothing to do"]):
            clean_text = self.tr("nothing_to_do")
            
        display_text = clean_text[:40] + "..." if len(clean_text) > 40 else clean_text
        
        if action in ["install", "uninstall", "update_app"]:
            if hasattr(self, 'page_detail'): self.page_detail.install_status_lbl.setText(display_text)
        elif action == "update_sys":
            if hasattr(self, 'page_inst'): self.page_inst.update_sys_btn.setText(display_text)
        elif action == "clean_sys":
            if hasattr(self, 'page_inst'): self.page_inst.clean_sys_btn.setText(display_text)

    def on_install_finished(self, success, message, action):
        if hasattr(self, 'page_detail'):
            self.page_detail.pacman_anim.stop()
            if self.page_detail.active_install_pkg == self.current_app_data.get("name"):
                self.page_detail.progress_container.hide()
                self.page_detail.btn_row_container.show()
            self.page_detail.active_install_pkg = None
            self.page_detail.active_install_action = None
            self.page_detail.active_install_source = None

        if success:
            if action in ["install", "uninstall", "update_app"]:
                if hasattr(self, 'page_detail'): self.page_detail.detail_spinner.start()
                if hasattr(self, 'page_detail'): self.page_detail.btn_row_container.hide()
                self.detail_worker.load_details(self.current_app_data)
                if self.app_settings.get("cache", 0) == 0:
                    self.run_system_clean()
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
                    if hasattr(self, 'page_detail'): self.page_detail.detail_spinner.start()
                    if hasattr(self, 'page_detail'): self.page_detail.btn_row_container.hide()
                    self.detail_worker.load_details(self.current_app_data)

    def run_check_app(self, pkg):
        if hasattr(self, 'page_detail'):
            self.page_detail.check_app_btn.setEnabled(False)
            self.page_detail.check_app_btn.setText("Buscando..." if self.app_settings.get("lang",1)==0 else "Searching...")
        self.check_worker.check_app(pkg)
        
    def on_app_update_checked(self, has_up, ver):
        if hasattr(self, 'page_detail'):
            self.page_detail.on_app_update_checked(has_up, ver)
            
    def run_check_sys(self):
        if hasattr(self, 'page_inst'):
            self.page_inst.check_sys_btn.setEnabled(False)
            self.page_inst.check_sys_btn.setText("Buscando..." if self.app_settings.get("lang",1)==0 else "Searching...")
        self.check_worker.check_sys()
        
    def on_sys_update_checked(self, count):
        if count > 0:
            if hasattr(self, 'page_inst'):
                self.page_inst.check_sys_btn.hide()
                self.page_inst.update_sys_btn.setText(f"{self.tr('inst_sys')} ({count})")
                self.page_inst.update_sys_btn.show()
        else:
            if hasattr(self, 'page_inst'):
                self.page_inst.check_sys_btn.setText(self.tr("sys_updated"))
                self.page_inst.check_sys_btn.setEnabled(True)

    def run_system_update(self):
        if hasattr(self, 'page_inst'):
            self.page_inst.update_sys_btn.setEnabled(False)
            self.page_inst.update_sys_btn.setText("Iniciando..." if self.app_settings.get("lang",1)==0 else "Starting...")
        aur_backend = self.page_settings.aur_cb.currentText() if hasattr(self, 'page_settings') else "yay"
        self.install_worker.run_command("update_sys", "aur", aur_backend=aur_backend)

    def run_system_clean(self):
        aur_backend = self.page_settings.aur_cb.currentText() if hasattr(self, 'page_settings') else "yay"
        if aur_backend in ["yay", "paru"]:
            if hasattr(self, 'page_inst'):
                self.page_inst.clean_sys_btn.setEnabled(False)
                self.page_inst.clean_sys_btn.setText("Limpiando..." if self.app_settings.get("lang",1)==0 else "Cleaning...")
            self.install_worker.run_command("clean_sys", "aur", aur_backend=aur_backend)

    def launch_app(self):
        app_name = self.current_app_data.get("name", "")
        clean_name = app_name.lower().replace("-bin", "").replace("-git", "").replace("-desktop", "").replace("-stable", "")
        
        comandos_especiales = {
            "visual-studio-code": "code",
            "google-chrome": "google-chrome-stable",
            "intellij-idea-community-edition": "idea",
            "pycharm-community-edition": "pycharm",
            "github": "github-desktop",
            "telegram": "telegram-desktop"
        }
        
        comando_final = comandos_especiales.get(clean_name, clean_name)
        
        try:
            subprocess.Popen([comando_final], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            msg = f"Iniciando {app_name}..." if self.app_settings.get("lang", 1) == 0 else f"Starting {app_name}..."
            self.toast = ToastNotification(self.centralWidget(), "Abriendo" if self.app_settings.get("lang", 1) == 0 else "Opening", msg, self.is_dark)
            self.toast.show_anim()
            
        except FileNotFoundError:
            err = f"No se encontró el comando '{comando_final}'." if self.app_settings.get("lang", 1) == 0 else f"Command '{comando_final}' not found."
            self.toast = ToastNotification(self.centralWidget(), "Error", err, self.is_dark)
            self.toast.show_anim()
        except Exception as e:
            self.toast = ToastNotification(self.centralWidget(), "Error", str(e), self.is_dark)
            self.toast.show_anim()

    def show_about_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(self.tr("about_btn"))
        msg.setTextFormat(Qt.RichText)
        msg.setText(self.tr("about_text"))
        
        logo_pixmap = QIcon(get_resource_path("logo.svg")).pixmap(64, 64)
        if not logo_pixmap.isNull():
            msg.setIconPixmap(logo_pixmap)
        
        if self.is_dark:
            msg.setStyleSheet("""
                QMessageBox { background-color: #1C1C1E; color: white; } 
                QLabel { color: white; font-size: 14px; } 
                QPushButton { background-color: #0A84FF; color: white; border-radius: 6px; padding: 6px 15px; font-weight: bold; }
                QPushButton:hover { background-color: #0071E3; }
            """)
        else:
            msg.setStyleSheet("""
                QMessageBox { background-color: white; color: #1D1D1F; } 
                QLabel { color: #1D1D1F; font-size: 14px; } 
                QPushButton { background-color: #0071E3; color: white; border-radius: 6px; padding: 6px 15px; font-weight: bold; }
                QPushButton:hover { background-color: #005BB5; }
            """)
            
        msg.exec()

    def check_self_update(self):
        if hasattr(self, 'page_settings'):
            self.page_settings.app_update_btn.setText("...")
            self.page_settings.app_update_btn.setEnabled(False)
        self.self_updater.check(self.CURRENT_VERSION)

    def on_self_update_result(self, has_update, latest_ver, link):
        if hasattr(self, 'page_settings'):
            btn = self.page_settings.app_update_btn
            btn.setEnabled(True)
            self.github_update_link = link
            
            if has_update:
                self.settings_badge.show()
                btn.setStyleSheet("background-color: #34C759; color: white; border-radius: 12px; font-weight: bold; font-size: 13px; padding: 8px 15px; border: none;")
                btn.setText(self.tr("app_up_avail").format(latest_ver))
                try: btn.clicked.disconnect() 
                except: pass
                btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.github_update_link)))
            else:
                self.settings_badge.hide()
                btn.setStyleSheet("background-color: #E8E8ED; color: #1D1D1F; border-radius: 12px; font-weight: bold; font-size: 13px; padding: 8px 15px; border: none;")
                btn.setText(self.tr("app_up_to_date"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = RubiAUR()
    window.show()
    sys.exit(app.exec())