import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import plotly.graph_objects as go

# Database Connection
DATABASE_USER = "Ud6xHKHHCuFbH6f.root"
DATABASE_PASSWORD = "jwl7QF0l1usUQwNi"
DATABASE_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
DATABASE_PORT = 4000
DATABASE_NAME = "Cricket_Data"

engine = create_engine(f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?ssl_verify_cert=false")

# Load Data
T20_Matches = pd.read_sql("SELECT * FROM T20_Matches;", con=engine)
ODI_Matches = pd.read_sql("SELECT * FROM ODI_Matches;", con=engine)
Test_Matches = pd.read_sql("SELECT * FROM Test_Matches;", con=engine)

# Run Rate Analysis
for df in [T20_Matches, ODI_Matches, Test_Matches]:
    df["total_runs"] = pd.to_numeric(df["total_runs"], errors="coerce")
    df["over_number"] = pd.to_numeric(df["over_number"], errors="coerce")
    df["run_rate"] = df["total_runs"].fillna(0) / df["over_number"].replace(0, pd.NA).fillna(1)

run_rate_df = pd.concat([
    T20_Matches[["match_id", "run_rate"]].assign(format="T20"),
    ODI_Matches[["match_id", "run_rate"]].assign(format="ODI"),
    Test_Matches[["match_id", "run_rate"]].assign(format="Test")
])

fig = px.box(run_rate_df, x="format", y="run_rate", color="format", 
             title="🏏 Run Rate Distribution Across Formats",
             labels={"run_rate": "Run Rate", "format": "Match Format"})
fig.show()

# Toss Decision Impact on Wins (Grouped Bar Chart)
toss_impact = pd.concat([
    T20_Matches.groupby(["toss_decision", "match_winner"]).size().reset_index(name="count").assign(format="T20"),
    ODI_Matches.groupby(["toss_decision", "match_winner"]).size().reset_index(name="count").assign(format="ODI"),
    Test_Matches.groupby(["toss_decision", "match_winner"]).size().reset_index(name="count").assign(format="Test")
])

fig = px.bar(toss_impact, x="toss_decision", y="count", color="match_winner",
             title="🎲 Toss Decision Impact on Match Wins (T20, ODI, Test)",
             labels={"toss_decision": "Toss Decision", "count": "Number of Matches"},
             barmode="group",
             facet_col="format")
fig.show()

# Wickets Analysis
wicket_df = pd.concat([
    T20_Matches.groupby("bowler")["wicket"].sum().reset_index().assign(format="T20"),
    ODI_Matches.groupby("bowler")["wicket"].sum().reset_index().assign(format="ODI"),
    Test_Matches.groupby("bowler")["wicket"].sum().reset_index().assign(format="Test")
])

fig = px.bar(wicket_df, x="bowler", y="wicket", color="format", 
             title="🎯 Top Wicket-Taking Bowlers in T20, ODI, and Test",
             labels={"bowler": "Bowler", "wicket": "Total Wickets"},
             barmode="group")
fig.show()

# Venue Analysis
venue_df = pd.concat([
    T20_Matches["venue"].value_counts().reset_index().assign(format="T20"),
    ODI_Matches["venue"].value_counts().reset_index().assign(format="ODI"),
    Test_Matches["venue"].value_counts().reset_index().assign(format="Test")
])
#player venue based performance
fig = px.bar(venue_df, x="index", y="venue", color="format", 
             title="🏟️ Matches Played at Different Venues",
             labels={"index": "Venue", "venue": "Number of Matches"},
             barmode="group")
fig.show()
#run vs strikr rate
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

# Sample Data: Runs, Balls Faced, Strike Rate
ax.scatter(df['runs'], df['ball_number'], df['total_runs'], c=df['runs'], cmap='coolwarm')

# Labels
ax.set_xlabel('Runs')
ax.set_ylabel('Balls Faced')
ax.set_zlabel('Strike Rate')
ax.set_title('3D Scatter: Runs vs Balls vs Strike Rate')
plt.show()

# Convert 'batter' to numeric
df['batter_code'] = df['batter'].astype('category').cat.codes  

# Select Top 10 Players by Runs
top_batters = df.groupby('batter')['runs'].sum().reset_index().sort_values(by='runs', ascending=False)[:10]
top_batters['batter_code'] = top_batters['batter'].astype('category').cat.codes

# 3D Bar Chart
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

x = top_batters['batter_code']  # Coded player names
y = np.zeros(len(top_batters))  # Single y-axis for bar placement
z = np.zeros(len(top_batters))  # Bar starts from zero
dx = np.ones(len(top_batters))  # Bar width
dy = np.ones(len(top_batters))  # Bar depth
dz = top_batters['runs']  # Bar height (Runs scored)

ax.bar3d(x, y, z, dx, dy, dz, shade=True)

# Labeling
ax.set_xticks(x)
ax.set_xticklabels(top_batters['batter'], rotation=45)  # Use player names as labels
ax.set_xlabel('Player')
ax.set_ylabel('Y (Dummy)')
ax.set_zlabel('Total Runs')
ax.set_title('Top 10 Players by Runs (3D Bar Chart)')

plt.show()
# Filter Virat Kohli's batting data
df = ODI_Matches.query("batter == 'V Kohli' and team_2 != 'India'")

# Ensure there's data before proceeding
if not df.empty:
    # Aggregate total runs against each country (excluding India)
    total_runs_per_country = df.groupby("team_2")["runs"].sum().reset_index()
    total_runs_per_country.rename(columns={"runs": "total_run"}, inplace=True)

    # Plot bar chart
    fig = px.bar(total_runs_per_country, x="team_2", y="total_run", 
                 title="Virat Kohli's Total Runs Against Each Country (Excluding India)",
                 labels={"team_2": "Opponent Country", "total_run": "Total Runs"},
                 color="total_run",  # Color based on total runs
                 color_continuous_scale="Reds"  # Darker shades
                 )
    
    fig.show()
else:
    print("No data available for Virat Kohli in the dataset.")
# Specify team
team_name = "India"  # Change this to any team of interest

# Filter data for the specific team
ODI_Matches = ODI_Matches[(ODI_Matches['team_1'] == team_name) | (ODI_Matches['team_2'] == team_name)]
T20_Matches = T20_Matches[(T20_Matches['team_1'] == team_name) | (T20_Matches['team_2'] == team_name)]
Test_Matches = Test_Matches[(Test_Matches['team_1'] == team_name) | (Test_Matches['team_2'] == team_name)]

# Compute average run rate per over for each format
odi_rr = ODI_Matches.groupby('over_number')['total_runs'].mean()
t20_rr = T20_Matches.groupby('over_number')['total_runs'].mean()
test_rr = Test_Matches.groupby('over_number')['total_runs'].mean()

x = np.arange(1, len(odi_rr) + 1)
x_rev = x[::-1]

# **New Prediction - Future Trend** (Exponential Model for Run Rate Growth)
predicted_rr = 2 * np.exp(0.05 * x)
predicted_upper = predicted_rr * 1.2
predicted_lower = predicted_rr * 0.8
predicted_lower = predicted_lower[::-1]

fig = go.Figure()

# Shaded Areas for confidence intervals
colors = ['rgba(0,100,80,0.2)', 'rgba(0,176,246,0.2)', 'rgba(231,107,243,0.2)', 'rgba(255,165,0,0.2)']
names = ['ODI', 'T20', 'Test', 'Predicted']
lines = [odi_rr, t20_rr, test_rr, predicted_rr]
upper_bounds = [odi_rr * 1.1, t20_rr * 1.1, test_rr * 1.1, predicted_upper]
lower_bounds = [odi_rr * 0.9, t20_rr * 0.9, test_rr * 0.9, predicted_lower]

for i in range(4):
    fig.add_trace(go.Scatter(
        x=np.concatenate((x, x_rev)),
        y=np.concatenate((upper_bounds[i], lower_bounds[i])),
        fill='toself',
        fillcolor=colors[i],
        line_color='rgba(255,255,255,0)',
        showlegend=False,
    ))

# Line plots
line_colors = ['rgb(0,100,80)', 'rgb(0,176,246)', 'rgb(231,107,243)', 'rgb(255,165,0)']
for i in range(4):
    fig.add_trace(go.Scatter(
        x=x, y=lines[i],
        line_color=line_colors[i],
        name=names[i],
    ))

fig.update_traces(mode='lines')
fig.update_layout(title=f"Run Rate Trends for {team_name} Across Formats with Predicted Future Growth")
fig.show()

