
import streamlit as st
import pandas as pd

from preprocessing import preprocess_data

from analysis import (
    get_summary,
    severity_analysis,
    city_analysis,
    cause_analysis,
    monthly_analysis,
    weekday_analysis,
    weather_analysis,
    road_analysis,
    time_analysis,
    severity_weather_test,
    casualties_correlation
)

st.set_page_config(
    page_title="Road Accident Analytics",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Road Accident Data Analysis")
st.caption("Safety Reporting and Statistical Analysis System")

@st.cache_data
def load_data():
    return pd.read_csv("data/road_accident_sample_500.csv")

df = load_data()

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Analysis",
    [
        "Dashboard",
        "Data Preprocessing",
        "Accident Analysis",
        "Statistical Analysis"
    ]
)

cleaned = preprocess_data(df)

if page == "Dashboard":

    st.header("Accident Overview")

    summary = get_summary(cleaned)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Accidents", summary["Total Accidents"])
    c2.metric("Total Casualties", summary["Total Casualties"])
    c3.metric("Fatal Accidents", summary["Fatal Accidents"])
    c4.metric("Average Casualties", summary["Average Casualties"])

    st.subheader("Severity Distribution")
    st.bar_chart(severity_analysis(cleaned))

    st.subheader("Monthly Accident Trends")
    st.bar_chart(monthly_analysis(cleaned))

elif page == "Data Preprocessing":

    st.header("Data Preprocessing")

    st.write("Original dataset")
    st.dataframe(df)

    st.write("Cleaned dataset")
    st.dataframe(cleaned)

    st.write("Missing values before cleaning")
    st.dataframe(df.isnull().sum())

    st.success("Data cleaning completed.")

    st.download_button(
        "Download Cleaned CSV",
        cleaned.to_csv(index=False),
        "cleaned_accidents.csv",
        "text/csv"
    )

elif page == "Accident Analysis":

    st.header("Exploratory Data Analysis")

    st.subheader("Accidents by City")
    st.bar_chart(city_analysis(cleaned))

    st.subheader("Accidents by Main Cause")
    st.bar_chart(cause_analysis(cleaned))

    st.subheader("Accidents by Weather")
    st.bar_chart(weather_analysis(cleaned))

    st.subheader("Accidents by Road Type")
    st.bar_chart(road_analysis(cleaned))

    st.subheader("Accidents by Day of Week")
    st.bar_chart(weekday_analysis(cleaned))

    st.subheader("Accidents by Time of Day")
    st.bar_chart(time_analysis(cleaned))

elif page == "Statistical Analysis":

    st.header("Statistical Analysis")

    st.subheader("Weather vs Accident Severity")

    result = severity_weather_test(cleaned)

    st.write("Chi-square statistic:", result["chi_square"])
    st.write("P-value:", result["p_value"])
    st.write("Degrees of freedom:", result["degrees_of_freedom"])

    if result["p_value"] < 0.05:
        st.success("Statistically significant association found.")
    else:
        st.info("No statistically significant association found.")

    st.subheader("Vehicles Involved vs Casualties")

    corr = casualties_correlation(cleaned)

    st.write("Pearson correlation:", corr["correlation"])
    st.write("P-value:", corr["p_value"])

    st.info(
        "These tests describe associations in the sample. "
        "They do not establish causation or predict future accidents."
    )
