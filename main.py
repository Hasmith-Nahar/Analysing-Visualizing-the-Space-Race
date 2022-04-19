import numpy as np
import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# These might be helpful:
from iso3166 import countries
# from datetime import datetime, timedelta

# Notebook Presentation
pd.options.display.float_format = '{:,.2f}'.format

# Load the Data
df_data = pd.read_csv('mission_launches.csv')
df_data.sample(5)

# Preliminary Data Exploration
print(f'The shape of the dataset is {df_data.shape}.')
print(f'The dataset has {df_data.shape[0]} rows and {df_data.shape[1]} columns.')
print('The column names are:')
for column in df_data.columns:
    print(column)
df_data.info()

# Data Cleaning - Check for Missing Values and Duplicates
print(f'There are {df_data.isna().sum().sum()} NaN values in the dataset.')
print(f'There are {df_data.duplicated().sum().sum()} duplicates in the dataset.')

df_data.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], inplace=True)
df_data.head()

# Descriptive Statistics
df_data.describe()

# Number of Launches per Company
launches_per_company = df_data.groupby('Organisation').count()['Date'].sort_values(ascending=False)
fig = px.bar(x=launches_per_company.index,
             y=launches_per_company.values,
             title='Number of Launches per Company',
             log_y=True,
             labels={"x": "Organisation", "y": "Launches"},
             color=launches_per_company.values)
fig.update_layout(xaxis_title='Organisation',
                  yaxis_title='Number of Launches',
                  coloraxis_showscale=False)
fig.update_xaxes(tickangle = 45)
fig.show()

# Number of Active versus Retired Rockets
rocket_status = df_data.groupby('Rocket_Status').count()['Date']
bar = px.bar(x=['Active', 'Retired'],
             y=rocket_status,
             color=rocket_status,
             title='Number of Active vs Retired Rockets')
bar.update_layout(xaxis_title='',
                  yaxis_title='Number of Rockets',
                  coloraxis_showscale=False)
bar.show()

# Distribution of Mission Status
mission_status = df_data.groupby('Mission_Status').count()['Date']
bar = px.bar(mission_status,
             color=mission_status,
             title='Distribution of Mission Status',
             log_y=True)
bar.update_layout(xaxis_title='',
                  yaxis_title='Count of Missions',
                  coloraxis_showscale=False)
bar.show()

# How Expensive are the Launches?
df_data.Price = df_data['Price'].str.replace(',', '')
df_data.Price = pd.to_numeric(df_data.Price)
plt.figure(figsize=(8, 4), dpi=200)
sns.histplot(data=df_data,
             x='Price',
             bins=100)
plt.xlabel('Price in USD Millions')
plt.title('Distribution of Launche Prices')
plt.show()
df_data.sample(5)

slice_location = df_data.Location.str.split(',', n=3, expand=True)
df_data['Country'] = np.where(slice_location[3].isna(), np.where(slice_location[2].isna(), slice_location[1], slice_location[2]), slice_location[3])
df_data.sample(5)

# check NaN in Country column
df_data.Country.isna().sum()
df_data.Country.unique()
df_data.Country = df_data.Country.str.lstrip(' ')
df_data.Country.unique()

# Update Countries
df_data['Country'] = np.where(df_data['Country'] == "Gran Canaria", "USA", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "Russia", "Russian Federation", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "New Mexico", "USA", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "Yellow Sea", "China", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "Shahrud Missile Test Site", "Iran", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "Pacific Missile Range Facility", "USA", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "Pacific Ocean", "USA", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "Barents Sea", "Russian Federation", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "Iran", "Iran, Islamic Republic of", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "North Korea", "Korea, Democratic People's Republic of", df_data['Country'])
df_data['Country'] = np.where(df_data['Country'] == "South Korea", "Korea, Republic of", df_data['Country'])

df_data.Country.unique()

# Get country codes
codes = [countries.get(country).alpha3 for country in df_data.Country]
df_data['ISO'] = codes
df_data.sample(5)

# Using a Choropleth Map to Show the Number of Failures by Country
failures_by_country = df_data[df_data.Mission_Status != 'Success'].groupby(['Country', 'ISO'], as_index=False).agg({'Mission_Status': pd.Series.count})
failures_by_country = failures_by_country.rename(columns={'Mission_Status': 'Failures'})
fig = px.choropleth(failures_by_country, locations='ISO',
                    color='Failures',
                    hover_name="Country",
                    color_continuous_scale=px.colors.sequential.matter,
                    title='Number of Launch Failures by Country')
fig.show()

# Create a Plotly Sunburst Chart of the countries, organisations, and mission status.
success_by_org = df_data[df_data.Mission_Status == 'Success'].groupby(['Country', 'Organisation'], as_index=False).agg({'Mission_Status': pd.Series.count})
success_by_org = success_by_org.rename(columns={'Mission_Status': 'Successes'})
# success_by_org

failures_by_org = df_data[df_data.Mission_Status != 'Success'].groupby(['Country', 'Organisation'], as_index=False).agg({'Mission_Status': pd.Series.count})
failures_by_org = failures_by_org.rename(columns={'Mission_Status': 'Failures'})
failures_by_org

outcome_by_org = pd.merge(success_by_org, failures_by_org,  how='outer', left_on=['Country','Organisation'], right_on = ['Country', 'Organisation'])
outcome_by_org.fillna(0, inplace=True)
outcome_by_org

burst = px.sunburst(outcome_by_org,
                  path=['Country', 'Organisation'],
                  values='Successes',
                  title='Launch Successes by Organisation')
burst.update_layout(xaxis_title='Number of Succeeding Launches',
                    yaxis_title='Organisation',
                    coloraxis_showscale=False)
burst.show()
burst = px.sunburst(outcome_by_org,
                  path=['Country', 'Organisation'],
                  values='Failures',
                  title='Launch Failures by Organisation')
burst.update_layout(xaxis_title='Number of Failed Launches',
                    yaxis_title='Organisation',
                    coloraxis_showscale=False)
burst.show()
