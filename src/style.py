LIGHT_STYLE = """
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

DARK_STYLE = """
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
