import subprocess
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import time

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
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Main Container Slide & Fade */
    .block-container {
        animation: fadeInScale 0.7s ease-out;
    }
    @keyframes fadeInScale {
        0% { opacity: 0; transform: scale(0.98) translateY(20px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }

    /* Glowing Animated Gradient Title */
    h1 {
        background: linear-gradient(45deg, #FF4B4B, #FF8C00, #FF4B4B);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s linear infinite;
        font-weight: 600 !important;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    /* Glassmorphism Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 20px rgba(255, 75, 75, 0.15);
        border-color: rgba(255, 75, 75, 0.5);
    }

    /* Sleek Sidebar Navigation Redesign */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111119 0%, #1e1e2f 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Animated Sidebar Radio Buttons */
    div[role="radiogroup"] > label {
        padding: 12px 20px;
        margin-bottom: 8px;
        border-radius: 10px;
        background: rgba(255,255,255,0.02);
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    div[role="radiogroup"] > label:hover {
        background: rgba(255, 75, 75, 0.1);
        border: 1px solid rgba(255, 75, 75, 0.3);
        transform: translateX(8px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Road Accident Data Analysis")
st.caption("Safety Reporting and Statistical Analysis System")


# --------------------------------------------------
# LOAD DATA FROM MYSQL
# --------------------------------------------------

@st.cache_data(ttl=600, show_spinner="🔗 Fetching data from MySQL... ⏳")
def load_data():
    load_dotenv()
    db_url = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
    engine = create_engine(db_url)

    # Just grab the data directly, no manual UI status inside the cache!
    df = pd.read_sql("SELECT * FROM accident_records", con=engine)
    return df

df = load_data()
cleaned = preprocess_data(df)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
st.sidebar.title("Navigation 🧭")


page = st.sidebar.radio(
    "Select Analysis Module:",
    [
        "📊 Dashboard",
        "⚙️ Data Preprocessing",
        "🗺️ Accident Analysis",
        "📈 Statistical Analysis"
    ]
)


st.toast(f"Launched {page.replace('📊', '').replace('⚙️', '').replace('🗺️', '').replace('📈', '').strip()} Engine", icon="🚀")


# --------------------------------------------------
# 1. DASHBOARD
# --------------------------------------------------

if page == "📊 Dashboard":

    st.balloons()
    st.header("Accident Overview")

    summary = get_summary(cleaned)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Accidents", summary["Total Accidents"])
    c2.metric("Total Casualties", summary["Total Casualties"])
    c3.metric("Fatal Accidents", summary["Fatal Accidents"])
    c4.metric("Average Casualties", summary["Average Casualties"])

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Severity Distribution")
        st.bar_chart(severity_analysis(cleaned))

    with col2:
        st.subheader("Monthly Accident Trends")
        st.bar_chart(monthly_analysis(cleaned))


# --------------------------------------------------
# 2. DATA PREPROCESSING
# --------------------------------------------------

elif page == "⚙️ Data Preprocessing":

    st.header("Data Preprocessing")

    st.subheader("Original Dataset")
    st.dataframe(df, use_container_width=True)

    st.subheader("Cleaned Dataset")
    st.dataframe(cleaned, use_container_width=True)

    st.subheader("Missing Values Before Cleaning")
    st.dataframe(df.isnull().sum())

    st.success("Data cleaning completed successfully. Sparkly clean! ✨")

    st.download_button(
        label="📥 Download Cleaned CSV",
        data=cleaned.to_csv(index=False),
        file_name="cleaned_accidents.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# 3. ACCIDENT ANALYSIS
# --------------------------------------------------

elif page == "🗺️ Accident Analysis":

    st.header("Exploratory Data Analysis")

    st.markdown("---")

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Accidents by City")
        st.bar_chart(city_analysis(cleaned))

        st.subheader("Accidents by Weather")
        st.bar_chart(weather_analysis(cleaned))

        st.subheader("Accidents by Day of Week")
        st.bar_chart(weekday_analysis(cleaned))

    with colB:
        st.subheader("Accidents by Main Cause")
        st.bar_chart(cause_analysis(cleaned))

        st.subheader("Accidents by Road Type")
        st.bar_chart(road_analysis(cleaned))

        st.subheader("Accidents by Time of Day")
        st.bar_chart(time_analysis(cleaned))


# --------------------------------------------------
# 4. STATISTICAL ANALYSIS
# --------------------------------------------------

elif page == "📈 Statistical Analysis":

    st.header("Statistical Analysis")
    st.markdown("---")

    # CHI-SQUARE TEST
    st.subheader("1. Weather vs Accident Severity")

    result = severity_weather_test(cleaned)

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("Chi-square Statistic", f"{result['chi_square']:.3f}")
    col_stat2.metric("P-value", f"{result['p_value']:.4f}")
    col_stat3.metric("Degrees of Freedom", result["degrees_of_freedom"])

    if result["cells_below_5"] > 0:
        st.warning("Some expected cell counts are below 5. Interpret cautiously.")
    elif result["p_value"] < 0.05:
        st.success("There is a statistically significant association between weather and accident severity.")
    else:
        st.info("No statistically significant association was detected.")

    with st.expander("View Expected Frequency Table"):
        st.dataframe(result["expected_frequencies"], use_container_width=True)

    st.markdown("---")
    st.subheader("3. Advanced Market Basket Analysis (Powered by R)")

    if st.button("🚀 Run R Statistical Engine"):
        with st.spinner("Crunching Apriori rules and Mann-Whitney tests in R... ⏳"):
            try:
                # The exact command that worked in your terminal
                r_exe = r"C:\Program Files\R\R-4.6.2\bin\Rscript.exe"
                r_script = r"R\statistical_analysis.R"

                # Execute R script in the background
                result = subprocess.run(
                    [r_exe, r_script],
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Display the raw R output beautifully inside a code block
                st.success("R Script Executed Successfully!")
                st.code(result.stdout, language="markdown")

            except subprocess.CalledProcessError as e:
                st.error("The R script encountered an error, sir:")
                st.code(e.stderr, language="bash")
            except FileNotFoundError:
                st.error("Could not locate the R executable. Check the path, sir!")

    # PEARSON CORRELATION
    st.subheader("2. Vehicles Involved vs Casualties")

    corr = casualties_correlation(cleaned)

    col_corr1, col_corr2, col_corr3 = st.columns(3)
    col_corr1.metric("Pearson Correlation", f"{corr['correlation']:.3f}")
    col_corr2.metric("P-value", f"{corr['p_value']:.4f}")
    col_corr3.metric("Sample Size", corr["sample_size"])

    if corr["p_value"] < 0.05:
        st.success("The linear correlation is statistically significant.")
    else:
        st.error("The linear correlation is not statistically significant.")

    if abs(corr["correlation"]) < 0.10:
        st.info("The observed linear relationship is negligible.")
    elif abs(corr["correlation"]) < 0.30:
        st.info("The observed linear relationship is weak.")
    elif abs(corr["correlation"]) < 0.50:
        st.info("The observed linear relationship is moderate.")
    else:
        st.info("The observed linear relationship is relatively strong.")
