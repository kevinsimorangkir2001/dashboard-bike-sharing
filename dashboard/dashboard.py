import streamlit as st
import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style='ticks')
plt.style.use('ggplot')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe
def create_by_humidity_category_df(df):
    temp_cat_df = df.groupby("humidity_category").agg({"count_cr": "mean"}).reset_index()
    temp_cat_df.columns = ["humadity_category", "avg_cnt"]
    return temp_cat_df

def create_hourly_df(df):
    hourly_df = df.groupby(by=["hours"]).agg({
        "count_cr": "sum"
    }).reset_index()
    return hourly_df

def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return day_df_count_2011
def total_registered_df(day_df):
   reg_df =  day_df.groupby(by="dteday").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df
def total_casual_df(day_df):
   cas_df =  day_df.groupby(by="dteday").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df
def sum_order (hour_df):
    sum_order_items_df = hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# Load cleaned data
day_df = pd.read_csv("dashboard/day_fix.csv")
hour_df = pd.read_csv("dashboard/hour_fix.csv")

# Filter data
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo 
    st.image("BikeRental.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df["dteday"] >= str(start_date)) &
                       (day_df["dteday"] <= str(end_date))]

second_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                       (hour_df["dteday"] <= str(end_date))]


# # Menyiapkan berbagai dataframe
sum_order_items_df = sum_order(second_df)
humidity_category_df = create_by_humidity_category_df(second_df)
day_df_count_2011 = count_by_day_df(main_df)
reg_df = total_registered_df(main_df)
cas_df = total_casual_df(main_df)
hourly_df = create_hourly_df(second_df)

#bagian header dan jumlah
st.header(':bike: Bike Sharing Dashboard :bike:')
kolom1, kolom2, kolom3 = st.columns(3)

with kolom1:
    total_orders = day_df_count_2011.count_cr.sum()
    st.metric("Total Sharing Bike", value=total_orders)

with kolom2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_sum)

with kolom3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_sum)

#pertanyaan 1
st.subheader("Performa penyewaan sepeda perusahaan periode 2011-2012")
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    main_df["dteday"],
    main_df["count_cr"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
plt.title('Grafik Jumlah Pelanggan periode 2011-2012')
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#Pertanyaan 2
# Create the subplots
# Get the top 5 and bottom 5 hours
st.subheader("Performa penyewaan berdasarkan jam")
top_5_hours = sum_order_items_df.nlargest(5, 'count_cr')['hours']
bottom_5_hours = sum_order_items_df.nsmallest(5, 'count_cr')['hours']

# Filter the DataFrame for the top 5 and bottom 5 hours
top_5_df = sum_order_items_df[sum_order_items_df['hours'].isin(top_5_hours)]
bottom_5_df = sum_order_items_df[sum_order_items_df['hours'].isin(bottom_5_hours)]

# Create the subplots
fig2, ax2 = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Plot the top 5 hours
sns.barplot(x="hours", y="count_cr", data=top_5_df,
            palette=["#D3D3D3", "#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3"], ax=ax2[0])
ax2[0].set_ylabel(None)
ax2[0].set_xlabel("Hours (PM)", fontsize=30)
ax2[0].set_title("Jam dengan banyak penyewa sepeda", loc="center", fontsize=30)
ax2[0].tick_params(axis='y', labelsize=35)
ax2[0].tick_params(axis='x', labelsize=30, rotation=45)  # Rotate x-axis labels for better readability

# Plot the bottom 5 hours
sns.barplot(x="hours", y="count_cr", data=bottom_5_df,
            palette=["#D3D3D3", "#D3D3D3", "#D3D3D3","#90CAF9", "#D3D3D3"], ax=ax2[1])
ax2[1].set_ylabel(None)
ax2[1].set_xlabel("Hours (AM)", fontsize=30)
ax2[1].set_title("Jam dengan sedikit penyewa sepeda", loc="center", fontsize=30)
ax2[1].invert_xaxis()
ax2[1].yaxis.set_label_position("right")
ax2[1].yaxis.tick_right()
ax2[1].tick_params(axis='y', labelsize=35)
ax2[1].tick_params(axis='x', labelsize=30, rotation=45)  # Rotate x-axis labels for better readability

st.pyplot(fig2)


#pertanyaan 3
st.subheader("Jumlah Penyewa Sepeda berdasarkan Musim")
# membuat subplot dengan 1 baris dan 1 kolom, dengan ukuran (20, 10)
fig3, ax3 = plt.subplots(figsize=(20, 10))
# Calculate the average count_cr for each season
average_counts = main_df.groupby('season')['count_cr'].mean()
# Find the season with the maximum count_cr
max_season = average_counts.idxmax()
# Create a color mapping dictionary
color_map = {max_season: "#90CAF9"}  # Highlight the max season
for season in main_df['season'].unique():
    if season != max_season:
        color_map[season] = "#D3D3D3"
# Create the barplot with dynamic color assignment
sns.barplot(
    y="count_cr",
    x="season",
    data=main_df.sort_values(by="count_cr", ascending=False),
    palette=color_map,
    ax=ax3
)
# mengatur judul, label y dan x, serta tick params untuk subplot tersebut
ax3.set_title("Grafik Antar Musim", loc="center", fontsize=50)
ax3.set_ylabel(None)
ax3.set_xlabel(None)
ax3.tick_params(axis='x', labelsize=35)
ax3.tick_params(axis='y', labelsize=30)
# menampilkan plot
st.pyplot(fig3)


#pertanyaan 4
st.subheader("Perbandingan Customer yang Registered dengan casual")
# Menjumlahkan semua elemen dalam kolom casual
total_casual = sum(main_df['casual'])
# Menjumlahkan semua elemen dalam kolom registered
total_registered = sum(main_df['registered'])
# Membuat data untuk pie plot
data = [total_casual, total_registered]
labels = 'casual', 'registered'
sizes = [total_casual, total_registered]
explode = (0, 0.1)
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',colors=["#D3D3D3", "#90CAF9"],
        shadow=True, startangle=90)
ax1.axis('equal')

st.pyplot(fig1)


#pertanyaan 5
st.subheader("dampak humadity terhadap keputusan pengguna untuk menggunakan sepeda")
# Membuat grafik
fig5, ax5 = plt.subplots()
sns.barplot(x='humidity_category', y='count_cr', data=second_df, palette='viridis')
# Menambahkan judul dan label
plt.title('Rata-rata Penggunaan Sepeda Berdasarkan Kategori Humadity', fontsize=14)
plt.xlabel('Kategori Humidity', fontsize=12)
plt.ylabel('Rata-rata Penggunaan Sepeda', fontsize=12)
for container in ax5.containers:
    ax5.bar_label(container, fontsize=8, color='black', weight='bold', label_type='edge')
# Tampilkan grafik
plt.tight_layout()
st.pyplot(fig5)
with st.expander('Keterangan Kategori Humidity'):
    st.write(
        """
        `kering`: musim dingin
          
        `ideal`:  musim semi
        
        `lembab`: musim panas  
        """
    )



