# Project Echo

### Developed by AEcoSpace — NASA International Space Apps Challenge 2025

---

## Overview

Echo is a web-based platform designed to integrate NASA Earth observation data with local socioeconomic indicators, enabling cities to plan for resilience and sustainability.

The system uses satellite and demographic datasets to visualize environmental risks — including air pollution, vegetation coverage, urban heat islands, and flood vulnerability — while correlating them with factors such as population density and income distribution.

By merging environmental and social data, Echo helps public managers, environmental agencies, and researchers identify vulnerabilities and prioritize interventions that promote healthier and more balanced cities.

---

## Challenge context

This project was developed for the NASA International Space Apps Challenge 2025, under the theme  
"Data pathways to healthy cities and human settlements."

The objective is to demonstrate how urban planners can leverage NASA Earth observation data to inform science-based decisions that protect both people and the environment.

---

## Team

| Name | Role | LinkedIn |
|------|------|-----------|
| Kaiki Nattan | Full stack developer | [linkedin.com/in/paulogomes](https://www.linkedin.com/in/kaikinattan) |
| Paulo Gomes | Front-end developer | [linkedin.com/in/paulotruly](https://www.linkedin.com/in/paulotruly) |
| Ester Santos | UX/UI designer | [linkedin.com/in/ester-hsnt](https://linkedin.com/in/ester-hsnt) |
| João Rafael | Front-end developer | [linkedin.com/in/joao-rafaell](https://linkedin.com/in/joao-rafaell) |
| Maximus Bragança | Team manager | [linkedin.com/in/maximus-bragança](https://linkedin.com/in/maximus-bragança) |

---

## Features

- Interactive geospatial dashboard for urban analytics  
- Dynamic filtering by region, population density, and income  
- Layer toggling for environmental indicators:
  - Air quality (OMI / TEMPO)
  - Green spaces (NDVI / MODIS)
  - Heat and urban temperature (ECOSTRESS)
  - Flood risk (SRTM + GPM)
- Correlative charts between environmental and social factors  
- AI-based recommendations for urban planning actions  
- NASA-inspired dark theme for clarity and accessibility  

---

## Data sources

- **NASA missions**
  - Aura OMI / TEMPO — Air quality
  - MODIS / NDVI — Vegetation coverage
  - ECOSTRESS — Urban heat and surface temperature
  - GPM + SRTM — Flood risk and topography
- **Socioeconomic data**
  - IBGE — Brazilian census data
  - SEDAC and WorldPop — Population density and income distribution
- **Cloud storage**
  - AWS S3 — Data storage and management

---

## Tech stack

### Front-end
- React.js  
- Vite.js  
- Tailwind CSS  
- Leaflet.js (spatial visualization)  
- Recharts (data visualization)  

### Back-end
- Python  
- Flask (REST API)  
- Pandas, NumPy — data analysis  
- GeoPandas, Rasterio, Rasterstats, Shapely — geospatial processing  
- Gemini API — AI-based urban recommendations  

---

## System architecture

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **Front-end (UI)** | **React + Vite** | Provides the user interface, interactive maps, data filters, and visualization components. |
| **Back-end (API/Engine)** | **Python (Flask)** | A REST API serving as the central **Python Data Engine**. It handles data processing, analysis, and AI-driven insights. |
| **Data Storage** | **AWS S3** | Stores and provides access to raw and processed remote sensing and geospatial datasets. |

### Key technologies in the data engine

* **Data processing:** Pandas / GeoPandas, Rasterio / Shapely
* **AI/Analysis:** Google **Gemini API** for advanced environmental analysis and insights.

---

## Installation and setup

### Prerequisites
* **Node.js**
* **Python 3.8+**
* A **Git** client

Clone the repository
```bash
git clone https://github.com/kaikinattandossantos/NASA_Hacka
```
Access the project folder
```bash
cd folder
```
Install the dependencies
```bash
npm install
pip install -r requirements.txt
```
Run the project
```bash
python app.py
npm run dev
```
