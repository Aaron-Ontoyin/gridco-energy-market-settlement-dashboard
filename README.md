# Energy Consumption Dashboard

A modern Dash dashboard for analyzing energy consumption patterns across generators, plants, and consumers.

## Features

- **Interactive Filtering**: Select consumer and date to view specific consumption data
- **24-Hour Breakdown**: View hourly consumption for any consumer on any date
- **Plant Generation Analysis**: See total generation from associated plants
- **Visual Analytics**: Beautiful spline charts showing consumption trends
- **Modern UI**: Sleek dark theme with gradient headers and smooth animations

## Installation

Install dependencies using uv:

```bash
uv sync
```

## Usage

### Running the Dashboard

```bash
python app.py
```

The dashboard will be available at `http://localhost:8050`

### Exploring Data

Open `lab.ipynb` to explore the dummy data:
- **Producers**: Generator-to-plant mappings
- **Plant-Consumer**: Plant allocation percentages per consumer
- **Readings**: Hourly plant readings over 7 days

## How It Works

1. **Data Structure**:
   - Each consumer receives energy from one or more plants
   - Each plant-consumer relationship has an allocation percentage
   - Readings are recorded hourly for each plant

2. **Consumption Calculation**:
   - Consumer consumption = Plant Reading × Allocation Percentage
   - Total consumption = Sum of all associated plant contributions

3. **Dashboard Components**:
   - **Filters**: Select consumer and date
   - **Consumption Table**: Hourly breakdown (24 hours)
   - **Plant Table**: Individual plant generation + total
   - **Chart**: Spline visualization of consumption and generation patterns

## Data Schema

### Producers
- `Generator`: Generator identifier
- `Plants`: Plant identifier

### Plant-Consumer
- `Plant`: Plant identifier
- `Consumer`: Consumer identifier
- `Pct`: Allocation percentage (0-1)

### Readings
- `Plant`: Plant identifier
- `Reading`: Energy reading value
- `Datetime`: Timestamp of reading

