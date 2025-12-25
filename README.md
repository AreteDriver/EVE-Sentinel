# EVE Sentinel (Starmap)

A mobile-first 2D starmap application for EVE Online that combines static universe data (SDE) with live ESI feeds and authenticated character overlays.

## Features

- **Offline-First Architecture**: SQLite database with preloaded universe data
- **Live Data Layers**: Kills, jumps, incursions, sovereignty heatmaps
- **Pathfinding**: Dijkstra/A* routing with secure/insecure preferences
- **Capital Jump Planner**: Jump range visualization and multi-leg route planning
- **ESI Integration**: OAuth2 SSO for character location, assets, standings
- **2D Map Projection**: Optimized rendering of the 3D EVE universe

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/AreteDriver/Sentinel-.git
cd Sentinel-

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### Initialize Database

```bash
# Ingest universe data from ESI (takes ~5-10 minutes)
python -m scripts.ingest_sde --reset

# Optional: Skip stargates for faster testing
python -m scripts.ingest_sde --reset --skip-stargates
```

### Run the API Server

```bash
# Start FastAPI server
python -m backend.main

# Or with uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### Refresh Live Data

```bash
# One-time refresh
python -m scripts.refresh_cache --once

# Continuous refresh service
python -m scripts.refresh_cache
```

## API Endpoints

### Systems

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/systems/{id}` | GET | Get system details |
| `/api/v1/systems?q=Jita` | GET | Search systems by name |
| `/api/v1/systems/{id}/neighbors` | GET | Get connected systems |

### Routing

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/route` | POST | Calculate route between systems |

Request body:
```json
{
  "origin_id": 30000142,
  "destination_id": 30002187,
  "route_type": "shortest",
  "avoid_systems": [],
  "avoid_regions": []
}
```

### Jump Planning

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jump/range` | POST | Get systems in jump range |
| `/api/v1/jump/route` | POST | Plan capital jump route |

### Heatmaps

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/heatmap` | POST | Get kills/jumps/activity heatmap |

### Statistics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/stats` | GET | Universe statistics |
| `/api/v1/health` | GET | API health check |

## Project Structure

```
eve_starmap/
├── backend/
│   ├── api/              # FastAPI routes and models
│   ├── esi/              # ESI client with caching
│   ├── sde/              # SQLite schema and models
│   ├── graph/            # Pathfinding algorithms
│   ├── jump_planner/     # Capital range calculations
│   └── main.py           # FastAPI application
├── mobile/               # React Native / Flutter app (future)
│   ├── components/
│   ├── screens/
│   └── services/
├── data/
│   └── universe.db       # SQLite database
├── scripts/
│   ├── ingest_sde.py     # SDE ingestion
│   └── refresh_cache.py  # Live data refresh
└── tests/
```

## Database Schema

### Core Tables

- **regions** - EVE regions with coordinates
- **constellations** - Region subdivisions
- **solar_systems** - Systems with security, coordinates, 2D projection
- **stargates** - Gate connections between systems
- **system_connections** - Graph edges with weights

### Live Data Tables

- **system_stats** - Kill/jump statistics (5 min TTL)
- **incursions** - Active incursions (10 min TTL)
- **sovereignty** - Sov ownership (1 hour TTL)
- **esi_cache** - Generic ESI response cache

### User Data Tables

- **ship_configs** - Capital ship configurations
- **pilot_profiles** - Skill and preference profiles
- **saved_routes** - Saved navigation routes
- **cyno_chains** - Capital jump chains

## ESI Scopes

For authenticated features, the following scopes are used:

| Scope | Feature |
|-------|---------|
| `esi-location.read_location.v1` | Live character position |
| `esi-location.read_online.v1` | Online status |
| `esi-ui.write_waypoint.v1` | Push routes to game |
| `esi-assets.read_assets.v1` | Asset location overlay |
| `esi-characters.read_standings.v1` | Standings-colored systems |

## Capital Ships

Supported capital ships for jump planning:

- **Dreadnoughts**: Revelation, Moros, Naglfar, Phoenix
- **Carriers**: Archon, Thanatos, Nidhoggur, Chimera
- **Force Auxiliaries**: Apostle, Ninazu, Lif, Minokawa
- **Supercarriers**: Aeon, Nyx, Hel, Wyvern
- **Titans**: Avatar, Erebus, Ragnarok, Leviathan
- **Jump Freighters**: Ark, Anshar, Nomad, Rhea
- **Black Ops**: Sin, Widow, Panther, Redeemer

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Type Checking

```bash
mypy backend/
```

### Linting

```bash
ruff check .
ruff format .
```

## Roadmap

- [x] SDE ingestion and SQLite schema
- [x] ESI client with caching
- [x] Pathfinding algorithms (Dijkstra/A*)
- [x] FastAPI backend
- [x] Capital jump planner
- [ ] ESI OAuth2 authentication
- [ ] Mobile app (React Native/Flutter)
- [ ] Real-time WebSocket updates
- [ ] Corp/Alliance features (Data Hub integration)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support the Project

If you enjoy this project, consider supporting development:

- **In-Game**: Send ISK donations to **AreteDriver** in EVE Online
- **Buy Me a Coffee**: [buymeacoffee.com/aretedriver](https://buymeacoffee.com/aretedriver)

Your support helps keep these projects maintained and improving. o7

---

## Acknowledgments

- [EVE Online](https://www.eveonline.com/) - CCP Games
- [ESI (EVE Swagger Interface)](https://esi.evetech.net/)
- [EVE SDE](https://developers.eveonline.com/resource/resources)
