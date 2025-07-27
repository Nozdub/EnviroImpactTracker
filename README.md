# Enviro Impact Tracker

**Enviro Impact Tracker** is a full-stack educational project designed to estimate and compare the environmental impact of different facility types in Norway.

It calculates **annual energy usage, CO₂ emissions, and energy costs** based on:
- Region
- Facility type
- Size
- (Optional) Custom usage and emission factors

The tool prioritizes **transparent, explainable calculations** — not a black box.  
All baseline assumptions are documented and sourced from public Norwegian data.

---

## Features

- Real-time environmental impact calculation
- Live electricity price + CO₂ emission factor APIs
- Visual comparison against national benchmarks
- Region-specific modeling (NO1-NO5 grid zones)
- Support for multiple facility types (industry, farms, schools, hospitals, offices, data centers, residential, etc.)
- Custom overrides (kWh, emission factor, electricity price)
- Full documentation of baseline assumptions ([baseline_data.md](baseline_data.md))
- Full test suite with automated CI checks on GitHub Actions
- Responsive UI with clear "About" and transparency statements

---

## Technology Stack

### Backend
- **FastAPI** – high-performance API framework
- **Pydantic** – strict request validation
- **Uvicorn** – ASGI server
- **Starlette** – routing and middleware
- **Live APIs**:
  - [hvakosterstrommen.no](https://www.hvakosterstrommen.no/) — electricity price API
  - [electricityMap.org](https://electricitymap.org/) — CO₂ intensity API
- Modular architecture: services, config_loader, benchmark_loader

### Frontend
- **ASP.NET Core Razor Pages** (.NET Core MVC)
- **Bootstrap 5** – responsive UI
- **Chart.js** – dynamic visualization
- **JavaScript** – interactive client logic
- **"About" page** with full project transparency

---

## Testing & Quality

- **Pytest** test suite
- **Parametrized tests** for core `/calculate` endpoint
- **Negative tests** for invalid input handling
- **Mocking tests** for API fallback paths
- **Endpoints tested**:
  - `/calculate`
  - `/regions`
  - `/facility-types`
- **GitHub Actions CI**:
  - Automatic test run on pull requests to `main`
  - Prevents broken builds from being merged

---

## Future updates
- Add more advanced metrics.
- Find a usable price api that can return historical price data as well.

## Installation

### Backend

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/EnviroImpactTracker.git
    cd EnviroImpactTracker
    ```

2. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```

3. Run backend:
    ```bash
    uvicorn app.main:app --reload
    ```

### Frontend

Open the `EnviroImpactFrontend` project in Visual Studio.  
Run the frontend with IIS Express or:

```bash
dotnet run

