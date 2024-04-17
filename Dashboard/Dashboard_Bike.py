import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='white')

def create_hour_rent(hour_data):
    hour_data['dteday'] = pd.to_datetime(hour_data['dteday'])
    hour_data['yr'] = hour_data['dteday'].dt.year
    hour_data['mnth'] = hour_data['dteday'].dt.month
    
    hour_rent = hour_data.groupby(['yr', 'mnth']).agg({'hr': 'count'}).reset_index()
    return hour_rent

def create_daily_rent(day_data):
    day_data['dteday'] = pd.to_datetime(day_data['dteday'])
    day_data['yr'] = day_data['dteday'].dt.year
    day_data['mnth'] = day_data['dteday'].dt.month

    daily_rent= day_data.groupby(['yr', 'mnth']).agg({
        'registered': 'sum',
        'casual': 'sum',
        'cnt': 'sum'
    }).reset_index()
    return daily_rent

def create_hour_season(hour_data):
    season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    hour_season = hour_data.groupby("season")['instant'].nunique().reset_index()
    hour_season['season'] = hour_season['season'].map(season_mapping)
    return hour_season

def create_day_season(day_data):
    season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    
    day_season = day_data.groupby("season")['instant'].nunique().reset_index()
    day_season['season'] = day_season['season'].map(season_mapping)
    
    return day_season
 

def create_hour_weathersit(hour_data):
   
    weathersit_mapping = {
        1: "Clear, Few clouds",
        2: "Mist + Cloudy",
        3: "Light Snow",
        4: "Heavy Rain "
    }
    
    hour_weathersit = hour_data.groupby("weathersit")['instant'].nunique().sort_values(ascending=False).reset_index()
    hour_weathersit['weathersit'] = hour_weathersit['weathersit'].map(weathersit_mapping)
    
    return hour_weathersit

def create_day_weathersit(day_data):
 
    weathersit_mapping = {
        1: "Clear, Few clouds",
        2: "Mist + Cloudy",
        3: "Light Snow",
        4: "Heavy Rain"
    }
    
    day_weathersit = day_data.groupby("weathersit")['instant'].nunique().sort_values(ascending=False).reset_index()
    day_weathersit['weathersit'] = day_weathersit['weathersit'].map(weathersit_mapping)
    
    return day_weathersit

def create_hour_weekday(hour_data):
    weekday_mapping = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    hour_weekday = hour_data.groupby("weekday")['instant'].nunique().reset_index()
    hour_weekday['weekday'] = hour_weekday['weekday'].map(weekday_mapping)
    
    return hour_weekday

def create_day_weekday(day_data):
    weekday_mapping = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    day_weekday = day_data.groupby("weekday")['instant'].nunique().reset_index()
    day_weekday['weekday'] = day_weekday['weekday'].map(weekday_mapping)
    
    return day_weekday

# create_rfm_df() bertanggung jawab untuk menghasilkan rfm_df.
# Menghitung RFM Data Hour
def create_rfm_rent(rent_data):
    rfm_rent = rent_data.groupby(by="registered", as_index=False).agg({
        "dteday": "max",  # Mengambil tanggal order terakhir
        "instant": "nunique",
        "cnt" : "sum"
    })

    # Mengganti nama kolom
    rfm_rent.columns = ["registered", "max_rent_time", "frequency", "monetary"]

    # Menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_rent["max_rent_time"] = pd.to_datetime(rfm_rent["max_rent_time"])
    recent_date = rfm_rent["max_rent_time"].max().date()
    rfm_rent["recency"] = rfm_rent["max_rent_time"].apply(lambda x: (recent_date - x.date()).days)

    # Menghapus kolom 'max_order_timestamp'
    rfm_rent.drop("max_rent_time", axis=1, inplace=True)

    return rfm_rent



hour_data = pd.read_csv("hour.csv")
day_data = pd.read_csv("day.csv")


# Filter komponen (datetime (dteday))
dt_tgl = ["dteday"]
hour_data.sort_values(by="instant", inplace=True)
hour_data.reset_index(inplace=True)
 
for column in dt_tgl:
    hour_data[column] = pd.to_datetime(hour_data[column])

    
min_date = hour_data["dteday"].min()
max_date = hour_data["dteday"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("logo_bike.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rang Time',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_hour_data = hour_data[(hour_data["dteday"] >= str(start_date)) & 
                (hour_data["dteday"] <= str(end_date))]

main_day_data = day_data[(day_data["dteday"] >= str(start_date)) & 
                (day_data["dteday"] <= str(end_date))]

hour_rent = create_hour_rent(main_hour_data)
daily_rent = create_daily_rent(main_day_data)
hour_season = create_hour_season(main_hour_data)
day_season = create_day_season(main_day_data)
weathersit_hour = create_hour_weathersit(main_hour_data)
weathersit_day= create_day_weathersit(main_day_data)
weekday_hour = create_hour_weekday(main_hour_data)
weekday_day = create_day_weekday(main_day_data)
rfm_rent = create_rfm_rent(main_hour_data)

st.header('Bike Rental Dashboard')
#Visualisasi Data 
st.subheader('Perfomance Rent per Month')
hour_rent_data = create_hour_rent(hour_data)
total_hour_rent = hour_data['hr'].sum()
col1 = st.columns(1)[0]
with col1:
    st.metric("Total Rental Hours", value=total_hour_rent)
fig, axs = plt.subplots(figsize=(15, 5))

for year in hour_rent_data['yr'].unique():
    year_data = hour_rent_data[hour_rent_data['yr'] == year]
    axs.plot(year_data['mnth'], year_data['hr'], label=year)

axs.set_title('Number of Bike Rental (Hour) By Month in 2011, 2012')
axs.set_xlabel('Bulan')
axs.set_ylabel('Number of Rental Bike (Hour)')
axs.set_xticks(range(1, 13))
axs.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
axs.legend(title='Tahun')
axs.grid(True)
# Mendapatkan total jam sewa dari seluruh data
st.pyplot(fig)

# Customer Demographics
st.subheader('Perfomance Rent by User per Month')
result_day_usr = create_daily_rent(day_data)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Registered", value=result_day_usr['registered'].sum())

with col2:
    st.metric("Casual", value=result_day_usr['casual'].sum())

with col3:
    st.metric("Total", value=result_day_usr['cnt'].sum())
axs.plot(result_day_usr.index, result_day_usr['registered'], label='Registered', marker='o')
axs.plot(result_day_usr.index, result_day_usr['casual'], label='Casual', marker='o')
axs.plot(result_day_usr.index, result_day_usr['cnt'], label='Total', marker='o')
axs.set_title('Number of User Bike Rental (Day) by month')
axs.set_xlabel('Bulan')
axs.set_ylabel('Number of Rental Bike (Day)')
axs.set_xticks(range(len(result_day_usr)))
axs.set_xticklabels(result_day_usr['mnth'].astype(str) + '/' + result_day_usr['yr'].astype(str), rotation=45)
axs.legend()
plt.tight_layout()
st.pyplot(fig)

# Season Demographics 
st.subheader("Season Demographics")
hour_season_data = create_hour_season(hour_data)
day_season_data = create_day_season(day_data)
col1, col2, col3, col4 = st.columns(4)

# Musim dengan jumlah penyewaan terbanyak
max_hour_season = hour_season_data.loc[hour_season_data['instant'].idxmax()]
with col1:
    st.write(f"Most Rental (Hour) in Season: {max_hour_season['season']}")
    st.write(f"Number of Rental (Hour): {max_hour_season['instant']}")

max_day_season = day_season_data.loc[day_season_data['instant'].idxmax()]
with col2:
    st.write(f"Most Rental (Day) in Season: {max_day_season['season']}")
    st.write(f"Number of Rental (Day): {max_day_season['instant']}")

# Musim dengan jumlah penyewaan terendah
min_hour_season = hour_season_data.loc[hour_season_data['instant'].idxmin()]
with col3:
    st.write(f"Least Rental (Hour) in Season: {min_hour_season['season']}")
    st.write(f"Number of Rental (Hour): {min_hour_season['instant']}")

min_day_season = day_season_data.loc[day_season_data['instant'].idxmin()]
with col4:
    st.write(f"Least Rental (Day) in Season: {min_day_season['season']}")
    st.write(f"Number of Rental (Day): {min_day_season['instant']}")

# Season Demographics (Hour)
fig, axs = plt.subplots(1, 2, figsize=(15, 5))
bar_color = ["#B0C4DE", "#B0C4DE","#00BFFF","#B0C4DE"]
axs[0].barh(hour_season_data['season'], hour_season_data['instant'], color=bar_color, edgecolor='black')
axs[0].set_xlim(0, hour_season_data['instant'].max() + 100)
axs[0].set_ylabel('Season')
axs[0].set_xlabel('Number of Rental Bike (Hour) by Season')
axs[0].set_title("Number of Bike Rental (Hour) by Season")
plt.tight_layout()

# Season Demographics (Day)
bar_color = ["#B0C4DE", "#B0C4DE","#00BFFF", "#B0C4DE"]
axs[1].barh(day_season_data['season'], day_season_data['instant'], color=bar_color, edgecolor='black')
axs[1].set_xlim(0, day_season_data['instant'].max() + 5)
axs[1].set_ylabel('Season')
axs[1].set_xlabel('Number of Rental Bike (Day) by Season')
axs[1].set_title("Number of Bike Rental (Day) by Season")
plt.tight_layout()
st.pyplot(fig)


# Weahersit Demographics 
st.subheader("Weather Situation Demographics ")
hour_weathersit_data = create_hour_weathersit(hour_data)
day_weathersit_data = create_day_weathersit(day_data)
fig, axs = plt.subplots(1, 2, figsize=(15, 5))

# Menampilkan informasi situasi cuaca dengan jumlah penyewaan terbanyak dan terendah
col1, col2, col3, col4 = st.columns(4)

# Situasi cuaca dengan jumlah penyewaan terbanyak
max_hour_weathersit = hour_weathersit_data.loc[hour_weathersit_data['instant'].idxmax()]
with col1:
    st.write(f"Most Rental (Hour) in Situation: {max_hour_weathersit['weathersit']}")
    st.write(f"Number of Rental (Hour): {max_hour_weathersit['instant']}")

max_day_weathersit = day_weathersit_data.loc[day_weathersit_data['instant'].idxmax()]
with col2:
    st.write(f"Most Rental (Day) in Weather Situation: {max_day_weathersit['weathersit']}")
    st.write(f"Number of Rental (Day): {max_day_weathersit['instant']}")

# Situasi cuaca dengan jumlah penyewaan terendah
min_hour_weathersit = hour_weathersit_data.loc[hour_weathersit_data['instant'].idxmin()]
with col3:
    st.write(f"Least Rental (Hour) in Weather Situation: {min_hour_weathersit['weathersit']}")
    st.write(f"Number of Rental (Hour): {min_hour_weathersit['instant']}")

min_day_weathersit = day_weathersit_data.loc[day_weathersit_data['instant'].idxmin()]
with col4:
    st.write(f"Least Rental (Day) in Weather Situation: {min_day_weathersit['weathersit']}")
    st.write(f"Number of Rental (Day): {min_day_weathersit['instant']}")

# Weahersit Demographics (Hour)
bar_color = ["#00BFFF", "#B0C4DE", "#B0C4DE", "#B0C4DE"]
axs[0].bar(hour_weathersit_data['weathersit'], hour_weathersit_data['instant'], color=bar_color, edgecolor='black')
axs[0].set_xlabel('Weather Situation')
axs[0].set_ylabel('Number of Rental (Hour)')
axs[0].set_title("Number of Rental (Hour) by Weather Situation", loc="center", fontsize=12)
plt.tight_layout()

# Weahersit Demographics
bar_color = ["#00BFFF", "#B0C4DE", "#B0C4DE"]
axs[1].bar(day_weathersit_data['weathersit'], day_weathersit_data['instant'], color=bar_color, edgecolor='black')
axs[1].set_xlabel('Weather Situation')
axs[1].set_ylabel('Number of Rental (Day)')
axs[1].set_title("Number of Rental (Day) by Weather Situation", loc="center", fontsize=12)
plt.tight_layout()
st.pyplot(fig)


st.subheader("Weekday Demographics")

fig, axs = plt.subplots(1, 2, figsize=(15, 5))
hour_weekday_data = create_hour_weekday(hour_data)
day_weekday_data = create_day_weekday(day_data)

# Menampilkan informasi hari dalam seminggu dengan jumlah penyewaan terbanyak dan terendah
col1, col2, col3, col4 = st.columns(4)

# Hari dalam seminggu dengan jumlah penyewaan terbanyak
max_hour_weekday = hour_weekday_data.loc[hour_weekday_data['instant'].idxmax()]
with col1:
    st.write(f"Most Rental (Hour) in Weekday: {max_hour_weekday['weekday']}")
    st.write(f"Number of Rental (Hour): {max_hour_weekday['instant']}")

max_day_weekday = day_weekday_data.loc[day_weekday_data['instant'].idxmax()]
with col2:
    st.write(f"Most Rental (Day) in Weekday: {max_day_weekday['weekday']}")
    st.write(f"Number of Rental (Day): {max_day_weekday['instant']}")

# Hari dalam seminggu dengan jumlah penyewaan terendah
min_hour_weekday = hour_weekday_data.loc[hour_weekday_data['instant'].idxmin()]
with col3:
    st.write(f"Least Rental (Hour) in Weekday: {min_hour_weekday['weekday']}")
    st.write(f"Number of Rental (Hour): {min_hour_weekday['instant']}")

min_day_weekday = day_weekday_data.loc[day_weekday_data['instant'].idxmin()]
with col4:
    st.write(f"Least Rental (Day) in Weekday: {min_day_weekday['weekday']}")
    st.write(f"Number of Rental (Day): {min_day_weekday['instant']}")
# Weekday Demographics (Hour)
line_color = "#4682B4"
axs[0].plot(hour_weekday_data['weekday'], hour_weekday_data['instant'], color=line_color, marker='o', linestyle='-')
axs[0].set_xlabel('weekday')
axs[0].set_ylabel('Number of Rental Bike (Hour)')
axs[0].set_xticks(hour_weekday_data['weekday'])
axs[0].set_xticklabels(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
axs[0].set_title("Number of Bike Rental (Hour) by weekday", loc="center", fontsize=14)

# Demografi weekday day

line_color = "#6A5ACD"
axs[1].plot(day_weekday_data['weekday'], day_weekday_data['instant'], color=line_color, marker='o', linestyle='-')
axs[1].set_xlabel('Weekday')
axs[1].set_ylabel('Number of Rental (Day)')
axs[1].set_xticks(day_weekday_data['weekday'])
axs[1].set_xticklabels(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
axs[1].set_title("Number of Bike Rental (Hour) by weekday", loc="center", fontsize=14)

plt.tight_layout()
st.pyplot(fig)


#Demografi RFM Analysis (hour)
st.subheader("RFM Analysis")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_rent.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_rent.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_rent.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_monetary)

rfm_rent = create_rfm_rent(hour_data)
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

# Histogram untuk Recency
axs[0].hist(rfm_rent['recency'], bins=20, color='skyblue', edgecolor='black')
axs[0].set_title('Recency Distribution')
axs[0].set_xlabel('Recency (days)')
axs[0].set_ylabel('Frequency')

# Histogram untuk Frequency
axs[1].hist(rfm_rent['frequency'], bins=20, color='lightgreen', edgecolor='black')
axs[1].set_title('Frequency Distribution')
axs[1].set_xlabel('Frequency')
axs[1].set_ylabel('Frequency')

# Histogram untuk Monetary
axs[2].hist(rfm_rent['monetary'], bins=20, color='salmon', edgecolor='black')
axs[2].set_title('Monetary Distribution')
axs[2].set_xlabel('Monetary')
axs[2].set_ylabel('Frequency')

plt.tight_layout()
st.pyplot(fig)