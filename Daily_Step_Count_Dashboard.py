import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import timedelta
import calendar as cal

# Page config
st.set_page_config(page_title="Step Count Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('dataset_assignment1.xlsx')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    
    def extract_avg_temp(temp_str):
        temps = temp_str.replace('ºC', '').split('-')
        min_temp = int(temps[0])
        max_temp = int(temps[1])
        return (min_temp + max_temp) / 2
    
    df['Avg_Temp'] = df['Temperature'].apply(extract_avg_temp)
    

    bins = [0, 10, 15, 20, 25, 30, 35, 100]
    labels = ['<10°C', '10-15°C', '15-20°C', '20-25°C', '25-30°C', '30-35°C', '35+°C']
    df['Temp_Bin'] = pd.cut(df['Avg_Temp'], bins=bins, labels=labels, right=False)
    

    df['Day_Type'] = df['Day of week'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')
    
    return df

df = load_data()

# Constants
GOAL = 11000
GREEN = '#59cd90'
RED = '#ee6055'
AMBER = '#fac05e'
GOAL_LINE_COLOR = '#3fa7d6'

# Title
st.markdown("<h1 style='text-align: center; margin-top: -20px; margin-bottom: 5px;'>Daily Step Count Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray; margin-top: 0px; margin-bottom: 15px;'>100-Day Walking Journey | Goal: 11,000 steps/day</h3>", unsafe_allow_html=True)

# Filters in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    date_range = st.selectbox(
        "📅 Date",
        ["All Days", "Last 30 Days", "Last 60 Days", "Custom Range"]
    )
    
    if date_range == "Custom Range":
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input(
                "Start Date",
                value=df['Date'].min(),
                min_value=df['Date'].min(),
                max_value=df['Date'].max()
            )
        with date_col2:
            end_date = st.date_input(
                "End Date",
                value=df['Date'].max(),
                min_value=df['Date'].min(),
                max_value=df['Date'].max()
            )

with col2:
    location_options = ["All Locations"] + sorted(df['Location'].unique().tolist())
    location = st.selectbox("📍 Location", location_options)

with col3:
    day_type = st.selectbox(
        "📆 Day Type",
        ["All Days","Weekdays", "Weekends", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )

with col4:
    temp_options = ["All Temperatures"] + ['<10°C', '10-15°C', '15-20°C', '20-25°C', '25-30°C', '30-35°C', '35+°C']
    temp_range = st.selectbox("🌡️ Temperature", temp_options)


filtered_df = df.copy()

# Date range filter
if date_range == 'Last 30 Days':
    cutoff_date = filtered_df['Date'].max() - timedelta(days=30)
    filtered_df = filtered_df[filtered_df['Date'] >= cutoff_date]
elif date_range == 'Last 60 Days':
    cutoff_date = filtered_df['Date'].max() - timedelta(days=60)
    filtered_df = filtered_df[filtered_df['Date'] >= cutoff_date]
elif date_range == 'Custom Range':
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    filtered_df = filtered_df[(filtered_df['Date'] >= start_datetime) & (filtered_df['Date'] <= end_datetime)]


# Location filter
if location != 'All Locations':
    filtered_df = filtered_df[filtered_df['Location'] == location]

# Day type filter
if day_type == 'Weekdays':
    filtered_df = filtered_df[filtered_df['Day_Type'] == 'Weekday']
elif day_type == 'Weekends':
    filtered_df = filtered_df[filtered_df['Day_Type'] == 'Weekend']
elif day_type in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
    filtered_df = filtered_df[filtered_df['Day of week'] == day_type]

# Temperature filter
if temp_range != 'All Temperatures':
    filtered_df = filtered_df[filtered_df['Temp_Bin'] == temp_range]

# Calculate KPIs
avg_steps = filtered_df['Step Count'].mean()
goal_pct = (filtered_df['Step Count'] >= GOAL).sum() / len(filtered_df) * 100
max_steps = filtered_df['Step Count'].max()
min_steps = filtered_df['Step Count'].min()

# Most active day
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
most_active_day = filtered_df.groupby('Day of week')['Step Count'].mean().reindex(day_order).idxmax()

# Most active location
most_active_location = filtered_df.groupby('Location')['Step Count'].mean().idxmax()

# Best temperature range
best_temp = filtered_df.groupby('Temp_Bin', observed=True)['Step Count'].mean().idxmax()

# Highest streak
filtered_df_sorted = filtered_df.sort_values('Date')
filtered_df_sorted['Met_Goal'] = filtered_df_sorted['Step Count'] >= GOAL


highest_streak = 0
current_streak_count = 0

for met in filtered_df_sorted['Met_Goal'].tolist():
    if met:
        current_streak_count += 1
        highest_streak = max(highest_streak, current_streak_count)
    else:
        current_streak_count = 0


# KPIs display
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 22px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 20px;
    }
    [data-testid="stMetricDelta"] {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h4 style='font-size: 24px;'>Key Performance Indicators</h4>", unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Average Daily Steps",
        value=f"{avg_steps:,.0f}",
        delta=f"{avg_steps - GOAL:,.0f} vs goal"
    )

with kpi2:
    st.metric(
        label="% Days Goal Reached",
        value=f"{goal_pct:.1f}%",
        delta=f"{goal_pct - 50:.1f}% vs 50%"
    )

with kpi3:
    st.metric(
        label="Max. Steps in a Day",
        value=f"{max_steps:,.0f}"
    )

with kpi4:
    st.metric(
        label="Min. Steps in a Day",
        value=f"{min_steps:,.0f}"
    )

kpi5, kpi6, kpi7, kpi8 = st.columns(4)

with kpi5:
    st.metric(
        label="Most Active Day",
        value=most_active_day
    )

with kpi6:
    st.metric(
        label="Most Active Location",
        value=most_active_location
    )

with kpi7:
    st.metric(
        label="Best Temp. Range",
        value=str(best_temp)
    )

with kpi8:
    st.metric(
        label="Highest Streak",
        value=f"{highest_streak} days"
    )

st.markdown("---")


#============================================
# SIDE BY SIDE: CALENDAR + BUBBLE CHART
# ============================================
st.markdown("<h3 style='text-align: center;'>How consistent is my daily activity?</h3>", unsafe_allow_html=True)


col_viz1, col_viz2 = st.columns([1, 1])

# ============================================
# LEFT COLUMN: INTERACTIVE MONTHLY CALENDAR
# ============================================
with col_viz1:
    st.markdown("<h4 style='text-align: center;'>📅 Monthly Calendar</h4>", unsafe_allow_html=True)
    
    filtered_df_sorted['Year'] = filtered_df_sorted['Date'].dt.year
    filtered_df_sorted['Month'] = filtered_df_sorted['Date'].dt.month
    filtered_df_sorted['Day'] = filtered_df_sorted['Date'].dt.day
    
    available_months = filtered_df_sorted.groupby(['Year', 'Month']).size().reset_index()[['Year', 'Month']]
    month_options = [f"{row['Year']}-{row['Month']:02d}" for _, row in available_months.iterrows()]
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    
    selected_month_str = st.selectbox(
        "Select Month",
        month_options,
        format_func=lambda x: f"{month_names[int(x.split('-')[1])]} {x.split('-')[0]}"
    )
    
    selected_year = int(selected_month_str.split('-')[0])
    selected_month = int(selected_month_str.split('-')[1])
    

    month_df = filtered_df_sorted[
        (filtered_df_sorted['Year'] == selected_year) & 
        (filtered_df_sorted['Month'] == selected_month)
    ].copy()


    month_cal = cal.monthcalendar(selected_year, selected_month)

 
    x_positions = []
    y_positions = []
    day_numbers = []
    colors = []
    sizes = []
    hover_texts = []

    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


    for week_idx, week in enumerate(month_cal):
        for day_idx, day in enumerate(week):
            if day == 0:
                continue
        
            day_data = month_df[month_df['Day'] == day]
        
            if len(day_data) > 0:
                steps = int(day_data.iloc[0]['Step Count'])
                location = day_data.iloc[0]['Location']
                temp = day_data.iloc[0]['Temperature']
            
                if steps >= 11000:
                    color = '#10b981'
                    status = '✅ Goal Met'
                elif steps >= 8800: 
                    color = '#f59e0b' 
                    status = '⚠️ Close'
                else:
                    color = '#ef4444'
                    status = '❌ Missed'
            
                
                size_ratio = min(steps / 11000, 1.5) 
                size = 30 + (size_ratio * 25)

                x_positions.append(day_idx)
                y_positions.append(len(month_cal) - week_idx - 1)
                day_numbers.append(str(day))
                colors.append(color)
                sizes.append(size)
                hover_texts.append(
                    f"<b>{month_names[selected_month]} {day}, {selected_year}</b><br>" +
                    f"🚶 Steps: {steps:,}<br>" +
                    f"📍 Location: {location}<br>" +
                    f"🌡️ Temperature: {temp}<br>" +
                    f" Status: {status}"
                )
            else:
                
                x_positions.append(day_idx)
                y_positions.append(len(month_cal) - week_idx - 1)
                day_numbers.append(str(day))
                colors.append('#e2e8f0')
                sizes.append(35)
                hover_texts.append(
                    f"<b>{month_names[selected_month]} {day}, {selected_year}</b><br>No data"
                )

    fig_calendar = go.Figure()

    fig_calendar.add_trace(go.Scatter(
        x=x_positions,
        y=y_positions,
        mode='markers+text',
        marker=dict(
            size=sizes,
            color=colors,
            symbol='circle',
            line=dict(width=2, color='white'),
            opacity=0.9
        ),
        text=day_numbers,
        textfont=dict(size=12, color='white', family='Arial Black'),
        textposition='middle center',
        hovertext=hover_texts,
        hovertemplate='%{hovertext}<extra></extra>',
        showlegend=False
    ))

    for i, day in enumerate(day_labels):
        fig_calendar.add_annotation(
            x=i, y=len(month_cal),
            text=f"<b>{day}</b>",
            showarrow=False,
            font=dict(size=14, color='#64748b'),
            xanchor='center',
            yanchor='middle'
        )

    fig_calendar.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color=GREEN),
        name='Goal Met (≥11k)',
        showlegend=True
    ))

    fig_calendar.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color=AMBER),
        name='Close (≥80%)',
        showlegend=True
    ))

    fig_calendar.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color=RED),
        name='Below Goal',
        showlegend=True
    ))


    fig_calendar.update_layout(
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-0.5, 6.5]
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-0.5, len(month_cal) + 0.5]
        ),
        height=500,
        plot_bgcolor='white',
        hovermode='closest',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=20, b=60)
    )

    st.plotly_chart(fig_calendar, use_container_width=True)

# ============================================
# RIGHT COLUMN: BUBBLE CHART
# ============================================
with col_viz2:
    st.markdown("<h4 style='text-align: center;'>🎯 Activity Timeline</h4>", unsafe_allow_html=True)
    
    df_sorted = filtered_df_sorted.sort_values('Date')
    

    df_met = df_sorted[df_sorted['Step Count'] >= GOAL]
    df_missed = df_sorted[df_sorted['Step Count'] < GOAL]
    
    fig_bubble = go.Figure()
    

    if len(df_met) > 0:
        sizes_met = []
        for temp in df_met['Avg_Temp']:
            size = 15 + ((temp - 8) / 30) * 25
            sizes_met.append(max(15, min(40, size)))
        
        fig_bubble.add_trace(
            go.Scatter(
                x=df_met['Date'],
                y=df_met['Step Count'],
                mode='markers',
                name='Goal Met (≥11k)',
                marker=dict(
                    size=sizes_met,
                    color=GREEN,
                    line=dict(width=2, color='white'),
                    opacity=0.8,
                    sizemode='diameter'
                ),
                text=[f"<b>{row['Date'].strftime('%Y-%m-%d')}</b><br>" +
                      f"🚶 Steps: {row['Step Count']:,}<br>" +
                      f"📍 Location: {row['Location']}<br>" +
                      f"🌡️ Temperature: {row['Temperature']}<br>" +
                      f"✅ Goal Met"
                      for _, row in df_met.iterrows()],
                hovertemplate='%{text}<extra></extra>',
                showlegend=True
            )
        )
    
    # goal missed (red)
    if len(df_missed) > 0:
        sizes_missed = []
        for temp in df_missed['Avg_Temp']:
            size = 15 + ((temp - 8) / 30) * 25
            sizes_missed.append(max(15, min(40, size)))
        
        fig_bubble.add_trace(
            go.Scatter(
                x=df_missed['Date'],
                y=df_missed['Step Count'],
                mode='markers',
                name='Goal Missed (<11k)',
                marker=dict(
                    size=sizes_missed,
                    color=RED,
                    line=dict(width=2, color='white'),
                    opacity=0.8,
                    sizemode='diameter'
                ),
                text=[f"<b>{row['Date'].strftime('%Y-%m-%d')}</b><br>" +
                      f"🚶 Steps: {row['Step Count']:,}<br>" +
                      f"📍 Location: {row['Location']}<br>" +
                      f"🌡️ Temp: {row['Temperature']}<br>" +
                      f"❌ Missed Goal"
                      for _, row in df_missed.iterrows()],
                hovertemplate='%{text}<extra></extra>',
                showlegend=True
            )
        )
    
    # goal line
    fig_bubble.add_trace(
        go.Scatter(
            x=[df_sorted['Date'].min(), df_sorted['Date'].max()],
            y=[GOAL, GOAL],
            mode='lines',
            name='Goal (11,000 steps)',
            line=dict(color=GOAL_LINE_COLOR, width=3, dash='dash'),
            hovertemplate='Goal: %{y:,.0f} steps<extra></extra>',
            showlegend=True
        )
    )
    
    fig_bubble.update_layout(
        xaxis_title="Date",
        yaxis_title="Step Count",
        hovermode='closest',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=20, t=20, b=80)
    )
    
    st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("""
    <div style='background-color: #f8fafc; padding: 12px; border-radius: 6px; font-size: 13px; margin-top: 15px; text-align: center;'>
        <b>Guide:</b> Calendar shows size=steps & color=goal status | Timeline shows size=temperature & color=goal status
    </div>
    """, unsafe_allow_html=True)


st.markdown("---")


# ============================================
# BAR CHARTS - Three side by side
# ============================================


st.markdown("""
<div style='background-color: #f8fafc; padding: 10px; border-radius: 6px; font-size: 14px; text-align: center;'>
    <span style='color: #59cd90; font-weight: bold;'>●</span> Goal Met (≥11k) | 
    <span style='color: #ee6055; font-weight: bold;'>●</span> Goal Missed (<11k) | 
    <span style='color: #3fa7d6; font-weight: bold;'>---</span> Goal Line
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

bar_col1, bar_col2, bar_col3 = st.columns(3)

# ============================================
# CHART 1: BAR CHART - Day of Week
# ============================================
with bar_col1:
    st.markdown("<h3 style='text-align: center;margin-bottom: -28px'>📅 Which days am I most active?</h3>", unsafe_allow_html=True)

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_avg = filtered_df.groupby('Day of week')['Step Count'].mean()


    
    day_order_filtered = []
    day_avg_filtered = []
    day_colors = []

    for day in day_order:
        if day in day_avg.index:
            avg = day_avg[day]
            day_order_filtered.append(day)
            day_avg_filtered.append(avg)
            color = GREEN if avg >= GOAL else RED
            day_colors.append(color)

    days_met = []
    avg_met = []

    days_missed = []
    avg_missed = []

    for day, avg in zip(day_order_filtered, day_avg_filtered):
        if avg >= GOAL:
            days_met.append(day)
            avg_met.append(avg)
        else:
            days_missed.append(day)
            avg_missed.append(avg)


    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(
            x=day_order_filtered,
            y=day_avg_filtered,
            marker=dict(color=day_colors),
            text=[f'{int(avg):,}' for avg in day_avg_filtered],
            textposition='outside',
            hovertemplate='%{x}<br>Average: %{y:,.0f} steps<extra></extra>',
            name = "Average Steps",
            showlegend=False
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=12, color=GREEN),
            name='Goal Met (≥11k)',
            showlegend=False
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=12, color=RED),
            name='Goal Missed (<11k)',
            showlegend=False
        )
    )


    fig2.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Average Step Count",
        height=500,
        showlegend=False,
        shapes=[
        dict(
            type='line',
            x0=-0.7,
            x1=len(day_order_filtered) - 0.3,
            y0=GOAL - 200,  
            y1=GOAL - 200,
            line=dict(color=GOAL_LINE_COLOR, width=2, dash='dash'),
            xref='x',
            yref='y'
        )
    ]
    )

    st.plotly_chart(fig2, use_container_width=True)

# ============================================
# CHART 2: BAR CHART - Temperature
# ============================================
with bar_col2:
    st.markdown("<h3 style='text-align: center;margin-bottom: -28px'>🌡️ How does temperature affect my walking habits?</h3>", unsafe_allow_html=True)

    temp_bin_avg = filtered_df.groupby('Temp_Bin', observed=True)['Step Count'].mean()

    if len(temp_bin_avg) > 0:
        temp_ranges = temp_bin_avg.index.tolist()
        temp_colors = [GREEN if avg >= GOAL else RED for avg in temp_bin_avg]

        fig3 = go.Figure()

        fig3.add_trace(
            go.Bar(
                x=temp_ranges,
                y=temp_bin_avg,
                marker=dict(color=temp_colors),
                text=[f'{int(avg):,}' for avg in temp_bin_avg],
                textposition='outside',
                hovertemplate='%{x}<br>Average: %{y:,.0f} steps<extra></extra>',
                name = "Average Steps",
                showlegend=False
            )
        )

        fig3.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=12, color=GREEN),
                name='Goal Met (≥11k)',
                showlegend=False
            )
        )

        fig3.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=12, color=RED),
                name='Goal Missed (<11k)',
                showlegend=False
            )
        )



        fig3.update_layout(
            xaxis_title="Temperature Range",
            yaxis_title="Average Step Count",
            height=500,
            showlegend=False,
            shapes=[
        dict(
            type='line',
            x0=-0.7,
            x1=len(temp_ranges) - 0.3,
            y0=GOAL - 200,  
            y1=GOAL - 200,
            line=dict(color=GOAL_LINE_COLOR, width=2, dash='dash'),
            xref='x',
            yref='y'
        )
    ]
    )

        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No temperature data available for the selected filters.")

# ============================================
# CHART 3: BAR CHART - Location
# ============================================
with bar_col3:
    st.markdown("<h3 style='text-align: center; margin-bottom: -28px;'>📍 Where do I walk the most?</h3>", unsafe_allow_html=True)

    location_avg = filtered_df.groupby('Location')['Step Count'].mean().sort_values(ascending=False)

    if len(location_avg) > 0:
        locations = location_avg.index.tolist()
        location_colors = [GREEN if avg >= GOAL else RED for avg in location_avg]

        fig4 = go.Figure()

        fig4.add_trace(
            go.Bar(
                x=locations,
                y=location_avg,
                marker=dict(color=location_colors),
                text=[f'{int(avg):,}' for avg in location_avg],
                textposition='outside',
                hovertemplate='%{x}<br>Average: %{y:,.0f} steps<extra></extra>',
                name = "Average Steps",
                showlegend=False
            )
        )

        fig4.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=12, color=GREEN),
                name='Goal Met (≥11k)',
                showlegend=False
            )
        )

        fig4.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=12, color=RED),
                name='Goal Missed (<11k)',
                showlegend=False
            )
        )

        fig4.update_layout(
            xaxis_title="Location",
            yaxis_title="Average Step Count",
            height=500,
            showlegend=False,
            shapes=[
        dict(
            type='line',
            x0=-0.7,
            x1=len(locations) - 0.3,
            y0=GOAL - 200,  
            y1=GOAL - 200,
            line=dict(color=GOAL_LINE_COLOR, width=2, dash='dash'),
            xref='x',
            yref='y'
        )
    ]
    )

        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("No location data available for the selected filters.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>🚶‍♂️ Keep moving towards your goals!</p>", unsafe_allow_html=True)

