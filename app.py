from numpy.lib.function_base import average
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

st.set_page_config(layout = "wide")

DATA_URL = ("mvc_update.csv")

st.title("EDA of Vehicle Accidents in the City of New York")

expand_bar = st.beta_expander("Features")
expand_bar.markdown("""
This webapp displays various visualizations of motor vehicle collisions in NYC. Features include :
* Selection of **Number of Injuries** to be displayed on the 2D map.
* Selection of **Time of Day** which displays the number of collisions in that time of day as a 3D bar graph overlayed on the second map. 
* A **Per-Minute Breakdown** of accidents that rook place in the selected 'Time of Day' using a Bar Graph.
* A table of **Most Dangerous Streets** that can be tailored to the type of person : Pedestrian, Motorist or Cyclist.
* A button also enables the user to view the enitre dataframe after all the user modifiations have been done.
* For a better experience, set the theme to 'Custom Theme'.

**Data Source:** [NYC OpenData](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/data)
""")

expand_bar = st.beta_expander("Known Bugs")
expand_bar.markdown("""
* The DeckGL Map (Map #2) hangs randomly. Hit Refresh to temporarily fix it.
""")

@st.cache(persist = True)
def load_data2(nrows):
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates= [['CRASH DATE', 'CRASH TIME']])
    data.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace = True)
    data.columns = data.columns.str.replace(' ','_')
    data.rename(columns = {'crash_date_crash_time' : 'date/time'}, inplace = True)
    return data

data = load_data2(20000)
copy_data = data

st.sidebar.header('Changeable Filters')

st.header('Map #1 for displaying accidents according to selected injured people :')
st.sidebar.subheader("Select the number of injuries for Map #1 :")
injured_people = st.sidebar.slider('', 0, 17)
st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how = "any"))



st.sidebar.subheader("Select an hour of the day for Map #2 :")
hour = st.sidebar.slider('', 0, 23)
data = data[data['date/time'].dt.hour == hour]

midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.header('Map #2 for displaying the number of injuries according to the select time of day :')

st.write(pdk.Deck(
    map_style = 'mapbox://styles/mapbox/dark-v9',
    initial_view_state = {
        'latitude' : midpoint[0],
        'longitude' : midpoint[1],
        'zoom' : 11,
        'pitch' : 50,
    },

    layers = [
        pdk.Layer(
        "HexagonLayer",
        data = data[['date/time', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,
        pickable = True,
        elevation_scale = 4,
        elevation_range = [0,1000],
        ),
    ]
))

st.header('Breakdown per minute between %i:00 and %i:00' % (hour, (hour + 1) %24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]

hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range = (0, 60))[0]
chart_date = pd.DataFrame({'minute': range(60), 'crashes' : hist})
fig = px.bar(chart_date, x = 'minute', y = 'crashes', hover_data = ['minute', 'crashes'], height = 400)

st.write(fig)

st.header('Most Dangerous Streets w.r.t Vehicle Collisions')
select = st.selectbox('Type of person : ', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(copy_data.query('number_of_pedestrians_injured >= 1')[['on_street_name', 'number_of_pedestrians_injured']].sort_values(by = ['number_of_pedestrians_injured'], ascending = False).dropna(how = 'any'))

elif select == 'Cyclists':
    st.write(copy_data.query('number_of_cyclist_injured >= 1')[['on_street_name', 'number_of_cyclist_injured']].sort_values(by = ['number_of_cyclist_injured'], ascending = False).dropna(how = 'any'))

else :
    st.write(copy_data.query('number_of_motorist_injured >= 1')[['on_street_name', 'number_of_motorist_injured']].sort_values(by = ['number_of_motorist_injured'], ascending = False).dropna(how = 'any'))

if st.button('Show Raw Data'):
    st.subheader('Raw Dataframe')
    st.write(data)