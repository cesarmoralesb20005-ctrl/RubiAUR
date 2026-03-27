import sys
import os
import shutil
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

class InstaladorRubiAUR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instalador de RubiAUR")
        self.setFixedSize(550, 400) # Un poco más alto para los botones
        self.setStyleSheet("""
            QMainWindow { background-color: #1D1D1F; }
            QLabel { color: #FFFFFF; }
            #Card { background-color: #2C2C2E; border-radius: 20px; }
            
            #InstalarBtn { background-color: #0A84FF; color: white; border-radius: 20px; font-weight: bold; font-size: 16px; padding: 12px; border: none; }
            #InstalarBtn:hover { background-color: #0071E3; }
            #InstalarBtn:disabled { background-color: #3A3A3C; color: #8E8E93; }
            
            #DesinstalarBtn { background-color: transparent; color: #FF453A; border-radius: 20px; font-weight: bold; font-size: 16px; padding: 10px; border: 2px solid #FF453A; }
            #DesinstalarBtn:hover { background-color: #FF453A; color: white; }
            #DesinstalarBtn:disabled { border-color: #3A3A3C; color: #8E8E93; }
        """)

        # Definir las rutas clave del sistema para instalar/desinstalar
        self.home = os.path.expanduser("~")
        self.bin_dir = os.path.join(self.home, ".local", "bin")
        self.icon_dir = os.path.join(self.home, ".local", "share", "icons")
        self.app_dir = os.path.join(self.home, ".local", "share", "applications")

        self.bin_destino = os.path.join(self.bin_dir, "rubiaur")
        self.logo_destino = os.path.join(self.icon_dir, "rubiaur-logo.svg")
        self.desktop_destino = os.path.join(self.app_dir, "RubiAUR.desktop")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedSize(450, 300)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Gestor RubiAUR")
        title.setFont(QFont("SF Pro Display", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        desc = QLabel("Instala RubiAUR en tu sistema para añadir el acceso\ndirecto al menú, o desinstálalo si ya no lo necesitas.")
        desc.setStyleSheet("color: #8E8E93; font-size: 14px;")
        desc.setAlignment(Qt.AlignCenter)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #34C759; font-size: 14px; font-weight: bold;")
        self.status_lbl.setAlignment(Qt.AlignCenter)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)

        self.btn_desinstalar = QPushButton("Desinstalar")
        self.btn_desinstalar.setObjectName("DesinstalarBtn")
        self.btn_desinstalar.setCursor(Qt.PointingHandCursor)
        self.btn_desinstalar.clicked.connect(self.ejecutar_desinstalacion)

        self.btn_instalar = QPushButton("Instalar / Actualizar")
        self.btn_instalar.setObjectName("InstalarBtn")
        self.btn_instalar.setCursor(Qt.PointingHandCursor)
        self.btn_instalar.clicked.connect(self.ejecutar_instalacion)

        btn_row.addWidget(self.btn_desinstalar)
        btn_row.addWidget(self.btn_instalar)

        card_layout.addWidget(title)
        card_layout.addSpacing(10)
        card_layout.addWidget(desc)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.status_lbl)
        card_layout.addSpacing(15)
        card_layout.addLayout(btn_row)

        main_layout.addWidget(card)

    def ejecutar_instalacion(self):
        self.btn_instalar.setEnabled(False)
        self.btn_desinstalar.setEnabled(False)
        self.btn_instalar.setText("Instalando...")
        QApplication.processEvents()

        # Asegurar que las carpetas existan
        os.makedirs(self.bin_dir, exist_ok=True)
        os.makedirs(self.icon_dir, exist_ok=True)
        os.makedirs(self.app_dir, exist_ok=True)

        # Nombres de archivos de origen
        bin_origen = "RubiAUR-x86_64.AppImage" # <--- ASEGÚRATE DE QUE SE LLAME ASÍ TU APPIMAGE
        logo_origen = "logo.svg"

        try:
            # 1. Copiar ejecutable
            if not os.path.exists(bin_origen):
                raise Exception(f"No se encontró {bin_origen}")
            shutil.copy(bin_origen, self.bin_destino)
            os.chmod(self.bin_destino, 0o755)

            # 2. Copiar logo
            if not os.path.exists(logo_origen):
                raise Exception(f"No se encontró {logo_origen}")
            shutil.copy(logo_origen, self.logo_destino)

            # 3. Crear .desktop
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=RubiAUR
Comment=Gestor elegante para Arch Linux
Exec={self.bin_destino}
Icon=rubiaur-logo
Terminal=false
Categories=System;Utility;Settings;
"""
            with open(self.desktop_destino, "w", encoding="utf-8") as f:
                f.write(desktop_content)
            os.chmod(self.desktop_destino, 0o755)

            self.status_lbl.setStyleSheet("color: #34C759; font-size: 14px; font-weight: bold;")
            self.status_lbl.setText("¡Instalación completada con éxito!")
            self.btn_instalar.setText("Cerrar")
            self.btn_instalar.clicked.disconnect()
            self.btn_instalar.clicked.connect(self.close)
            self.btn_instalar.setEnabled(True)

        except Exception as e:
            self.status_lbl.setStyleSheet("color: #FF453A; font-size: 14px; font-weight: bold;")
            self.status_lbl.setText("Error en la instalación.")
            print(f"Error detallado: {e}")
            self.btn_instalar.setText("Reintentar")
            self.btn_instalar.setEnabled(True)
            self.btn_desinstalar.setEnabled(True)

    def ejecutar_desinstalacion(self):
        self.btn_instalar.setEnabled(False)
        self.btn_desinstalar.setEnabled(False)
        self.btn_desinstalar.setText("Eliminando...")
        QApplication.processEvents()

        try:
            # Eliminar los archivos si existen
            if os.path.exists(self.bin_destino): 
                os.remove(self.bin_destino)
            if os.path.exists(self.logo_destino): 
                os.remove(self.logo_destino)
            if os.path.exists(self.desktop_destino): 
                os.remove(self.desktop_destino)

            self.status_lbl.setStyleSheet("color: #FF453A; font-size: 14px; font-weight: bold;")
            self.status_lbl.setText("¡RubiAUR fue desinstalado del sistema!")
            
            self.btn_desinstalar.setText("Cerrar")
            self.btn_desinstalar.clicked.disconnect()
            self.btn_desinstalar.clicked.connect(self.close)
            self.btn_desinstalar.setEnabled(True)

        except Exception as e:
            self.status_lbl.setStyleSheet("color: #FF453A; font-size: 14px; font-weight: bold;")
            self.status_lbl.setText("Error al desinstalar.")
            print(f"Error detallado: {e}")
            self.btn_desinstalar.setText("Reintentar")
            self.btn_instalar.setEnabled(True)
            self.btn_desinstalar.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstaladorRubiAUR()
    window.show()
    sys.exit(app.exec())