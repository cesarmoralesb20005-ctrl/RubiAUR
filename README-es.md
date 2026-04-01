🌍 Leer en: [English](README.md) | [Español](README-es.md) 

---

<p align="center">
  <img src="LOGO.svg" width="450" alt="Logo de RubiAUR">
</p>

# 💎 RubiAUR
![Version](https://img.shields.io/badge/version-1.3-blue.svg)
![Arch Linux](https://img.shields.io/badge/OS-Arch%20Linux-1793D1?logo=arch-linux&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-F6D220?logo=python&logoColor=1D1D1F)

**La forma más elegante de gestionar tu sistema Arch Linux.**

RubiAUR es una tienda de aplicaciones gráfica y gestor de paquetes construido con Python y PySide6. Diseñado meticulosamente para ofrecer una experiencia premium, fluida y visualmente atractiva, unificando el poder de `pacman` y el ecosistema AUR (`yay` / `paru`) en una sola interfaz moderna.

![Pantalla de inicio de RubiAUR](home.png) 

## ✨ Características Principales

* 🚀 **Interfaz Premium y Responsiva:** Diseño líquido que se adapta perfectamente desde pantallas de laptops hasta monitores 4K. Animaciones fluidas, transiciones suaves y cero congelamientos.
* 📦 **Todo tu software en un solo lugar:** Explora un catálogo seleccionado por categorías, o usa la búsqueda inteligente con autocompletado en tiempo real para encontrar paquetes oficiales o de la comunidad (AUR).
* 🖼️ **Galería de Aplicaciones (¡Nuevo en v1.3!):** Previsualiza visualmente el software antes de instalarlo. RubiAUR obtiene dinámicamente capturas de pantalla oficiales y metadatos directamente de la API de Flathub/AppStream.
* 🎨 **Temas Dinámicos:** Soporte nativo para Modo Oscuro, Modo Claro y Automático. Los íconos vectoriales se dibujan matemáticamente, asegurando que nunca se pixelen.
* ⚙️ **Control Total del Sistema:** * Instala y desinstala aplicaciones con un solo clic.
  * Busca y aplica actualizaciones de todo el sistema.
  * Herramienta integrada para limpiar la caché de forma segura y eliminar dependencias huérfanas.
* 🪄 **Instalador y Configuración Inteligente:** Configura tus preferencias (idioma, tema, backend) en el primer inicio. Si no tienes un ayudante de AUR instalado, RubiAUR automáticamente preparará e instalará `yay` por ti en segundo plano.

![Detalles de la aplicación RubiAUR](details.png)

## 📥 Instalación (Recomendado)

La forma más sencilla de usar RubiAUR es a través del paquete AppImage precompilado, que incluye nuestro asistente de instalación gráfico.

1. Ve a la sección de **[Releases](../../releases)** y descarga el último `RubiAUR_Release.zip`.
2. Extrae el contenido en una carpeta.
3. Abre tu terminal en esa carpeta y ejecuta el instalador visual:
   ```bash
   chmod +x Instalar_RubiAUR
   ./Instalar_RubiAUR

🛠️ Compilar desde el código fuente

Si deseas ejecutar el código fuente directamente o contribuir al proyecto:
Bash

git clone [https://github.com/LoopedRacer9/RubiAUR.git](https://github.com/LoopedRacer9/RubiAUR.git)
cd RubiAUR
pip install -r requirements.txt
python src/main.py

🌎 Idiomas

Actualmente, la tienda RubiAUR está completamente traducida y soporta:

    🇪🇸 Español

    🇬🇧 Inglés

    🇫🇷 Francés

    🇩🇪 Alemán
