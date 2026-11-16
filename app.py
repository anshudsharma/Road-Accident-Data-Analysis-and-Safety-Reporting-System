
import os
import shutil
import subprocess
from pathlib import Path
from analysis import (
    get_summary,
    # ... your existing imports ...
    mann_whitney_test,
    apriori_association
)
import streamlit as st
import pandas as pd

from dotenv import load_dotenv

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
DATA_DIR = PROJECT_DIR / "data"

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
# 3. LOAD DATA WITHOUT MYSQL
# ============================================================

POSSIBLE_DATA_FILES = [
    DATA_DIR / "road_accident_data.csv",
    DATA_DIR / "accident_records.csv",
    DATA_DIR / "data.csv",
    PROJECT_DIR / "road_accident_data.csv",
    PROJECT_DIR / "accident_records.csv",
    PROJECT_DIR / "data.csv",
    DATA_DIR / "road_accident_data.xlsx",
    PROJECT_DIR / "road_accident_data.xlsx"
]


def read_dataset(file_path):

    extension = Path(file_path).suffix.lower()

    if extension == ".csv":
        data = pd.read_csv(file_path)

    elif extension == ".xlsx":
        data = pd.read_excel(file_path, engine="openpyxl")

    else:
        raise ValueError(
            "Unsupported file format. Use CSV or XLSX."
        )

    if data.empty:
        raise ValueError("The dataset is empty.")

    return data


def find_local_dataset():

    for file_path in POSSIBLE_DATA_FILES:

        if file_path.is_file():
            return read_dataset(file_path)

    return None


def load_uploaded_dataset(uploaded_file):

    extension = Path(uploaded_file.name).suffix.lower()

    if extension == ".csv":
        data = pd.read_csv(uploaded_file)

    elif extension == ".xlsx":
        data = pd.read_excel(
            uploaded_file,
            engine="openpyxl"
        )

    else:
        raise ValueError(
            "Please upload a CSV or XLSX file."
        )

    if data.empty:
        raise ValueError("The uploaded dataset is empty.")

    return data


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

    r_path = shutil.which("Rscript")

    if r_path:
        return r_path

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
# 6. LOAD PROJECT DATA
# ============================================================

st.title("🚗 Road Accident Data Analysis")

st.caption(
    "Safety Reporting and Statistical Analysis System"
)

try:

    # Try loading an existing local dataset first
    df = find_local_dataset()

    # If no local dataset exists, allow upload
    if df is None:

        st.info(
            "No local dataset found. Upload your road accident dataset below."
        )

        uploaded_file = st.file_uploader(
            "Upload Road Accident Dataset",
            type=["csv", "xlsx"],
            help="Upload your accident dataset in CSV or Excel format."
        )

        if uploaded_file is None:

            st.warning(
                "Please upload your dataset to start the application."
            )

            st.stop()

        df = load_uploaded_dataset(uploaded_file)

    if "cleaned" not in st.session_state:
        st.session_state["cleaned"] = None

    st.success(
        f"Dataset loaded successfully! "
        f"Total records: {len(df)}"
    )

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
        st.warning(
            "Please go to Data Preprocessing and clean the dataset first!"
        )
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

    st.dataframe(
        df,
        use_container_width=True
    )

    if st.button(
        "🧹 Clean Dataset",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Scrubbing the data... Please wait."
            ):

                st.session_state["cleaned"] = preprocess_data(df)

            st.success(
                "Data preprocessing completed!"
            )

        except Exception as e:

            st.error(
                f"Data preprocessing failed: {e}"
            )

    if st.session_state["cleaned"] is not None:

        cleaned = st.session_state["cleaned"]

        st.subheader("Cleaned Dataset")

        st.dataframe(
            cleaned,
            use_container_width=True
        )

        st.subheader("Missing Values Before Cleaning")

        st.dataframe(df.isnull().sum())

        st.subheader("Dataset Information")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Original Records",
            len(df)
        )

        c2.metric(
            "Cleaned Records",
            len(cleaned)
        )

        c3.metric(
            "Columns",
            len(cleaned.columns)
        )

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
        st.warning(
            "Please go to Data Preprocessing and clean the dataset first!"
        )
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
        st.warning(
            "Please go to Data Preprocessing and clean the dataset first!"
        )
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

        st.error(
            f"Chi-square test error: {e}"
        )

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
            st.success(
                "Correlation is statistically significant."
            )
        else:
            st.info(
                "Correlation is not statistically significant."
            )

        if abs(corr["correlation"]) < 0.10:
            st.info("Negligible linear relationship.")

        elif abs(corr["correlation"]) < 0.30:
            st.info("Weak linear relationship.")

        elif abs(corr["correlation"]) < 0.50:
            st.info("Moderate linear relationship.")

        else:
            st.info("Relatively strong linear relationship.")

    except Exception as e:

        st.error(
            f"Correlation error: {e}"
        )
# ============================================================
# 12. ADVANCED STATS & APRIORI (PYTHON NATIVE)
# ============================================================

elif page == "🧪 R Statistical Analysis":

    cleaned = st.session_state["cleaned"]

    if cleaned is None:
        st.warning("Please go to Data Preprocessing and clean the dataset first!")
        st.stop()

    st.header("Advanced Statistical & Association Analysis")
    st.markdown("---")

    st.subheader("1. Mann-Whitney U Test")
    st.write("Compare the distribution of casualties between Fatal and Slight accidents.")

    try:
        mw_result = mann_whitney_test(cleaned, group_col='severity', target_col='casualties', group1='Fatal', group2='Minor')

        m1, m2, m3 = st.columns(3)
        m1.metric("U-Statistic", f"{mw_result['statistic']:.2f}")
        m2.metric("P-value", f"{mw_result['p_value']:.4f}")
        m3.metric("Sample Sizes", f"{mw_result['g1_size']} vs {mw_result['g2_size']}")

        if mw_result['p_value'] < 0.05:
            st.success("Statistically significant difference in casualties between Fatal and Slight accidents.")
        else:
            st.info("No statistically significant difference detected.")

    except Exception as e:
        st.warning("Could not run test. Ensure 'Severity' and 'Casualties' columns exist and contain 'Fatal' and 'Slight'.")

    st.markdown("---")

    st.subheader("2. Apriori Association Rules")
    st.write("Discover patterns and associations between Weather, Road Type, and Severity.")

    with st.spinner("Mining association rules..."):
        try:
            # Adjust these column names to match your exact dataset columns if needed
            cols_to_mine = ['weather', 'road_type', 'severity']

            rules = apriori_association(cleaned, cols_to_mine, min_support=0.05)

            if rules is not None and not rules.empty:
                st.dataframe(rules.head(15), use_container_width=True)
                st.success(f"Found {len(rules)} significant association rules!")
            else:
                st.info("No strong association rules found at the current support threshold.")

        except Exception as e:
            st.error(f"Apriori analysis failed: {e}. Check column names.")
