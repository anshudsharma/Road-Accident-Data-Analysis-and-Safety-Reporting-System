
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


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("data/road_accident_sample_500.csv")


df = load_data()

# Preprocess dataset
cleaned = preprocess_data(df)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

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


# --------------------------------------------------
# 1. DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.header("Accident Overview")

    summary = get_summary(cleaned)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Accidents",
        summary["Total Accidents"]
    )

    c2.metric(
        "Total Casualties",
        summary["Total Casualties"]
    )

    c3.metric(
        "Fatal Accidents",
        summary["Fatal Accidents"]
    )

    c4.metric(
        "Average Casualties",
        summary["Average Casualties"]
    )

    st.subheader("Severity Distribution")
    st.bar_chart(severity_analysis(cleaned))

    st.subheader("Monthly Accident Trends")
    st.bar_chart(monthly_analysis(cleaned))


# --------------------------------------------------
# 2. DATA PREPROCESSING
# --------------------------------------------------

elif page == "Data Preprocessing":

    st.header("Data Preprocessing")

    st.subheader("Original Dataset")
    st.dataframe(df, use_container_width=True)

    st.subheader("Cleaned Dataset")
    st.dataframe(cleaned, use_container_width=True)

    st.subheader("Missing Values Before Cleaning")
    st.dataframe(df.isnull().sum())

    st.success("Data cleaning completed successfully.")

    st.download_button(
        label="Download Cleaned CSV",
        data=cleaned.to_csv(index=False),
        file_name="cleaned_accidents.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# 3. ACCIDENT ANALYSIS
# --------------------------------------------------

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


# --------------------------------------------------
# 4. STATISTICAL ANALYSIS
# --------------------------------------------------

elif page == "Statistical Analysis":

    st.header("Statistical Analysis")

    # CHI-SQUARE TEST

    st.subheader("1. Weather vs Accident Severity")

    result = severity_weather_test(cleaned)

    st.metric(
        "Chi-square Statistic",
        f"{result['chi_square']:.3f}"
    )

    st.metric(
        "P-value",
        f"{result['p_value']:.4f}"
    )

    st.write(
        "Degrees of Freedom:",
        result["degrees_of_freedom"]
    )

    st.write(
        "Minimum Expected Frequency:",
        f"{result['minimum_expected']:.2f}"
    )

    st.write(
        "Expected Cells Below 5:",
        result["cells_below_5"]
    )

    if result["cells_below_5"] > 0:

        st.warning(
            "Some expected cell counts are below 5. "
            "Interpret the chi-square result cautiously. "
            "Consider combining sparse categories or using "
            "an appropriate exact or simulation-based test."
        )

    elif result["p_value"] < 0.05:

        st.success(
            "There is a statistically significant association "
            "between weather and accident severity."
        )

    else:

        st.info(
            "No statistically significant association was "
            "detected between weather and accident severity."
        )

    st.write("Expected Frequency Table")
    st.dataframe(
        result["expected_frequencies"],
        use_container_width=True
    )


    # PEARSON CORRELATION

    st.subheader("2. Vehicles Involved vs Casualties")

    corr = casualties_correlation(cleaned)

    st.metric(
        "Pearson Correlation",
        f"{corr['correlation']:.3f}"
    )

    st.metric(
        "P-value",
        f"{corr['p_value']:.4f}"
    )

    st.write(
        "Sample Size:",
        corr["sample_size"]
    )

    if corr["p_value"] < 0.05:

        st.write(
            "The linear correlation is statistically significant."
        )

    else:

        st.write(
            "The linear correlation is not statistically significant."
        )

    if abs(corr["correlation"]) < 0.10:

        st.info(
            "The observed linear relationship is negligible."
        )

    elif abs(corr["correlation"]) < 0.30:

        st.info(
            "The observed linear relationship is weak."
        )

    elif abs(corr["correlation"]) < 0.50:

        st.info(
            "The observed linear relationship is moderate."
        )

    else:

        st.info(
            "The observed linear relationship is relatively strong."
        )

    st.warning(
        "These results describe the available sample only. "
    )
