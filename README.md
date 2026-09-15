<p align="center">
  <img src="icon.png" width="160" height="160" alt="Running Races Home Assistant Icon" />
</p>

# Regional Running Races & Trails for Home Assistant 🏅📅

[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/lediabloteur)

A Home Assistant integration powered by **Miles Republic** (`milesrepublic.com`) that automatically discovers and syncs upcoming official running, trail, triathlon, walking, obstacle, and cycling competitions into Home Assistant.

---

## ✨ Features
- 🌐 **Live Miles Republic Sync**: Automatically queries official event databases in real-time.
- 📍 **Multi-Department Filtering**: Select one or multiple French departments (e.g. 86 - Vienne, 79 - Deux-Sèvres, 37 - Indre-et-Loire, etc.).
- 🏃 **Discipline Selection**: Filter by Running, Trail, Marche / Rando, Triathlon / Duathlon, Vélo / Gravel, and Course d'obstacles.
- 📅 **Native Calendar (`calendar.courses_trails_...`)**: Displays all scheduled events with start times, distances, elevation gain, prices, and direct registration links.
- 🎯 **Next Race Sensor (`sensor.prochaine_course_officielle`)**: Countdown in days, next event name, location, and a complete list of upcoming races in `attributes.races` for rich Lovelace cards.
- ⚙️ **Full UI Configuration & Options Flow**: Modify your departments and sports choices at any time directly in Home Assistant.

---

## 🚀 Installation via HACS

1. In Home Assistant, open **HACS** > **Integrations** > **Custom repositories**.
2. Add this repository URL (`https://github.com/lediabloteur/ha-running-races`) with category **Integration**.
3. Download and restart Home Assistant if prompted.
4. Go to **Settings** > **Devices & Services** > **Add Integration** > search for **Regional Running Races & Trails**.
5. Select your department(s) and sports, and submit!

---

## ☕ Support the Project

If this integration helps you discover new races and trails in your region, consider supporting the project!

<p align="left">
  <a href="https://buymeacoffee.com/lediabloteur" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="180" />
  </a>
</p>

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** - see the [LICENSE](LICENSE) file for details.
