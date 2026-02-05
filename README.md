# Daily-Step-Count-Dashboard

An interactive dashboard built with Streamlit to visualize and analyze daily step count data over a 100-day period.

## Features

- **Interactive Filters**: Filter data by date range, location, day type, and temperature.
- **Key Performance Indicators (KPIs)**: Track average steps, goal achievement percentage, streaks, and more.
- **Monthly Calendar View**: Visual calendar showing daily performance with color-coded indicators.
- **Activity Timeline**: Bubble chart displaying steps over time with temperature correlation.
- **Analysis**: Bar charts comparing activity by day of week, temperature range, and location

## Installation

### Prerequisites
- Python 3.8 or higher

### Setup
1. Clone or download this repository
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Dashboard

Run the following command in your terminal:
```bash
streamlit run dashboard.py
```
**Note:** replace `dashboard.py` with your actual filename if different.

The dashboard will open automatically in your default web browser at `http://localhost:8501`

## Project Structure
```
.
├── dashboard.py                          # Main dashboard application
├── dataset_assignment1.xlsx              # Data file
├── requirements.txt                      # Python dependencies
├── README.md                             # This file
├── presentation.pdf                      # Project presentation slides
├── online_tool.txt                       # Online dashboard URL
└── thumbnail.png                         # Dashboard preview image
```

## Data Format
The Excel file should contain the following columns:
- `Date`: Date of the record.
- `Step Count`: Number of steps taken.
- `Location`: Location where steps were recorded.
- `Day of week`: Day name (Monday, Tuesday, etc.).
- `Temperature`: Temperature range (e.g., "15-20ºC").

## Dashboard Sections

1. **Filters**: Date range, location, day type, and temperature filters.
2. **KPIs**: 8 key metrics including averages, maximums, and streaks.
3. **Calendar & Timeline**: Monthly calendar and activity timeline.
4. **Comparative Charts**: Three bar charts analyzing patterns.

## Goal Settings
- Personal daily step goal: 11,000 steps
- Color coding:
  - 🟢 Green: Goal met ($\geq$ 11,000 steps)
  - 🟡 Amber: Close to goal ($geq$ 8,800 steps)
  - 🔴 Red: Below goal (< 8,800 steps)


## Deliverables
- **dashboard.py**: Code for the interactive Streamlit dashboard application
- **dataset_assignment1.xlsx**: 100-day step count dataset
- **presentation.pdf**: Project presentation
- **thumbnail.png**: Dashboard screenshot
- **online_tool.txt**: Link to the dashboard
- **requirements.txt**: Python package dependencies
- **README.md**: Setup and usage instructions
  
## Author
[Alexandra Perruchot-Triboulet Rodríguez]
