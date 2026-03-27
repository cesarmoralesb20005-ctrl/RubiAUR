🌍 Read this in: [Español](README.md) | [English](README-en.md)

---

# 💎 RubiAUR

**The most elegant way to manage your Arch Linux system.**

RubiAUR is a graphical app store and package manager built with Python and PySide6. Meticulously designed to deliver a premium, fluid, and visually appealing experience, unifying the power of `pacman` and the AUR ecosystem (`yay` / `paru`) into a single modern interface.

![RubiAUR Screenshot](home.png) 

## ✨ Key Features

* 🚀 **Premium & Responsive UI:** Liquid design that adapts perfectly to everything from laptop screens to 4K monitors. Fluid animations, smooth transitions, and zero freezes.
* 📦 **All your software in one place:** Browse a curated catalog by category, or use the smart real-time auto-completion search to find official packages or community ones (AUR).
* 🎨 **Dynamic Themes:** Native support for Dark Mode, Light Mode, and Auto. Vector icons are drawn mathematically, ensuring they never pixelate.
* ⚙️ **Total System Control:** * Install and uninstall applications with one click.
  * Search for and apply system-wide updates.
  * Built-in tool to safely clear cache and remove orphaned dependencies.
* 📊 **Detailed Insights:** Get descriptions, estimated package sizes, dynamically fetched app icons, and community comments for AUR packages.
* 🪄 **Welcome Wizard & Visual Installer:** Configure your preferences (language, theme, backend) on first launch. Includes a graphical installer to integrate the application into your system menu without touching the terminal.

## 📥 Installation (Recommended)

The easiest way to use RubiAUR is through the pre-compiled package which includes our graphical installation wizard.

1. Go to the **[Releases](../../releases)** section and download the compressed archive of the latest version.
2. Extract the contents into a folder.
3. Open your terminal in that folder and run the visual installer:
   ```bash
   chmod +x installer
   ./installer
4. Si las aplicaciones de aur no se instalan asegúrate de tener instalado yay o paru:
   instala git desde la app RubiAUR
   ```bash
   git clone https://aur.archlinux.org/yay.git
   cd yay
   makepkg -si
4. If the apps from AUR doesn't work/install,make sure you have yay or paru:
   install git from RubiAUR
   ```bash
   git clone https://aur.archlinux.org/yay.git
   cd yay
   makepkg -si
 
🌎 Languages

    Currently, the RubiAUR store only supports Spanish, but future updates will implement: Français, Deutsch & English, with the latter being the next to be added. We appreciate your patience. :)