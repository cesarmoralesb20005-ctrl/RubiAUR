import re
import requests
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

SUSPICIOUS_PATTERNS = [
    (r'(?i)curl\s+.*\|\s*(bash|sh|zsh)', "Ejecución directa de script remoto vía curl"),
    (r'(?i)wget\s+.*\|\s*(bash|sh|zsh)', "Ejecución directa de script remoto vía wget"),
    (r'(?i)(curl|wget)\s+.*https?://(pastebin\.com|bit\.ly|tinyurl\.com|ngrok\.io|t\.co|raw\.githubusercontent\.com/[a-zA-Z0-9_-]+/(?!.*PKGBUILD))', "Descarga desde dominio acortador/anónimo"),
    (r'(?i)/etc/ld\.so\.preload', "Modificación de librerías precargadas del sistema (ld.so.preload)"),
    (r'(?i)~\/\.bashrc|~\/\.zshrc|/etc/profile', "Modificación de archivos de inicio del usuario/sistema"),
    (r'(?i)~\/\.config\/autostart|/etc/systemd/system/.*\.service', "Añadiendo programas de inicio automático no estándar"),
    (r'(?i)~\/\.ssh\/authorized_keys', "Añadiendo llaves SSH (Posible Backdoor)"),
    (r'(?i)crontab\s+', "Modificación de tareas programadas (Persistencia)"),
    (r'(?i)eval\s+\$', "Ejecución de código ofuscado (eval)"),
    (r'(?i)base64\s+-d\s*\|', "Decodificación y posible ejecución de código Base64"),
    (r'(?i)python3?\s+-c\s+.*(urllib|requests|base64|socket|subprocess)', "Payload malicioso de Python en línea"),
    (r'(?i)rm\s+-rf\s+(/|/\*|\$HOME|~\/|/\w+)', "Comando destructivo (rm -rf masivo)"),
    (r'(?i)chattr\s+\+i', "Haciendo archivos inmutables (típico de malware para evitar ser borrado)"),
    (r'(?i)chmod\s+(u\+s|\+s|4[0-9]{3})', "Asignación de permisos SUID (Escalada de privilegios)"),
    (r'(?i)nc\s+-e\s+/bin/(bash|sh)', "Creación de Reverse Shell (Netcat)"),
    (r'(?i)>\s*/dev/(sda|nvme|zero|random)', "Escritura directa a bloque de disco"),
    (r'(?i)source=\(.*http://.*\)', "Descarga de fuentes inseguras sin cifrar (http:// en lugar de https://)"),
]

class SecurityScannerSignals(QObject):
    finished = Signal(bool, list, str) # (is_clean, threats, pkgbuild_code)
    error = Signal(str)

class SecurityScannerWorker(QRunnable):
    """Worker que descarga de forma silenciosa el PKGBUILD de AUR y lo escanea en busca de malware."""
    
    def __init__(self, pkg_name):
        super().__init__()
        self.pkg_name = pkg_name
        self.signals = SecurityScannerSignals()
        
    @Slot()
    def run(self):
        try:
            threats = []
            code_buffer = ""
            
            # 1. Análisis de Reputación vía AUR RPC
            try:
                rpc_url = f"https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={self.pkg_name}"
                rpc_response = requests.get(rpc_url, timeout=5)
                if rpc_response.status_code == 200:
                    data = rpc_response.json()
                    if data.get("resultcount", 0) > 0:
                        pkg_info = data["results"][0]
                        votes = pkg_info.get("NumVotes", 0)
                        maintainer = pkg_info.get("Maintainer", None)
                        
                        if votes < 5:
                            threats.append(f"REPUTACIÓN: Paquete con muy pocos votos ({votes}). Podría ser malicioso o inestable.")
                        if not maintainer:
                            threats.append(f"REPUTACIÓN: Paquete HUÉRFANO (sin mantenedor oficial). Cualquiera podría haber inyectado código.")
            except Exception as e:
                pass # Ignorar fallos de reputación si la API falla
                
            # 2. Análisis del PKGBUILD
            url_pkgbuild = f"https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h={self.pkg_name}"
            response = requests.get(url_pkgbuild, timeout=10)
            if response.status_code != 200:
                self.signals.error.emit(f"No se pudo descargar el PKGBUILD (HTTP {response.status_code}).")
                return
                
            code_buffer += f"--- PKGBUILD ---\n{response.text}\n"
            
            # 3. Intento de Análisis del .install
            url_install = f"https://aur.archlinux.org/cgit/aur.git/plain/{self.pkg_name}.install?h={self.pkg_name}"
            install_response = requests.get(url_install, timeout=5)
            if install_response.status_code == 200:
                code_buffer += f"--- {self.pkg_name}.install ---\n{install_response.text}\n"
            
            # Buscar patrones en todo el código recolectado
            for idx, line in enumerate(code_buffer.split('\n')):
                for pattern, reason in SUSPICIOUS_PATTERNS:
                    if re.search(pattern, line):
                        threats.append(f"Línea {idx+1}: {reason}\nCódigo: {line.strip()}")
            
            is_clean = len(threats) == 0
            self.signals.finished.emit(is_clean, threats, code_buffer)
            
        except Exception as e:
            self.signals.error.emit(str(e))
