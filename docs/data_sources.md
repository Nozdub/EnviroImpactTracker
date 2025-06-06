# Data Sources & Calculations for Baselines

This document explains the sources, calculations, and reasoning behind each baseline value used in `static_config.json`.

---

## Factory

- **Total industry usage (GWh)**: 75,603 GWh
- **Number of industrial companies**: 9,436
- **Baseline calculation**:  
  75,603,000 MWh / 9,436 ≈ 8,013 MWh per factory
  - **Source(s)**:  
    - [SSB - Energibruk i industrien](https://www.ssb.no/energi-og-industri/energi/statistikk/energibruk-i-industrien)  
    - [SSB - Bedrifter etter størrelse og næring](https://www.ssb.no/virksomheter-foretak-og-regnskap/virksomheter-og-foretak/statistikk/virksomheter)

    Benchmark data:
    - **Best Practice Energy Use**: 200 kWh/m²/year
    - **Best Practice CO₂ Emissions**: 6.8 kgCO₂/m²/year
    - **Assumed Average Floor Area**: 3,000 m²
    - **Calculated Annual Energy Use**: 600,000 kWh
    - **Calculated Annual CO₂ Emissions**: 20,400 kg
    - **Source**: [EU Building Stock Observatory](https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficient-buildings/eu-building-stock-observatory_en)
---

## Data Center

- **Total usage (2024)**: 1,612.88 GWh
- **Estimated number of data centers**: 150
- **Baseline calculation**:  
  1,612,880 MWh / 150 ≈ 10,752 MWh per data center
- **Source(s)**:  
  - [Elhub Report - Norske datasentre forbruksanalyse (2024)](file-6PvHdZ6YvUyjfTSCgKRMj9)

  Benchmark data:
    - **Best Practice Energy Use**: 500 kWh/m²/year
    - **Best Practice CO₂ Emissions**: 17 kgCO₂/m²/year
    - **Assumed Average Floor Area**: 2,000 m²
    - **Calculated Annual Energy Use**: 1,000,000 kWh
    - **Calculated Annual CO₂ Emissions**: 34,000 kg
    - **Source**: [EU Building Stock Observatory](https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficient-buildings/eu-building-stock-observatory_en)

---

## Farm

- **Total farm usage**: 7,300 GWh
- **Number of farms**: 37,400
- **Baseline calculation**:  
  7,300,000 MWh / 37,400 ≈ 195 MWh per farm
- **Source(s)**:  
  - [SSB - Energibruk i jordbruket](https://www.ssb.no/jord-skog-jakt-og-fiskeri/jordbruk/artikler/jordbruk-og-miljo-energibruk-i-jordbruket)
  - [SSB - Bedrifter etter størrelse og næring](https://www.ssb.no/virksomheter-foretak-og-regnskap/virksomheter-og-foretak/statistikk/virksomheter)

  Benchmark data:
    - **Best Practice Energy Use**: 150 kWh/m²/year
      - **Best Practice CO₂ Emissions**: 5.1 kgCO₂/m²/year
      - **Assumed Average Floor Area**: 1,000 m²
      - **Calculated Annual Energy Use**: 150,000 kWh
      - **Calculated Annual CO₂ Emissions**: 5,100 kg
      - **Source**: [EU Building Stock Observatory](https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficient-buildings/eu-building-stock-observatory_en)

---

## Hospital

- **Estimated total usage**: 1,600 GWh
- **Number of hospitals**: 42
- **Baseline calculation**:  
  1,600,000 MWh / 42 ≈ 38,095 MWh per hospital
- **Source(s)**:  
  - [Estimate based on sector reports, Statnett](https://www.statnett.no)
  - [Wikipedia - List of Norwegian hospitals](https://no.wikipedia.org/wiki/Liste_over_norske_sykehus)

  Benchmark data:
    - **Best Practice Energy Use**: 738.5 kWh/m²/year
    - **Best Practice CO₂ Emissions**: 25.9 kgCO₂/m²/year
    - **Assumed Average Floor Area**: 5,000 m²
    - **Calculated Annual Energy Use**: 3,692,500 kWh
    - **Calculated Annual CO₂ Emissions**: 129,500 kg
    - **Source**: [EU Building Stock Observatory](https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficient-buildings/eu-building-stock-observatory_en)
---

## Office Building

- **Estimated total usage**: 5,990 GWh (estimated 40% share of service sector)
- **Number of office-related businesses**: 38,550
- **Baseline calculation**:  
  5,990,000 MWh / 38,550 ≈ 155,400 kWh per office building
- **Source(s)**:  
  - [SSB - Strømforbruk etter prisområde og forbrukergruppe (2023)](https://www.ssb.no/energi-og-industri/energi/statistikk/elektrisitet)
  - [SSB - Bedrifter etter størrelse og næring (2023)](https://www.ssb.no/virksomheter-foretak-og-regnskap/virksomheter-og-foretak/statistikk/virksomheter)

  Benchmark data:
    - **Best Practice Energy Use**: 180 kWh/m²/year
    - **Best Practice CO₂ Emissions**: 6.12 kgCO₂/m²/year
    - **Assumed Average Floor Area**: 1,000 m²
    - **Calculated Annual Energy Use**: 180,000 kWh
    - **Calculated Annual CO₂ Emissions**: 6,120 kg
    - **Source**: [EU Building Stock Observatory](https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficient-buildings/eu-building-stock-observatory_en)

---

## Retail Store

- **Estimated baseline usage**: 165,000 kWh
- **Assumptions**:
  - Typical size: ~600 m²
  - Specific energy use: ~275 kWh/m²/year (based on NVE report)
- **Calculation**:  
  600 m² * 275 kWh/m²/year ≈ 165,000 kWh/year
- **Source(s)**:  
  - [NVE Rapport 2014-01: Spesifikk energibruk i yrkesbygg](https://publikasjoner.nve.no/rapport/2014/rapport2014_01.pdf)

  Benchmark data:
    - **Best Practice Energy Use**: 180 kWh/m²/year
    - **Best Practice CO₂ Emissions**: 6.12 kgCO₂/m²/year
    - **Assumed Average Floor Area**: 1,000 m²
    - **Calculated Annual Energy Use**: 180,000 kWh
    - **Calculated Annual CO₂ Emissions**: 6,120 kg
    - **Source**: [EU Building Stock Observatory](https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficient-buildings/eu-building-stock-observatory_en)

---

## School

- **Estimated baseline usage**: 437,500 kWh
- **Assumptions**:
  - Typical school size: ~2,500 m²
  - Specific energy use: ~175 kWh/m²/year (NVE report)
- **Calculation**:  
  2,500 m² * 175 kWh/m²/year ≈ 437,500 kWh/year
- **Source(s)**:  
  - [NVE Rapport 2014-01: Spesifikk energibruk i yrkesbygg](https://publikasjoner.nve.no/rapport/2014/rapport2014_01.pdf)

  Benchmark data:
    - **Best Practice Energy Use**: 175 kWh/m²/year
    - **Best Practice CO₂ Emissions**: 5.95 kgCO₂/m²/year
    - **Assumed Average Floor Area**: 2,500 m²
    - **Calculated Annual Energy Use**: 437,500 kWh
    - **Calculated Annual CO₂ Emissions**: 14,875 kg
    - **Source**: [EU Building Stock Observatory](https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficient-buildings/eu-building-stock-observatory_en)
---

## Residential

- **Building types**:
  - Small = Leilighet (blokk): 10,899 kWh/year
  - Medium = Rekkehus: 17,090 kWh/year
  - Large = Enebolig: 25,776 kWh/year
- **Source(s)**:  
  - [Average electricity use by dwelling type, Norway (NVE / public reports)]

  Benchmark data:
## Residential Buildings (Norway)

- **Best Practice Energy Use** (TEK17/Enova guidance):
  - Apartment: 100 kWh/m²/year
  - Townhouse: 110 kWh/m²/year
  - Detached House: 120 kWh/m²/year
- **Assumed Floor Areas**:
  - Small (Apartment): 60 m² → 6,000 kWh/year
  - Medium (Townhouse): 100 m² → 11,000 kWh/year
  - Large (Detached House): 150 m² → 18,000 kWh/year
- **Source(s)**:
  - [TEK17 Energy Frame Limits](https://dibk.no/byggereglene/byggteknisk-forskrift-tek17/kapittel-14-energi/)
  - [Enova Recommendations](https://www.enova.no/)


---