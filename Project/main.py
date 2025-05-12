import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv('Project/AirQuality.csv') #loading the dataset

st.header('World air quality index analytics')
st.text('The dataset is availbable at https://www.kaggle.com/datasets/adityaramachandran27/world-air-quality-index-by-city-and-coordinates/data')
st.text('The dataset contains the Air Quality Index (hereafter AQI) for various cities around the world, along with their coordinates, as well as pollution and various gas levels.')



st.subheader('Basic Information')

st.code('df.shape')
df.shape
st.text('The dataset contains {} rows and {} columns.'.format(df.shape[0], df.shape[1]))

st.code('df.describe(include="all")')
st.dataframe(df.describe(include='all'))
st.text('-The average AQI is 63\n-There are 174 countries and 14229 unique cities in the dataset.\n-For all 4 pollutants(CO, O3, NO2 and PM2.5), the most common category is "Good".\n-The data also includes the coordinates of the all its cities, which are recorded in the "Lat" and "Long" columns.')

st.text("Let's look at the first 10 rows of the dataset:")
st.code('df.head(10)')
st.dataframe(df.head(10))

st.text('Check for missing values:')
st.code('df.isnull().sum()')
st.dataframe(df.isnull().sum())
st.text('As we can see, the only missing values can be found in the country column.\nSince there is no sufficient way to fill these missing values, they will be removed.')

st.text("Let's also check for duplicate rows in the city column:")
st.code('df.duplicated(subset="City").sum()')
st.code(df.duplicated(subset="City").sum())
st.text('We have {} duplicate rows in the city column.\nThey will be also removed.'.format(df.duplicated(subset="City").sum()))

st.text('Removal duplicates and missing values:')
df.drop_duplicates(subset='City') # drops dublicates
df.dropna(inplace=True) # drops rows with missing values
df.reset_index(drop=True, inplace=True) # resets the indexes
st.code("df.drop_duplicates(subset='City')\ndf.dropna(inplace=True)\ndf.reset_index(drop=True, inplace=True)")
st.text("Let's check that there are no more missing values left:")
st.code('df.isnull().sum().sum()')
st.code(df.isnull().sum().sum())

st.code('df.shape')
df.shape
st.text('The dataset now has {} rows and {} columns, which is an insignificant drop.'.format(df.shape[0], df.shape[1]))

st.text("Let's also print at the median value of the AQI Values")
st.code("df['AQI Value'].median()")
st.code(df['AQI Value'].median())
st.markdown('After the data has been cleaned, we can get to the next step - graph plotting')
 
st.subheader('Simple graph plotting')

st.text('Let\'s creatr a choropleth map to visualize the distribution of the AQI Value in different countries:')
fig = px.choropleth(df, locations='Country', locationmode='country names', color='AQI Value', hover_name='Country', color_continuous_scale='deep')
fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
st.plotly_chart(fig)

colour_ops = {
    'Good': '#58d68d',
    'Moderate': '#f1c40f',
    'Unhealthy for Sensitive Groups': '#9467bd',
    'Unhealthy': '#ff7f0e',
    'Very Unhealthy': '#d62728',
    'Hazardous': '#d834b8',
}

st.text('Next, let\'s create a histogram to visualize the distribution of the AQI Categories:')
fig2 = px.histogram(df, x='AQI Category', color='AQI Category', title='Distribution of AQI Categories', color_discrete_map=colour_ops)
st.plotly_chart(fig2)


data = {
    "CO AQI Category": 'CO AQI Value',
    "Ozone AQI Category": 'Ozone AQI Value',
    "NO2 AQI Category": 'NO2 AQI Value',
    "PM2.5 AQI Category": 'PM2.5 AQI Value'
}


st.text('Finally, let\'s create a piechart that will show the distribution of each category for a pollutant:')
op = st.selectbox('Pollutant', options = list(data.keys()))
if op:
    fig3 = px.pie(df, values=data[op], names='AQI Category', title='Distribution of {}'.format(op), color_discrete_map=colour_ops)
    st.plotly_chart(fig3)

st.subheader('Complex grapj plotting')

st.text('I will create a histrogram to show the distribution of AQI Values')
fig4 = px.histogram(df, x='AQI Value', color='AQI Category', nbins=300, title='Global Air Quality Index', color_discrete_map=colour_ops)
st.plotly_chart(fig4)
st.text("From the histogram, we can see that the AQI values are mostly distributed between 0 and 100, with a peak around 50. This indicates that the majority of the world's cities have relatively good air quality, except for a few cities with extremely high AQI values(27 cities with a value of 500).")

st.text("Finally, I'll create a sunburst chart that will indicate all 4 pollutant categories for each country. The parenting variable(from which the other categories will expand) will the the Country name, and then will come the AQI Category, CO AQI Category, Ozone AQI Category and PM2.5 Category")
# Prepare the data for the sunbusrt graph
sunburst_data = df.groupby(['Country', 'AQI Category', 'CO AQI Category', 'Ozone AQI Category', 'NO2 AQI Category', 'PM2.5 AQI Category']).size().reset_index(name='Count')
# Calculate total count for each country
country_counts = sunburst_data.groupby('Country')['Count'].sum().reset_index()
# Create a list of countries whose count is larger than 130
new_country = country_counts[country_counts['Count'] > 130]['Country'].tolist()
# create a new dataframe with only countries with count larger than 130
sunburst_dataf = sunburst_data[sunburst_data['Country'].isin(new_country)]
# Calculate the total count for each pollutant category within each country
sunburst_dataf = sunburst_dataf.groupby(['Country', 'CO AQI Category', 'Ozone AQI Category', 'NO2 AQI Category', 'PM2.5 AQI Category'])['Count'].sum().reset_index()
# Create the sunburst plot
fig5 = px.sunburst(
    sunburst_dataf,
    path=['Country', 'CO AQI Category', 'Ozone AQI Category', 'NO2 AQI Category', 'PM2.5 AQI Category'],
    values='Count',
    title='Distribution of AQI Values and Pollutants by Country',
    width=700,
    height=700
)

st.plotly_chart(fig5)

st.subheader('A more detailed analysis')
st.text("As as have various pollutants in the table, I belive that we can construct a matrix to look at the correlation between different pollutants and how their changes affect each other.\nI will create a separae df for the pollutants and calculate the correlation.")
st.code("pol_df = df[['CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']]\ncorr_matrix = pol_df.corr().round(2)")
pol_df = df[['CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']]
corr_matrix = pol_df.corr().round(2)
st.dataframe(corr_matrix)
st.text('And I will also create a heatmap to better visualize the correlation matrix.')
fig6 = px.imshow(corr_matrix, text_auto=True, title='Correlation Matrix of Pollutants and AQI', color_continuous_scale='haline')
st.plotly_chart(fig6)
st.text("As we can see from the heatmap:\n - PM2.5 has quite a strong positive correlation with all other pollutants.\n- NO2 has a pretty strong negative correlation with Ozone. This means that when the level of NO2 increases, the level of Ozone will decrease.")

st.subheader('Hypothesis proposition and testing')
st.markdown('''The hypothesis I'm considering is that :blue[**The larger the population of the city, the higher is the AQI Value.**]\nSince I don't have a "Population column in my dataset, I will get this column from an external source.''')

st.subheader('Gettign a new dataset for population')
c_df = pd.read_csv('Project/worldcities.csv')
c_df.rename(columns={'city' : 'City', 'population' : 'Population'}, inplace=True) # renaming the columns for consistency
c_sdf = c_df[['City', 'Population']].copy() # creating a smaller dataframe with only the necessary columns
st.code("c_df = pd.read_csv('Project/worldcities.csv')\nc.rename(columns={'city' : 'City', 'population' : 'Population'}, inplace=True)\nc_sdf = c_df[['City', 'Population']].copy()")

st.text("Let's also clean this dataframe from null's and duplicates:")
c_sdf.dropna(inplace=True) # drops rows with missing values
c_sdf.drop_duplicates(subset='City', inplace=True) # drops dublicates
c_sdf.reset_index(drop=True, inplace=True) # resets the indexes
st.code("c_sdf.dropna(inplace=True)\nc_sdf.drop_duplicates(subset='City', inplace=True)\nc_sdf.reset_index(drop=True)")

st.subheader("Merging the two datasets")
st.text("I will merge the population column from the second dataset into the original.")
dfm = df.merge(c_sdf, on='City', how='left').copy() # merging the two datasets
dfm.drop(3679, inplace=True) # drops american city Delhi as it causes chaos in the dataframe
st.code("dfm = df.merge(c_sdf, on='City', how='left').copy()")

st.text("Now let's check if any missing values have emerged after the merge:")
st.code('dfm.isnull().sum().sun()')
st.code(dfm.isnull().sum())

st.text("We can see that we have 92 missing values for the population column.\nI don't want to drop these values, so I will fill them in with mean values of the population column.")
dfm['Population'] = dfm['Population'].fillna(dfm['Population'].mean()) #filling in missing values with the mean population
dfm['Population'] = dfm['Population'].astype(int) # converting the float values to integers
st.code("dfm['Population'] = dfm['Population'].fillna(dfm['Population'].mean())\ndfm['Population'] = dfm['Population'].astype(int)")
st.code(dfm.isnull().sum().sum())

st.subheader("Visualizing the correlation between population and AQI Value")
st.text("Now let's create a scatter plot to visualize the correlation between AQI Value and Population.")
fig7 = px.scatter(dfm, x='Population', y='AQI Value', hover_name='City', title='Population vs AQI Value', color = 'AQI Value', color_continuous_scale='bluered', trendline='ols', trendline_color_override='#1aff1a')
st.plotly_chart(fig7)

st.text('From the scatter plot we can derive that therer are several dots in the top left corner indicating that despite having a relatively small population, their AQI Value is an astonishingly high value of 500.\nAnd if we look at the bottom right corner, Tokyo, despite its gargantuan population of 37 mil has a relatively low AQI Value of 79.')

st.markdown('''Since the hypothesis is proven to be :red[**incorrect**], it can be concluded that the AQI Value doesn't always depend on the Population of a city.''')

st.text("As we can see from the map, the largest dots not always have the highest values of AQI.\nThis could be due to various factors such as population density, geographical location, and the industialisation level of the city, since the pollutants in the table (PM2.5, NO2 and CO all get produced when the heavy industry is working.)")

st.text('This can actually be shown by this scatter map plot:')
fig8 = px.scatter_geo(dfm,
                     lat='lat',
                     lon='lng',
                     color='AQI Value',
                     size='Population',
                     hover_name='City',
                     title='Population vs AQI Value',
                     labels={'AQI Value': 'AQI Value', 'Population': 'Population'},
                     color_continuous_scale='Plasma',
                     )

st.plotly_chart(fig8)

st.subheader('Conclusion')
st.text("In conclusion, I have analyzed the AQI dataset and found that the AQI Value does not always depend on the population of a city. The AQI Value does not seem to have a strong correlation with the population, and the highest AQI values were observed in the top left corner of the scatter plot, indicating cities with a relatively small population and high pollution levels.")
