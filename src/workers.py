import subprocess
import requests

import concurrent.futures
import re
import os
import glob
from PySide6.QtCore import QObject, Signal, QThreadPool
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
                proc = subprocess.run(['pacman', '-Ssq', query_clean], capture_output=True, text=True)
                if proc.returncode == 0: pacman_pkgs = set(p for p in proc.stdout.strip().split('\n') if p)
            except: pass
            try:
                url = f"https://aur.archlinux.org/rpc/?v=5&type=search&by=name&arg={query_clean}"
                res = requests.get(url, timeout=5).json()
                if res.get('results'):
                    aur_pkgs = set(item['Name'] for item in res['results'])
            except: pass
            
            all_pkgs = pacman_pkgs.union(aur_pkgs)
            combined = []
            for pkg in all_pkgs:
                combined.append({"name": pkg, "has_pacman": pkg in pacman_pkgs, "has_aur": pkg in aur_pkgs})
                
            def sort_logic(x):
                name = x["name"].lower()
                if name == query_clean: return 0
                if name in [f"{query_clean}-bin", f"{query_clean}-git", f"{query_clean}-stable", f"{query_clean}-desktop"]: return 1
                if name.startswith(f"{query_clean}-"): return 2
                if f"-{query_clean}-" in name or name.endswith(f"-{query_clean}"): return 3
                if name.startswith(query_clean): return 4
                if query_clean in name: return 5
                return 6
                
            combined.sort(key=lambda x: (sort_logic(x), len(x["name"]), x["name"]))
            self.results_ready.emit(combined[:10], query)
        QThreadPool.globalInstance().start(run)

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
        QThreadPool.globalInstance().start(run)

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
        QThreadPool.globalInstance().start(run)

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
                elif action == "clean_sys": cmd = [aur_backend, "-c" if aur_backend == "paru" else "-Yc", "--noconfirm", "--sudo", "pkexec"]
                
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
        QThreadPool.globalInstance().start(execute)

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
        QThreadPool.globalInstance().start(run)

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
                res = requests.get(url, timeout=5).json()
                if res.get('results'):
                    for item in res['results']:
                        name = item['Name']
                        if name in results:
                            results[name]["has_aur"] = True
                            if not results[name]["has_pacman"]: results[name]["desc"] = item.get('Description', 'Sin descripción')
                            results[name]["votes"] = item.get('NumVotes', 0)
            except: pass
            self.finished.emit([results[app] for app in app_list], cat_name)
        QThreadPool.globalInstance().start(run)

CURATED_SCREENSHOTS = {
    "kdenlive": [
        "https://kdenlive.org/wp-content/uploads/2024/04/kdenlive-24.04-main.png"
    ],
    "onlyoffice": [
        "https://www.onlyoffice.com/images/desktop/new-interface/hero_image_new.png?v=1"
    ],
    "obs-studio": ["https://obsproject.com/assets/images/home_screen.webp"],
    "gimp": ["https://www.gimp.org/images/frontpage/gimp-3.0-rc1-screenshot.jpg"],
    "vlc": ["https://images.sftcdn.net/images/t_app-cover-l,f_auto/p/c167d446-96d0-11e6-b636-00163ed833e7/3576356784/vlc-media-player-screenshot.png"],
    "blender": ["https://www.blender.org/wp-content/uploads/2020/12/blender-startup-1.jpg"],
    "inkscape": ["https://media.inkscape.org/media/doc/release_notes/1.3/Inkscape_1-3_Shape_builder_tool.png"],
    "libreoffice-fresh": ["https://es.libreoffice.org/assets/Uploads/Discover/LO-7.0-Start-Center-macOS.png"],
    "libreoffice-still": ["https://es.libreoffice.org/assets/Uploads/Discover/LO-7.0-Start-Center-macOS.png"],
    "krita": ["https://krita.org/en/wp-content/uploads/2018/03/krita_3.0_default.png"],
    "steam": ["https://store.cloudflare.steamstatic.com/public/shared/images/responsive/share_steam_logo.png"],
    "discord": ["https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"]
}

class IconWorker(QObject):
    icon_data_ready = Signal(str, bytes)
    def load_icons(self, apps_list):
        def fetch_single(app_name):
            icon_url = None
            try:
                flathub_search = requests.post("https://flathub.org/api/v2/search", json={"query": search_term}, timeout=5).json()
                if flathub_search.get("hits") and len(flathub_search["hits"]) > 0:
                    icon_url = flathub_search["hits"][0].get("icon")
            except: pass
            
            if not icon_url:
                try:
                    res = requests.get(f"https://itunes.apple.com/search?term={search_term}&entity=macSoftware&limit=1", timeout=5).json()
                    if res['resultCount'] == 0:
                        res = requests.get(f"https://itunes.apple.com/search?term={search_term}&entity=software&limit=1", timeout=5).json()
                    if res['resultCount'] > 0:
                        track_name = res['results'][0].get('trackName', '').lower()
                        term_words = search_term.lower().split()
                        if term_words and any(word in track_name for word in term_words if len(word) > 2) or (term_words and term_words[0] in track_name):
                            icon_url = res['results'][0]['artworkUrl100'].replace('100x100', '256x256')
                except: pass
            if icon_url:
                try:
                    img_data = requests.get(icon_url, timeout=5).content
                    self.icon_data_ready.emit(app_name, img_data)
                except: pass
        def run():
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(fetch_single, apps_list)
        QThreadPool.globalInstance().start(run)

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
                res = requests.get(f"https://aur.archlinux.org/rpc/?v=5&type=search&arg={query_clean}", timeout=5).json()
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
                if name in [f"{query_clean}-bin", f"{query_clean}-git", f"{query_clean}-stable", f"{query_clean}-desktop"]: return 1
                if name.startswith(f"{query_clean}-"): return 2
                if f"-{query_clean}-" in name or name.endswith(f"-{query_clean}"): return 3
                if name.startswith(query_clean): return 4
                if query_clean in name: return 5
                return 6
                
            result_list.sort(key=lambda x: (sort_key(x), -x.get('votes', 0)))
            self.finished.emit(result_list[:30])
        QThreadPool.globalInstance().start(run)

class DetailWorker(QObject):
    finished = Signal(dict)
    def load_details(self, app_data):
        def run():
            name = app_data['name']
            check = subprocess.run(['pacman', '-Qq', name], capture_output=True)
            app_data["is_installed"] = (check.returncode == 0)

            app_data["icon_url"] = None
            app_data["official_url"] = "" 
            app_data["source_url"] = ""   
            app_data["screenshots"] = []
            app_data["size"] = "Variable"
            app_data["comments"] = []
            
            search_term = name.replace("-bin", "").replace("-git", "").replace("-launcher", "").replace("-desktop", "").replace("-", " ")
            
            import concurrent.futures

            def fetch_media():
                try:
                    flathub_search = requests.post("https://flathub.org/api/v2/search", json={"query": search_term}, timeout=4).json()
                    if flathub_search.get("hits") and len(flathub_search["hits"]) > 0:
                        app_id = flathub_search["hits"][0]["app_id"]
                        app_data["icon_url"] = flathub_search["hits"][0].get("icon")
                        
                        appstream = requests.get(f"https://flathub.org/api/v2/appstream/{app_id}", timeout=4).json()
                        if "screenshots" in appstream and appstream["screenshots"]:
                            for s in appstream["screenshots"]:
                                if "sizes" in s and s["sizes"]:
                                    app_data["screenshots"].append(s["sizes"][0]["src"])
                                    if len(app_data["screenshots"]) >= 5: break
                except: pass
                
                if not app_data["screenshots"]:
                    try:
                        itunes_url_mac = f"https://itunes.apple.com/search?term={search_term}&entity=macSoftware&limit=1"
                        res = requests.get(itunes_url_mac, timeout=4).json()
                        if res['resultCount'] == 0:
                            itunes_url = f"https://itunes.apple.com/search?term={search_term}&entity=software&limit=1"
                            res = requests.get(itunes_url, timeout=4).json()
                        
                        if res['resultCount'] > 0: 
                            track_name = res['results'][0].get('trackName', '').lower()
                            term_words = search_term.lower().split()
                            if term_words and any(word in track_name for word in term_words if len(word) > 2) or (term_words and term_words[0] in track_name):
                                if not app_data.get("icon_url"):
                                    app_data["icon_url"] = res['results'][0]['artworkUrl100'].replace('100x100', '256x256')
                                app_data["screenshots"] = res['results'][0].get('screenshotUrls', [])
                    except: pass

            def fetch_pacman():
                if app_data['has_pacman']:
                    try:
                        proc = subprocess.run(['pacman', '-Si', name], capture_output=True, text=True)
                        lines = proc.stdout.split('\n')
                        app_data["size"] = next((l for l in lines if 'Tamaño' in l or 'Installed Size' in l), "Size: ").split(': ', 1)[-1]
                        
                        for line in lines:
                            if line.startswith('URL'):
                                app_data["official_url"] = line.split(': ', 1)[-1].strip()
                                break
                        app_data["source_url"] = f"https://archlinux.org/packages/?q={name}"
                    except: pass

            def fetch_aur():
                if app_data['has_aur']:
                    try:
                        res = requests.get(f"https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={name}", timeout=4).json()
                        if res.get('results'):
                            if not app_data.get("official_url"):
                                app_data["official_url"] = res['results'][0].get('URL', '')
                        
                        app_data["source_url"] = f"https://aur.archlinux.org/packages/{name}"
                        aur_page = requests.get(app_data["source_url"], timeout=4).text
                        matches = re.findall(r'<div class="article-content">\s*<p>(.*?)</p>\s*</div>', aur_page, re.IGNORECASE | re.DOTALL)
                        if matches: app_data["comments"] = [re.sub(r'<[^>]+>', '', m).strip() for m in matches[:2]]
                    except: pass

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                t1 = executor.submit(fetch_media)
                t2 = executor.submit(fetch_pacman)
                t3 = executor.submit(fetch_aur)
                concurrent.futures.wait([t1, t2, t3])
                
            self.finished.emit(app_data)
        QThreadPool.globalInstance().start(run)

class AurInstallerWorker(QObject):
    finished = Signal(bool, str)
    
    def run(self):
        def execute():
            try:
                build_dir = os.path.expanduser("~/.cache/rubiaur_yay_build")
                repo_url = "https://aur.archlinux.org/yay-bin.git"
                
                proc1 = subprocess.run(["pkexec", "pacman", "-Syu", "--needed", "--noconfirm", "base-devel", "git"], capture_output=True, text=True)
                if proc1.returncode != 0: raise Exception(f"Pacman: {proc1.stderr}")
                
                subprocess.run(["rm", "-rf", build_dir])
                proc2 = subprocess.run(["git", "clone", repo_url, build_dir], capture_output=True, text=True)
                if proc2.returncode != 0: raise Exception(f"Git: {proc2.stderr}")
                
                env = os.environ.copy()
                env["PACMAN_AUTH"] = "pkexec"
                proc3 = subprocess.run(["makepkg", "-s", "--noconfirm"], cwd=build_dir, env=env, capture_output=True, text=True)
                if proc3.returncode != 0: raise Exception(f"Makepkg: {proc3.stdout}")
                
                pkg_files = glob.glob(os.path.join(build_dir, "*.pkg.tar.zst"))
                if not pkg_files: raise Exception(f"El paquete no se generó. Log: {proc3.stdout}")
                
                proc4 = subprocess.run(["pkexec", "pacman", "-U", "--noconfirm", pkg_files[0]], capture_output=True, text=True)
                if proc4.returncode != 0: raise Exception(f"Instalación final: {proc4.stderr}")
                
                self.finished.emit(True, "Yay instalado correctamente")
            except Exception as e:
                self.finished.emit(False, str(e))
                
        QThreadPool.globalInstance().start(execute)

class SelfUpdateWorker(QObject):
    result = Signal(bool, str, str) 
    
    def check(self, current_version):
        def run():
            try:
                url = "https://api.github.com/repos/cesarmoralesb20005-ctrl/RubiAUR/releases/latest"
                res = requests.get(url, timeout=5).json()
                latest_ver = res.get("tag_name", "0.0.0").replace("v", "")
                link = res.get("html_url", "")
                
                if latest_ver > current_version.replace("v", ""):
                    self.result.emit(True, latest_ver, link)
                else:
                    self.result.emit(False, latest_ver, link)
            except Exception:
                self.result.emit(False, "", "")
                
        QThreadPool.globalInstance().start(run)
class GalleryWorker(QObject):
    image_ready = Signal(bytes)
    
    def load(self, urls):
        def run():
            import requests # double check
            for url in urls[:5]:
                try:
                    img_data = requests.get(url, timeout=5).content
                    self.image_ready.emit(img_data)
                except: pass
        QThreadPool.globalInstance().start(run)
