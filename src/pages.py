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

class InstalledPage(QWidget):
    back_requested = Signal()
    app_selected = Signal(dict)
    clean_sys_requested = Signal()
    check_sys_requested = Signal()
    update_sys_requested = Signal()

    def __init__(self, main_window):
        super().__init__()
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QScrollArea, QFrame
        from PySide6.QtGui import QFont, QCursor
        from widgets import LoadingSpinner
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("MainBg")
        self.main_window = main_window
        self.is_dark = main_window.is_dark
        self.tr = main_window.tr
        
        self.all_installed_results = []
        self.filtered_installed_results = []
        self.current_inst_index = 0
        self.list_items_refs = {}

        inst_page_layout = QVBoxLayout(self)
        inst_page_layout.setContentsMargins(50, 10, 50, 40)
        
        self.inst_back_btn = QPushButton()
        self.inst_back_btn.setIconSize(QSize(18, 18))
        self.inst_back_btn.setObjectName("BackBtn")
        self.inst_back_btn.setCursor(Qt.PointingHandCursor)
        self.inst_back_btn.clicked.connect(self.back_requested.emit)
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
        self.clean_sys_btn.clicked.connect(self.clean_sys_requested.emit)

        self.check_sys_btn = QPushButton()
        self.check_sys_btn.setStyleSheet("background-color: #F2F2F7; color: #0071E3; border-radius: 14px; font-weight: bold; font-size: 13px; padding: 8px 20px; border: none;")
        self.check_sys_btn.setCursor(Qt.PointingHandCursor)
        self.check_sys_btn.clicked.connect(self.check_sys_requested.emit)
        
        self.update_sys_btn = QPushButton()
        self.update_sys_btn.setStyleSheet("background-color: #0071E3; color: white; border-radius: 14px; font-weight: bold; font-size: 13px; padding: 8px 20px; border: none;")
        self.update_sys_btn.setCursor(Qt.PointingHandCursor)
        self.update_sys_btn.clicked.connect(self.update_sys_requested.emit)
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

    def reload(self):
        self.inst_title.setText(self.tr("analyzing"))
        self.inst_spinner.start()
        
        self.inst_load_more_container = None 
        for i in reversed(range(self.inst_layout.count())):
            item = self.inst_layout.itemAt(i)
            widget = item.widget()
            if widget: widget.deleteLater()
            
        self.check_sys_btn.setText(self.tr("check_sys"))
        self.check_sys_btn.setEnabled(True)
        self.check_sys_btn.show()
        self.update_sys_btn.hide()
        
        self.main_window.installed_worker.load()

    def populate_installed(self, results):
        self.inst_spinner.stop()
        self.inst_title.setText(f"{self.tr('inst_title')} ({len(results)})")
        self.all_installed_results = results 
        self.filtered_installed_results = results 
        self.current_inst_index = 0
        self.list_items_refs = {}
        
        self.inst_load_more_container = None
        for i in reversed(range(self.inst_layout.count())):
            item = self.inst_layout.itemAt(i)
            widget = item.widget()
            if widget: widget.deleteLater()
            
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
        for i in reversed(range(self.inst_layout.count())):
            item = self.inst_layout.itemAt(i)
            widget = item.widget()
            if widget: widget.deleteLater()
        self.load_more_installed_apps()

    def handle_load_more_inst_click(self):
        self.inst_load_more_btn.hide()
        from PySide6.QtCore import QTimer
        self.inst_bottom_spinner.start()
        QTimer.singleShot(200, self.load_more_installed_apps)

    def load_more_installed_apps(self):
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        from PySide6.QtCore import Qt
        from widgets import AppListItem, LoadingSpinner
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
            item_widget.clicked.connect(self.app_selected.emit)
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
            from utils import get_ui_icon
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
            
    def update_texts(self, tr_func):
        self.inst_back_btn.setText(f" {tr_func('back_btn')}")
        self.inst_search_bar.setPlaceholderText(tr_func("filter_inst"))
        if self.clean_sys_btn.text(): self.clean_sys_btn.setText(tr_func("clean_sys"))
        
    def update_theme(self, is_dark):
        self.is_dark = is_dark
        from utils import get_ui_icon
        self.inst_back_btn.setIcon(get_ui_icon("back", is_dark))
        if hasattr(self, 'inst_spinner') and self.inst_spinner: self.inst_spinner.update_theme(is_dark)
        if hasattr(self, 'inst_bottom_spinner') and self.inst_bottom_spinner: self.inst_bottom_spinner.update_theme(is_dark)

class HomePage(QWidget):
    quick_search_requested = Signal(str)
    open_category_requested = Signal(str)

    def __init__(self, main_window):
        super().__init__()
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QGridLayout
        from PySide6.QtGui import QFont, Qt
        from constantes import HOME_CATEGORIES
        from widgets import FeaturedAppCard, HomeAppCard
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("MainBg")
        self.main_window = main_window
        self.tr = main_window.tr
        self.app_settings = main_window.app_settings
        
        self.cat_buttons = {}
        self.home_cards_refs = {}

        home_layout = QVBoxLayout(self)
        home_layout.setContentsMargins(0,0,0,0)
        home_scroll = QScrollArea()
        home_scroll.setWidgetResizable(True)
        home_content = QWidget()
        home_content.setObjectName("MainBg")
        hc_layout = QVBoxLayout(home_content)
        hc_layout.setContentsMargins(50, 40, 50, 40)
        
        self.home_title_lbl = QLabel()
        self.home_title_lbl.setFont(QFont("SF Pro Display", 32, QFont.Bold))
        hc_layout.addWidget(self.home_title_lbl)
        hc_layout.addSpacing(20)

        # --- BANNERS DESTACADOS ---
        featured_lay = QHBoxLayout()
        featured_lay.setSpacing(20)
        
        self.yay_card = FeaturedAppCard("yay", "Yay", self.tr("yay_desc"), "#0071E3", self.tr("feat_badge")) 
        self.yay_card.clicked.connect(self.quick_search_requested.emit)
        
        self.paru_card = FeaturedAppCard("paru", "Paru", self.tr("paru_desc"), "#2C2C2E", self.tr("feat_badge")) 
        self.paru_card.clicked.connect(self.quick_search_requested.emit)
        
        featured_lay.addWidget(self.yay_card)
        featured_lay.addWidget(self.paru_card)
        
        hc_layout.addLayout(featured_lay)
        hc_layout.addSpacing(40)
        
        for cat_name, apps in HOME_CATEGORIES.items():
            cat_key = f"cat_{cat_name}"
            cat_btn = QPushButton()
            cat_btn.setObjectName("CategoryTitleBtn")
            cat_btn.setCursor(Qt.PointingHandCursor)
            cat_btn.clicked.connect(lambda checked, c=cat_name: self.open_category_requested.emit(c))
            hc_layout.addWidget(cat_btn)
            self.cat_buttons[cat_key] = cat_btn
            
            grid = QGridLayout()
            grid.setSpacing(15)
            row, col = 0, 0
            
            for app_name, desc_dict in apps[:4]:
                card = HomeAppCard(app_name, desc_dict, self.app_settings.get("lang", 1))
                card.clicked.connect(self.quick_search_requested.emit)
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
        
        self.update_texts(self.tr)

    def update_texts(self, tr_func):
        self.home_title_lbl.setText(tr_func("discover_title"))
        self.yay_card.update_texts(tr_func("feat_badge"), tr_func("yay_desc"))
        self.paru_card.update_texts(tr_func("feat_badge"), tr_func("paru_desc"))
        for cat_key, btn in self.cat_buttons.items():
            btn.setText(f"{tr_func(cat_key)}  >")

    def update_lang(self, lang_code):
        for card in self.home_cards_refs.values():
            card.update_lang(lang_code)

class ListPage(QWidget):
    back_requested = Signal()
    app_selected = Signal(dict)
    icons_requested = Signal(list)

    def __init__(self, main_window):
        super().__init__()
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame
        from PySide6.QtGui import QFont, Qt
        from widgets import LoadingSpinner
        from PySide6.QtCore import QSize
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("MainBg")
        self.main_window = main_window
        self.tr = main_window.tr
        self.is_dark = main_window.is_dark
        
        self.list_items_refs = {}
        self.current_cat_apps = []
        self.current_cat_index = 0
        self.cat_load_more_container = None
        self.current_cat_name = ""

        list_page_layout = QVBoxLayout(self)
        list_page_layout.setContentsMargins(50, 10, 50, 40)
        
        self.list_back_btn = QPushButton()
        self.list_back_btn.setIconSize(QSize(18, 18))
        self.list_back_btn.setObjectName("BackBtn")
        self.list_back_btn.setCursor(Qt.PointingHandCursor)
        self.list_back_btn.clicked.connect(self.back_requested.emit)
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

    def prepare_search(self, query):
        self.status_lbl.setText(self.tr("results_for").format(query))
        self.cat_load_more_container = None
        for i in reversed(range(self.list_layout.count())):
            item = self.list_layout.itemAt(i)
            widget = item.widget()
            if widget: widget.deleteLater()
        self.list_spinner.start()

    def populate_list(self, results):
        from utils import get_local_icon
        from widgets import AppListItem
        self.list_spinner.stop()
        if not results:
            self.status_lbl.setText(self.tr("no_results"))
            return
        self.list_items_refs = {}
        for i, app_data in enumerate(results):
            item_widget = AppListItem(app_data, self.is_dark, self.tr)
            item_widget.clicked.connect(self.app_selected.emit)
            self.list_layout.addWidget(item_widget)
            self.list_items_refs[app_data['name']] = item_widget
            item_widget.animate_entry(delay=i * 30)
        
        apps_to_load = [app['name'] for app in results if not get_local_icon(app['name'], 50)]
        if apps_to_load: self.icons_requested.emit(apps_to_load)

    def prepare_category(self, cat_name):
        from constantes import HOME_CATEGORIES
        self.status_lbl.setText(self.tr(f"cat_{cat_name}"))
        self.cat_load_more_container = None
        for i in reversed(range(self.list_layout.count())):
            item = self.list_layout.itemAt(i)
            widget = item.widget()
            if widget: widget.deleteLater()
        self.list_spinner.start()
        self.list_items_refs = {}
        self.current_cat_name = cat_name
        self.current_cat_apps = [app[0] for app in HOME_CATEGORIES[cat_name]]
        self.current_cat_index = 0

    def populate_category(self, results, cat_name):
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        from PySide6.QtCore import Qt, QSize
        from widgets import AppListItem, LoadingSpinner
        from utils import get_local_icon, get_ui_icon

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
            item_widget.clicked.connect(self.app_selected.emit)
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
        if apps_to_load: self.icons_requested.emit(apps_to_load)

    def handle_cat_load_more_click(self):
        from PySide6.QtCore import QTimer
        self.cat_load_more_btn.hide()
        self.cat_bottom_spinner.start()
        QTimer.singleShot(200, self.load_more_category_apps)

    def load_more_category_apps(self):
        chunk = self.current_cat_apps[self.current_cat_index : self.current_cat_index + 30]
        self.main_window.category_worker.load_category(chunk, self.current_cat_name)
        
    def update_texts(self, tr_func):
        self.list_back_btn.setText(f" {tr_func('back_btn')}")
        if hasattr(self, 'cat_load_more_btn') and self.cat_load_more_btn:
            self.cat_load_more_btn.setText(tr_func("load_more"))
            
    def update_theme(self, is_dark):
        from utils import get_ui_icon
        self.is_dark = is_dark
        self.list_back_btn.setIcon(get_ui_icon("back", is_dark))
        if hasattr(self, 'list_spinner') and self.list_spinner: self.list_spinner.update_theme(is_dark)
        if hasattr(self, 'cat_bottom_spinner') and self.cat_bottom_spinner: self.cat_bottom_spinner.update_theme(is_dark)
        if hasattr(self, 'cat_load_more_btn') and self.cat_load_more_btn:
            self.cat_load_more_btn.setIcon(get_ui_icon("down_arrow", is_dark))

class DetailPage(QWidget):
    back_requested = Signal()
    install_requested = Signal(str, str, str) # action, source, pkg
    cancel_requested = Signal()
    check_app_requested = Signal(str)
    launch_requested = Signal(str)

    def __init__(self, main_window):
        super().__init__()
        from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                                     QScrollArea, QWidget, QFrame, QComboBox, QStyledItemDelegate)
        from PySide6.QtGui import QFont, Qt
        from PySide6.QtCore import QSize
        from widgets import LoadingSpinner, PacmanProgress
        from utils import get_ui_icon
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("MainBg")
        self.main_window = main_window
        self.tr = main_window.tr
        self.app_settings = main_window.app_settings
        self.is_dark = main_window.is_dark
        
        self.active_install_pkg = None
        self.active_install_action = None
        self.active_install_source = None
        self.current_app_data = {}

        detail_layout = QVBoxLayout(self)
        detail_layout.setContentsMargins(0,0,0,0)
        
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail_content = QWidget()
        detail_content.setObjectName("MainBg")
        scroll_layout = QVBoxLayout(detail_content)
        scroll_layout.setContentsMargins(50, 10, 50, 40)
        
        self.back_btn = QPushButton()
        self.back_btn.setIconSize(QSize(18, 18))
        self.back_btn.setObjectName("BackBtn")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        scroll_layout.addWidget(self.back_btn)

        self.card = QFrame()
        self.card.setObjectName("AppCard")
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
        
        self.links_container = QWidget()
        links_lay = QHBoxLayout(self.links_container)
        links_lay.setContentsMargins(0, 5, 0, 0)
        links_lay.setAlignment(Qt.AlignLeft)
        
        self.web_btn = QPushButton()
        self.web_btn.setCursor(Qt.PointingHandCursor)
        self.web_btn.setStyleSheet("background-color: transparent; color: #0071E3; font-weight: bold; font-size: 13px; text-decoration: underline; border: none; padding: 0px; text-align: left;")
        self.web_btn.setIcon(get_ui_icon("web", False, custom_color="#0071E3"))
        self.web_btn.setIconSize(QSize(16, 16))
        
        self.source_btn = QPushButton()
        self.source_btn.setCursor(Qt.PointingHandCursor)
        self.source_btn.setStyleSheet("background-color: transparent; color: #0071E3; font-weight: bold; font-size: 13px; text-decoration: underline; border: none; padding: 0px; text-align: left;")
        self.source_btn.setIcon(get_ui_icon("package", False, custom_color="#0071E3"))
        self.source_btn.setIconSize(QSize(16, 16))
        
        links_lay.addWidget(self.web_btn)
        links_lay.addSpacing(15)
        links_lay.addWidget(self.source_btn)
        links_lay.addStretch()
        
        self.web_btn.hide()
        self.source_btn.hide()

        v_info.addLayout(name_lay)
        v_info.addWidget(self.stars_lab)
        v_info.addWidget(self.size_lab)
        v_info.addWidget(self.links_container)
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
        self.install_btn.clicked.connect(self.on_install_clicked)

        self.check_app_btn = QPushButton()
        self.check_app_btn.setProperty("class", "ActionBtn")
        self.check_app_btn.setStyleSheet("background-color: #F2F2F7; color: #0071E3;")
        self.check_app_btn.setFixedHeight(36)
        self.check_app_btn.setCursor(Qt.PointingHandCursor)
        self.check_app_btn.clicked.connect(self.on_check_app_clicked)
        self.check_app_btn.hide()

        self.update_app_btn = QPushButton()
        self.update_app_btn.setProperty("class", "ActionBtn")
        self.update_app_btn.setStyleSheet("background-color: #0071E3; color: white;")
        self.update_app_btn.setFixedHeight(36)
        self.update_app_btn.setCursor(Qt.PointingHandCursor)
        self.update_app_btn.clicked.connect(self.on_update_app_clicked)
        self.update_app_btn.hide()

        self.open_btn = QPushButton()
        self.open_btn.setProperty("class", "ActionBtn")
        self.open_btn.setStyleSheet("background-color: #0071E3; color: white;")
        self.open_btn.setFixedHeight(36)
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.clicked.connect(self.on_launch_clicked)
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
        self.cancel_install_btn.clicked.connect(self.cancel_requested.emit)

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
        self.card_lay.addSpacing(15)
        
        self.gallery_scroll = QScrollArea()
        self.gallery_scroll.setWidgetResizable(True)
        self.gallery_scroll.setFixedHeight(300)
        self.gallery_scroll.hide()
        
        self.gallery_container = QWidget()
        self.gallery_container.setStyleSheet("background: transparent;")
        self.gallery_container_lay = QHBoxLayout(self.gallery_container)
        self.gallery_container_lay.setContentsMargins(0, 0, 0, 0)
        self.gallery_container_lay.setSpacing(15)
        self.gallery_container_lay.setAlignment(Qt.AlignLeft)
        self.gallery_scroll.setWidget(self.gallery_container)
        
        self.gallery_label = QLabel()
        self.gallery_label.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        self.gallery_label.hide()
        
        self.gallery_warn = QLabel()
        self.gallery_warn.setStyleSheet("color: #888888; font-size: 11px;")
        self.gallery_warn.hide()
        
        self.card_lay.addWidget(self.gallery_label)
        self.card_lay.addWidget(self.gallery_warn)
        self.card_lay.addSpacing(5)
        self.card_lay.addWidget(self.gallery_scroll)
        self.card_lay.addSpacing(30)
        self.card_lay.addWidget(self.reviews_label)
        self.card_lay.addSpacing(10)
        self.card_lay.addLayout(self.comments_container)
        self.card_lay.addStretch()

        scroll_layout.addWidget(self.card)
        detail_scroll.setWidget(detail_content)
        detail_layout.addWidget(detail_scroll)
        
        self.update_texts(self.tr)
        self.update_theme(self.is_dark)



    def set_placeholder_icon(self, letter):
        from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
        from PySide6.QtCore import Qt
        pixmap = QPixmap(120, 120)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#0071E3"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 120, 120, 24, 24)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("SF Pro Display", 48, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, letter)
        painter.end()
        self.icon_lab.setStyleSheet("background-color: transparent;")
        self.icon_lab.setPixmap(pixmap)

    def prepare_view(self, data):
        self.current_app_data = data
        self.name_lab.setText(data['name'])
        self.desc_lab.setText(data['desc'])
        self.size_lab.setText("")
        self.stars_lab.setText("")
        self.set_placeholder_icon(data['name'][0].upper())
        self.source_selector.clear()
        
        if data.get('has_pacman'): self.source_selector.addItem("Repositorios (Pacman)", "pacman")
        if data.get('has_aur'): self.source_selector.addItem("AUR (Comunidad)", "aur")
        
        if self.source_selector.count() > 0:
            self.source_selector.setCurrentIndex(0)
            
        is_active_install = (self.active_install_pkg == data['name'])
        
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

    def update_ui(self, detailed_data):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        
        self.detail_spinner.stop()
        self.current_app_data.update(detailed_data)
        
        for i in reversed(range(self.gallery_container_lay.count())):
            widget = self.gallery_container_lay.itemAt(i).widget()
            if widget: widget.deleteLater()
            
        screenshots = detailed_data.get("screenshots", [])
        if screenshots:
            self.gallery_label.show()
            self.gallery_warn.show()
            self.gallery_scroll.show()
            self.main_window.gallery_worker.load(screenshots)
        else:
            self.gallery_label.hide()
            self.gallery_warn.hide()
            self.gallery_scroll.hide()

        if "size" in detailed_data: self.size_lab.setText(self.tr("size_est").format(detailed_data['size']))
        
        if detailed_data.get('official_url'):
            self.web_btn.setText(" " + self.tr("official_web"))
            try: self.web_btn.clicked.disconnect() 
            except Exception: pass
            self.web_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(detailed_data['official_url'])))
            self.web_btn.show()
            
        if detailed_data.get('source_url'):
            self.source_btn.setText(" " + self.tr("pkg_source"))
            try: self.source_btn.clicked.disconnect() 
            except Exception: pass
            self.source_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(detailed_data['source_url'])))
            self.source_btn.show()

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

    def add_comment(self, user, text):
        from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
        from PySide6.QtGui import QFont
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

    def on_install_clicked(self):
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
            
        self.install_requested.emit(action, source_type, pkg)

    def on_check_app_clicked(self):
        self.check_app_btn.setEnabled(False)
        self.check_app_btn.setText("Buscando..." if self.app_settings.get("lang",1)==0 else "Searching...")
        self.check_app_requested.emit(self.current_app_data['name'])

    def on_app_update_checked(self, has_up, ver):
        if has_up:
            self.check_app_btn.hide()
            self.update_app_btn.setText(f"{self.tr('update_btn')} (v{ver})")
            self.update_app_btn.show()
        else:
            self.check_app_btn.setText(self.tr("app_updated"))

    def on_update_app_clicked(self):
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
            
        self.install_requested.emit("update_app", source_type, pkg)

    def on_launch_clicked(self):
        self.launch_requested.emit(self.current_app_data.get("name", ""))

    def update_texts(self, tr_func):
        self.back_btn.setText(f" {tr_func('back_btn')}")
        self.reviews_label.setText(tr_func("comm_info"))
        self.gallery_label.setText("Galería de Imágenes" if self.app_settings.get("lang", 1) == 0 else "Image Gallery")
        self.gallery_warn.setText("Nota: Imágenes extraídas de Flathub. Pueden diferir del empaquetado AUR." if self.app_settings.get("lang", 1) == 0 else "Note: Images provided by Flathub. May differ from AUR package.")
        self.cancel_install_btn.setText(tr_func("cancel_btn"))
        
        if self.install_btn.text() in ["Obtener", "Get"]: self.install_btn.setText(tr_func("get_btn"))
        if self.install_btn.text() in ["Desinstalar", "Uninstall"]: self.install_btn.setText(tr_func("uninstall_btn"))
        self.open_btn.setText(tr_func("open_btn"))
        if self.check_app_btn.text() in ["Buscar actualización", "Check for update"]: self.check_app_btn.setText(tr_func("check_up_btn"))
        if self.check_app_btn.text() in ["Actualizado", "Up to date"]: self.check_app_btn.setText(tr_func("app_updated"))

    def update_theme(self, is_dark):
        from utils import get_ui_icon
        self.is_dark = is_dark
        self.back_btn.setIcon(get_ui_icon("back", is_dark))
        if hasattr(self, 'detail_spinner') and self.detail_spinner: self.detail_spinner.update_theme(is_dark)
        if hasattr(self, 'pacman_anim') and self.pacman_anim: self.pacman_anim.update_theme(is_dark)



class SetupPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        from PySide6.QtWidgets import QVBoxLayout, QLabel
        from PySide6.QtGui import QFont
        from PySide6.QtCore import Qt
        from widgets import LoadingSpinner
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("MainBg")
        
        setup_lay = QVBoxLayout(self)
        setup_lay.setAlignment(Qt.AlignCenter)
        
        self.setup_spinner = LoadingSpinner(size=64)
        self.setup_spinner.start()
        
        self.setup_lbl = QLabel()
        self.setup_lbl.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        self.setup_lbl.setAlignment(Qt.AlignCenter)
        
        setup_lay.addWidget(self.setup_spinner, alignment=Qt.AlignCenter)
        setup_lay.addSpacing(20)
        setup_lay.addWidget(self.setup_lbl)

    def set_status(self, tr_func, text_key=None, raw_text=None):
        if raw_text:
            self.setup_lbl.setText(raw_text)
        elif text_key:
            self.setup_lbl.setText(tr_func(text_key))

    def update_theme(self, is_dark):
        self.setup_spinner.update_theme(is_dark)