import os
import json

def adjust_color_brightness(hex_color, amount):
    """Ajusta el brillo de un color HEX. amount puede ser positivo o negativo."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6: return "#" + hex_color
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return "#" + hex_color

def get_stylesheet(is_dark=True):
    # Valores por defecto de RubiAUR
    if is_dark:
        bg_main = "#000000"
        bg_header = "#1D1D1F"
        bg_card = "#1C1C1E"
        bg_card_hover = "#2C2C2E"
        accent = "#0A84FF"
        text_main = "#FFFFFF"
        text_secondary = "#8E8E93"
        border_color = "rgba(255,255,255,0.05)"
        border_light = "rgba(255,255,255,0.1)"
        danger = "#FF453A"
        danger_bg = "#2C2C2E"
        danger_bg_hover = "#3A1A1A"
        input_bg = "#2C2C2E"
        input_hover = "#3A3A3C"
        active_btn_bg = "#1A2A40"
    else:
        bg_main = "#F5F5F7"
        bg_header = "#FFFFFF"
        bg_card = "white"
        bg_card_hover = "#F2F2F7"
        accent = "#0071E3"
        text_main = "#1D1D1F"
        text_secondary = "#8E8E93"
        border_color = "rgba(0,0,0,0.05)"
        border_light = "rgba(0,0,0,0.1)"
        danger = "#FF3B30"
        danger_bg = "#F2F2F7"
        danger_bg_hover = "#FFE5E5"
        input_bg = "#E8E8ED"
        input_hover = "#D1D1D6"
        active_btn_bg = "#E6F0FF"

    # Intentar cargar colores dinámicos de Pywal
    wal_path = os.path.expanduser("~/.cache/wal/colors.json")
    if os.path.exists(wal_path):
        try:
            with open(wal_path, "r", encoding="utf-8") as f:
                wal_colors = json.load(f)
            
            # Usar color de acento principal (color4 es azul, pero color2 o color6 también son populares. Usamos color4 por defecto).
            accent = wal_colors["colors"].get("color4", accent)
            
            # En modo oscuro, adaptamos el fondo
            if is_dark:
                wal_bg = wal_colors["special"].get("background", bg_main)
                bg_main = wal_bg
                bg_header = adjust_color_brightness(bg_main, 10)
                bg_card = adjust_color_brightness(bg_main, 15)
                bg_card_hover = adjust_color_brightness(bg_main, 25)
                input_bg = bg_card_hover
                input_hover = adjust_color_brightness(bg_main, 35)
                active_btn_bg = adjust_color_brightness(bg_main, 20)
                
        except Exception:
            pass
            
    # Plantilla de CSS
    template = f"""
    QMainWindow, #CentralWidget, #MainBg {{ background-color: {bg_main}; }}
    #Header {{ background-color: {bg_header}; border-bottom: 1px solid {border_color}; }}
    #AppCard, #ListContainer {{ background-color: {bg_card}; border-radius: 20px; border: 1px solid {border_color}; }}
    #HomeCard {{ background-color: {bg_card}; border-radius: 16px; border: 1px solid {border_color}; }}
    #HomeCard:hover {{ background-color: {bg_card_hover}; }}
    .ActionBtn {{ font-weight: bold; font-size: 14px; border-radius: 16px; padding: 0px 20px; border: none; }}
    #InstallBtn {{ background-color: {accent}; color: white; }}
    #UninstallBtn {{ background-color: {danger_bg}; color: {danger}; }}
    #BackBtn {{ background-color: transparent; color: {accent}; font-weight: bold; font-size: 14px; text-align: left; border: none; }}
    #BackBtn:hover {{ text-decoration: underline; }}
    #LogoBtn {{ background-color: transparent; color: {text_main}; font-size: 20px; font-weight: bold; text-align: left; border: none; padding: 6px 12px; border-radius: 12px;}}
    #LogoBtn:hover {{ background-color: {bg_card_hover}; }}
    #LogoBtn[active="true"] {{ background-color: {active_btn_bg}; color: {accent}; }}
    #HeaderActionBtn {{ background-color: transparent; color: {accent}; font-size: 14px; font-weight: bold; border: none; padding: 8px 15px; border-radius: 12px; }}
    #HeaderActionBtn:hover {{ background-color: {bg_card_hover}; }}
    #HeaderActionBtn[active="true"] {{ background-color: {active_btn_bg}; color: {accent}; }}
    #IconBtn {{ background-color: transparent; border: none; border-radius: 12px; }}
    #IconBtn:hover {{ background-color: {bg_card_hover}; }}
    #IconBtn[active="true"] {{ background-color: {active_btn_bg}; }}
    #CategoryTitleBtn {{ text-align: left; font-size: 22px; font-weight: bold; background: transparent; border: none; padding: 5px 0px; margin: 0; color: {text_main}; }}
    #CategoryTitleBtn:hover {{ color: {accent}; }}
    #ListItem {{ background-color: {bg_card}; border-radius: 12px; border: none; border-bottom: 1px solid {border_color}; }}
    #ListItem:hover {{ background-color: {bg_card_hover}; }}
    QComboBox {{ background-color: {bg_card_hover}; color: {text_main}; border-radius: 12px; padding: 0px 15px; font-weight: bold; border: none; }}
    QComboBox:hover {{ background-color: {input_hover}; }}
    QComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox QAbstractItemView {{ background-color: {bg_card}; border: 1px solid {border_light}; selection-background-color: {bg_card_hover}; selection-color: {accent}; outline: none; }}
    QComboBox QAbstractItemView::item {{ min-height: 35px; padding: 0px 10px; }}
    QScrollArea {{ border: none; background-color: transparent; }}
    QLabel {{ color: {text_main}; }} 
    QLineEdit {{ background-color: {input_bg}; color: {text_main}; border-radius: 12px; padding: 10px; border: none; }}
    #ReviewBox {{ background-color: {bg_card_hover}; border-radius: 12px; padding: 15px; }}
    #SeparatorLine {{ background-color: {border_color}; border: none; }}
    #SearchPopup {{ background-color: {bg_card}; border-radius: 12px; border: 1px solid {border_light}; padding: 5px; outline: none; }}
    #SearchPopup::item {{ padding: 8px 12px; border-radius: 8px; font-size: 14px; color: {text_main}; }}
    #SearchPopup::item:hover {{ background-color: {bg_card_hover}; }}
    #SearchPopup::item:disabled {{ background-color: transparent; color: {text_secondary}; font-weight: bold; font-size: 12px; padding-top: 15px; }}
    #CancelBtn {{ background-color: {danger_bg_hover}; color: {danger}; border-radius: 16px; padding: 0px 20px; font-weight: bold;}}
    #CancelBtn:hover {{ background-color: {danger_bg}; }}
    #LoadMoreBtn {{ background-color: {input_bg}; color: {text_main}; border-radius: 18px; font-weight: bold; font-size: 14px; padding: 12px; }}
    #LoadMoreBtn:hover {{ background-color: {input_hover}; }}
    """
    return template
