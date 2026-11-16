import os
import shutil
import subprocess
from pathlib import Path

import streamlit as st
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL

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


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent
R_SCRIPT = PROJECT_DIR / "R" / "statistical_analysis.R"
REPORT_DIR = PROJECT_DIR / "reports"
PLOT_DIR = REPORT_DIR / "plots"

load_dotenv(PROJECT_DIR / ".env")

st.set_page_config(
    page_title="Road Accident Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.block-container {
    animation: fadeInScale 0.7s ease-out;
}

@keyframes fadeInScale {
    0% { opacity: 0; transform: scale(0.98) translateY(20px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}

h1 {
    background: linear-gradient(45deg, #FF4B4B, #FF8C00, #FF4B4B);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 600 !important;
}

div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 15px;
    padding: 20px;
    transition: all 0.3s ease;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    border-color: rgba(255,75,75,0.5);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111119 0%, #1e1e2f 100%);
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. MYSQL CONNECTION
# ============================================================

@st.cache_data(ttl=600, show_spinner="Connecting to MySQL...")
def load_data():

    required = [
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_HOST",
        "MYSQL_DATABASE"
    ]

    missing = [
        key for key in required if not os.getenv(key)
    ]

    if missing:
        raise ValueError(
            "Missing database settings: " + ", ".join(missing)
        )

    db_url = URL.create(
        drivername="mysql+mysqlconnector",
        username=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE")
    )

    engine = create_engine(db_url)

    try:
        return pd.read_sql(
            "SELECT * FROM accident_records",
            con=engine
        )
    finally:
        engine.dispose()


# ============================================================
# 4. FIND R EXECUTABLE
# ============================================================

def get_r_executable():

    configured_path = os.getenv("R_EXECUTABLE")

    if configured_path:
        if Path(configured_path).is_file():
            return configured_path

        raise FileNotFoundError(
            "R_EXECUTABLE path in .env does not exist."
        )

    # Search Rscript from system PATH
    r_path = shutil.which("Rscript")

    if r_path:
        return r_path

    # Common Windows installation locations
    if os.name == "nt":

        candidates = sorted(
            Path("C:/Program Files/R").glob(
                "*/bin/Rscript.exe"
            ),
            reverse=True
        )

        if candidates:
            return str(candidates[0])

    raise FileNotFoundError(
        "Rscript was not found. Install R or configure "
        "R_EXECUTABLE in your .env file."
    )


# ============================================================
# 5. RUN R STATISTICAL ENGINE
# ============================================================

def run_r_analysis():

    if not R_SCRIPT.is_file():
        raise FileNotFoundError(
            f"R script not found: {R_SCRIPT}"
        )

    r_exe = get_r_executable()

    result = subprocess.run(
        [r_exe, str(R_SCRIPT)],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr or result.stdout or
            "R script failed without an error message."
        )

    return result.stdout, result.stderr


# ============================================================
# 6. LOAD DATA
# ============================================================

st.title("🚗 Road Accident Data Analysis")

st.caption(
    "Safety Reporting and Statistical Analysis System"
)

try:
    df = load_data()

    # Initialize memory so Streamlit doesn't reset the cleaned data
    if "cleaned" not in st.session_state:
        st.session_state["cleaned"] = None

except Exception as e:
    st.error(f"Unable to load project data: {e}")
    st.stop()


# ============================================================
# 7. SIDEBAR NAVIGATION
# ============================================================

page = st.sidebar.radio(
    "Select Analysis Module:",
    [
        "📊 Dashboard",
        "⚙️ Data Preprocessing",
        "🗺️ Accident Analysis",
        "📈 Statistical Analysis",
        "🧪 R Statistical Analysis"
    ]
)


# ============================================================
# 8. DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    cleaned = st.session_state["cleaned"]
    if cleaned is None:
        st.warning(" Please go to  Data Preprocessing and clean the dataset first!")
        st.stop()

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

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Severity Distribution")
        st.bar_chart(severity_analysis(cleaned))

    with col2:
        st.subheader("Monthly Accident Trends")
        st.bar_chart(monthly_analysis(cleaned))


# ============================================================
# 9. DATA PREPROCESSING
# ============================================================

elif page == "⚙️ Data Preprocessing":

    st.header("Data Preprocessing")

    st.subheader("Original Dataset")
    st.dataframe(df, use_container_width=True)

    if st.button("🧹 Clean Dataset", type="primary", use_container_width=True):
        with st.spinner("Scrubbing the data... Please wait."):
            st.session_state["cleaned"] = preprocess_data(df)
        st.success("Data preprocessing completed!")

    if st.session_state["cleaned"] is not None:
        cleaned = st.session_state["cleaned"]

        st.subheader("Cleaned Dataset")
        st.dataframe(cleaned, use_container_width=True)

        st.subheader("Missing Values Before Cleaning")
        st.dataframe(df.isnull().sum())

        st.subheader("Dataset Information")

        c1, c2, c3 = st.columns(3)

        c1.metric("Original Records", len(df))
        c2.metric("Cleaned Records", len(cleaned))
        c3.metric("Columns", len(cleaned.columns))

        st.download_button(
            label="📥 Download Cleaned CSV",
            data=cleaned.to_csv(index=False),
            file_name="cleaned_accidents.csv",
            mime="text/csv"
        )


# ============================================================
# 10. ACCIDENT ANALYSIS
# ============================================================

elif page == "🗺️ Accident Analysis":

    cleaned = st.session_state["cleaned"]
    if cleaned is None:
        st.warning("⚠️ Please go to **⚙️ Data Preprocessing** and clean the dataset first!")
        st.stop()

    st.header("Exploratory Data Analysis")

    colA, colB = st.columns(2)

    with colA:

        st.subheader("Accidents by City")
        st.bar_chart(city_analysis(cleaned))

        st.subheader("Accidents by Weather")
        st.bar_chart(weather_analysis(cleaned))

        st.subheader("Accidents by Day")
        st.bar_chart(weekday_analysis(cleaned))

    with colB:

        st.subheader("Accidents by Cause")
        st.bar_chart(cause_analysis(cleaned))

        st.subheader("Accidents by Road Type")
        st.bar_chart(road_analysis(cleaned))

        st.subheader("Accidents by Time")
        st.bar_chart(time_analysis(cleaned))


# ============================================================
# 11. PYTHON STATISTICAL ANALYSIS
# ============================================================

elif page == "📈 Statistical Analysis":

    cleaned = st.session_state["cleaned"]
    if cleaned is None:
        st.warning("⚠️ Please go to **⚙️ Data Preprocessing** and clean the dataset first!")
        st.stop()

    st.header("Python Statistical Analysis")

    st.markdown("---")

    # CHI-SQUARE TEST

    st.subheader("1. Weather vs Accident Severity")

    try:

        result = severity_weather_test(cleaned)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Chi-square Statistic",
            f"{result['chi_square']:.3f}"
        )

        col2.metric(
            "P-value",
            f"{result['p_value']:.4f}"
        )

        col3.metric(
            "Degrees of Freedom",
            result["degrees_of_freedom"]
        )

        if result["cells_below_5"] > 0:

            st.warning(
                "Some expected cell counts are below 5. "
                "Interpret cautiously."
            )

        if result["p_value"] < 0.05:

            st.success(
                "Statistically significant association detected."
            )

        else:

            st.info(
                "No statistically significant association detected."
            )

        with st.expander("View Expected Frequencies"):
            st.dataframe(
                result["expected_frequencies"],
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Chi-square test error: {e}")

    st.markdown("---")

    # PEARSON CORRELATION

    st.subheader("2. Vehicles Involved vs Casualties")

    try:

        corr = casualties_correlation(cleaned)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Pearson Correlation",
            f"{corr['correlation']:.3f}"
        )

        col2.metric(
            "P-value",
            f"{corr['p_value']:.4f}"
        )

        col3.metric(
            "Sample Size",
            corr["sample_size"]
        )

        if corr["p_value"] < 0.05:
            st.success("Correlation is statistically significant.")
        else:
            st.info("Correlation is not statistically significant.")

        if abs(corr["correlation"]) < 0.10:
            st.info("Negligible linear relationship.")

        elif abs(corr["correlation"]) < 0.30:
            st.info("Weak linear relationship.")

        elif abs(corr["correlation"]) < 0.50:
            st.info("Moderate linear relationship.")

        else:
            st.info("Relatively strong linear relationship.")

    except Exception as e:
        st.error(f"Correlation error: {e}")


# ============================================================
# 12. R STATISTICAL ANALYSIS
# ============================================================

elif page == "🧪 R Statistical Analysis":

    st.header("R Statistical Analysis Engine")

    st.write(
        "Run statistical tests, Apriori association mining, "
        "Bayesian analysis, time-series analysis and ggplot2 "
        "visualizations using R."
    )

    st.markdown("---")

    # R MODULE INFORMATION

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Language", "R")
    col2.metric("Statistical Tests", "Multiple")
    col3.metric("Association", "Apriori")
    col4.metric("Visualization", "ggplot2")

    st.markdown("---")

    st.subheader("Analysis Modules")

    with st.expander("1. Statistical Testing", expanded=True):

        st.write("""
        - Mann-Whitney U Test
        - Independent T-test
        - Shapiro-Wilk Normality Test
        - One-way ANOVA
        - Kruskal-Wallis Test
        - Chi-square Test
        - Fisher Exact Test
        """)

    with st.expander("2. Apriori Association Analysis"):

        st.write("""
        - Frequent itemsets
        - Association rules
        - Support
        - Confidence
        - Lift
        - Minor severity association rules
        """)

    with st.expander("3. Bayesian Analysis"):

        st.write("""
        - Probability of fatal accidents
        - Weather-wise fatality probability
        - Beta-Binomial model
        - 95% credible intervals
        """)

    with st.expander("4. Time Series Analysis"):

        st.write("""
        - Monthly accident frequency
        - Monthly casualty totals
        - Moving averages
        - Linear trend analysis
        """)

    with st.expander("5. ggplot2 Visualizations"):

        st.write("""
        - Accident severity chart
        - Weather analysis chart
        - Road type chart
        - Monthly accident trend
        - Casualty distribution
        """)

    st.markdown("---")

    # EXECUTION BUTTON

    if st.button(
        "🚀 Run Complete R Statistical Analysis",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Running R statistical engine... Please wait."
            ):

                stdout, stderr = run_r_analysis()

            st.session_state["r_stdout"] = stdout
            st.session_state["r_stderr"] = stderr
            st.session_state["r_success"] = True

            st.success(
                "R statistical analysis completed successfully!"
            )

        except subprocess.TimeoutExpired:

            st.session_state["r_success"] = False
            st.error(
                "R analysis exceeded the 5-minute execution limit."
            )

        except Exception as e:

            st.session_state["r_success"] = False
            st.error(f"R execution failed: {e}")

    # DISPLAY R OUTPUT

    if st.session_state.get("r_success", False):

        st.markdown("---")
        st.subheader("R Statistical Results")

        stdout = st.session_state.get("r_stdout", "")

        st.code(stdout, language="text")

        stderr = st.session_state.get("r_stderr", "")

        if stderr.strip():
            with st.expander("R Warnings and Messages"):
                st.code(stderr, language="text")

        # DISPLAY GENERATED PLOTS

        st.markdown("---")
        st.subheader("R Data Visualizations (ggplot2)")

        plot_files = {
            "Accident Severity": "severity.png",
            "Weather Conditions": "weather.png",
            "Road Type": "road_type.png",
            "Monthly Accident Trend": "monthly_trend.png",
            "Casualty Distribution": "casualty_histogram.png"
        }

        available_plots = []

        for title, filename in plot_files.items():

            plot_path = PLOT_DIR / filename

            if plot_path.is_file():
                available_plots.append((title, plot_path))

        if available_plots:

            for i in range(0, len(available_plots), 2):

                columns = st.columns(2)

                for j, (title, path) in enumerate(
                    available_plots[i:i + 2]
                ):

                    with columns[j]:
                        st.write(f"**{title}**")
                        st.image(
                            str(path),
                            use_container_width=True
                        )

        else:

            st.info(
                "No ggplot2 images found. Update the R script "
                "to save charts inside reports/plots/."
            )

        # DOWNLOAD REPORT FILES

        st.markdown("---")
        st.subheader("Download R Analysis Reports")

        for filename in [
            "accident_analysis_data.csv",
            "bayesian_analysis.csv",
            "monthly_accident_analysis.csv"
        ]:

            file_path = REPORT_DIR / filename

            if file_path.is_file():

                with open(file_path, "rb") as file:

                    st.download_button(
                        label=f"📥 Download {filename}",
                        data=file.read(),
                        file_name=filename,
                        mime="text/csv",
                        key=f"download_{filename}"
                    )

    st.markdown("---")

    st.caption(
        "Python + R + MySQL + Streamlit"
    )
