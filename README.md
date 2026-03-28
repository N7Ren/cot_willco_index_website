# COT Willco Index Screener

The **COT Willco Index Screener** is a web application that provides a screener for Commitment of Traders (COT) data, specifically focusing on the Williams Commercial Index (Willco). It calculates and tracks positioning metrics over time, enabling users to easily evaluate large commercial and non-commercial position changes across different futures markets.

## Features

- **COT Data Screening**: View normalized readings of COT position data (Willco Index) calculated over different time horizons (e.g., 0.5 years, 1 year, 3 years).
- **Position Tracking**: Monitor weekly changes in positions and easily identify significant shifts in commercial and non-commercial positioning.
- **Automated Data Updates**: Integrates with GitHub Actions to fetch and process new COT data regularly.

## Acknowledgments

This project's website is built using the [al-folio](https://github.com/alshedivat/al-folio) theme. **al-folio** is a beautiful, simple, clean, and responsive Jekyll theme for academics and portfolios. We extend our thanks to the al-folio contributors for providing such an excellent and robust foundation. 

## Local Development

The recommended approach for local development is using Docker.

```bash
# Initial setup & start dev server
docker compose pull && docker compose up
# Site runs at http://localhost:8080

# Rebuild after changing dependencies or Dockerfile
docker compose up --build

# Stop containers and free port 8080
docker compose down
```
