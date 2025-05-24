# Enviro Impact Tracker

**Enviro Impact Tracker** is a full-stack application that helps organizations estimate and compare the environmental impact of different facility types. It calculates annual energy usage, CO₂ emissions, and associated energy costs based on region, facility type, size, and usage pattern — and benchmarks them against national averages.

## Features

- 🔎 Real-time environmental impact calculation
- 📊 Visual comparison with national benchmark data
- 💡 Support for custom energy usage, emissions factor, and electricity price
- 🗺 Region-specific energy price and emissions modeling
- Responsive UI built with Bootstrap and Chart.js
- Fast, modern backend powered by FastAPI

## Technology Stack

### Backend
- **FastAPI** – high-performance API framework
- **Pydantic** – request model validation
- **Uvicorn** – ASGI web server
- **Starlette** – middleware and routing foundation

### Frontend
- **ASP.NET Core Razor Pages**
- **Bootstrap 5** – UI components and layout
- **Chart.js** – dynamic bar chart visualizations
- **JavaScript** (vanilla) – interactive client-side logic

## Installation

### Backend

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/EnviroImpactTracker.git
   cd EnviroImpactTracker
