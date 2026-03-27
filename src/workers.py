import subprocess
import requests
import threading
import concurrent.futures
import re
from PySide6.QtCore import QObject, Signal
from constantes import HOME_CATEGORIES

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



# --- TRABAJADOR INSTALADOR YAY ---
class AurInstallerWorker(QObject):
    finished = Signal(bool, str)
    
    def run(self):
        def execute():
            try:
                import os 
                import subprocess
                import glob
                
                build_dir = os.path.expanduser("~/.cache/rubiaur_yay_build")
                repo_url = "https://aur.archlinux.org/yay-bin.git"
                
                # 1. Instalar dependencias (atrapando el error si pacman falla)
                proc1 = subprocess.run(["pkexec", "pacman", "-Syu", "--needed", "--noconfirm", "base-devel", "git"], capture_output=True, text=True)
                if proc1.returncode != 0:
                    raise Exception(f"Pacman: {proc1.stderr}")
                
                # 2. Clonar repo
                subprocess.run(["rm", "-rf", build_dir])
                proc2 = subprocess.run(["git", "clone", repo_url, build_dir], capture_output=True, text=True)
                if proc2.returncode != 0:
                    raise Exception(f"Git: {proc2.stderr}")
                
                # 3. Compilar paquete
                env = os.environ.copy()
                env["PACMAN_AUTH"] = "pkexec"
                proc3 = subprocess.run(["makepkg", "-s", "--noconfirm"], cwd=build_dir, env=env, capture_output=True, text=True)
                if proc3.returncode != 0:
                    raise Exception(f"Makepkg: {proc3.stderr}")
                
                # 4. Encontrar e instalar el paquete
                pkg_files = glob.glob(os.path.join(build_dir, "*.pkg.tar.zst"))
                if not pkg_files:
                    raise Exception(f"El paquete no se generó. Log: {proc3.stdout}")
                
                proc4 = subprocess.run(["pkexec", "pacman", "-U", "--noconfirm", pkg_files[0]], capture_output=True, text=True)
                if proc4.returncode != 0:
                    raise Exception(f"Instalación final: {proc4.stderr}")
                
                self.finished.emit(True, "Yay instalado correctamente")
            except Exception as e:
                # Emitimos el error EXACTO para que la ventana principal lo muestre
                self.finished.emit(False, str(e))
                
        threading.Thread(target=execute).start()



# --- TRABAJADOR PARA ACTUALIZACIONES DE RUBIAUR (GITHUB) ---
class SelfUpdateWorker(QObject):
    # Devuelve: ¿Hay actualización?, Versión nueva, Link de descarga
    result = Signal(bool, str, str) 
    
    def check(self, current_version):
        def run():
            try:
                # Reemplaza con tu usuario y repositorio de GitHub
                url = "https://api.github.com/repos/cesarmoralesb20005-ctrl/RubiAUR/releases/latest"
                res = requests.get(url, timeout=3).json()
                
                # Obtenemos la versión (ej. "v1.0.1") y le quitamos la "v" para comparar
                latest_ver = res.get("tag_name", "0.0.0").replace("v", "")
                link = res.get("html_url", "")
                
                # Comparamos si la versión de GitHub es mayor a la actual
                if latest_ver > current_version.replace("v", ""):
                    self.result.emit(True, latest_ver, link)
                else:
                    self.result.emit(False, latest_ver, link)
            except Exception:
                # Si no hay internet o falla, simplemente decimos que no hay actualizaciones
                self.result.emit(False, "", "")
                
        threading.Thread(target=run).start()