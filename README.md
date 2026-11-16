# 🚦 Road Accident Data Analysis and Safety Reporting System

## 1. Project Overview

The **Road Accident Data Analysis and Safety Reporting System** is a data analytics project developed using Python, R Programming, and Streamlit.

The main objective of this project is to analyze historical road accident data, identify accident patterns, understand factors contributing to accidents, and generate meaningful statistical reports to support road safety awareness and decision-making.

This project uses CSV files for data storage instead of a database, making it simple, lightweight, and easy to execute.

## 2. Technologies Used

| Technology    | Purpose                   |
| ------------- | ------------------------- |
| Python        | Data processing           |
| R Programming | Statistical analysis      |
| Streamlit     | Interactive dashboard     |
| Pandas        | Data manipulation         |
| NumPy         | Numerical operations      |
| Matplotlib    | Data visualization        |
| Seaborn       | Statistical visualization |
| ggplot2       | R visualization           |
| dplyr         | Data manipulation in R    |
| arules        | Association rule mining   |
| lubridate     | Date and time analysis    |
| CSV           | Data storage              |

## 3. Main Features

- CSV-based accident data management.
- Data cleaning and preprocessing using Python.
- Interactive Streamlit dashboard.
- Statistical analysis using R.
- Apriori association rule mining.
- Bayesian probability analysis.
- Monthly accident trend analysis.
- Accident severity visualization.
- Weather condition analysis.
- Road type analysis.
- Casualty distribution analysis.
- Statistical report generation.
- Data visualization and insights.

## 4. Statistical Analysis

The project implements the following statistical techniques:

1. Mann–Whitney U Test
2. Independent Samples T-Test
3. Shapiro–Wilk Normality Test
4. One-Way ANOVA
5. Kruskal–Wallis Test
6. Chi-Square Test
7. Fisher's Exact Test
8. Spearman Correlation

These statistical methods help identify differences, relationships, and patterns in road accident data.

## 5. Project Architecture

```text
       ROAD ACCIDENT DATA
               |
               v
          CSV DATASET
               |
               v
       PYTHON APPLICATION
               |
               v
      DATA CLEANING AND
        PREPROCESSING
               |
               v
         CLEANED DATA
               |
               v
        R ANALYSIS MODULE
               |
       +-------+-------+
       |       |       |
       v       v       v
  Statistical Apriori Bayesian
    Testing   Analysis Analysis
       |       |       |
       +-------+-------+
               |
               v
       TIME SERIES ANALYSIS
               |
               v
          GGPLOT2 CHARTS
               |
               v
       STREAMLIT DASHBOARD
               |
               v
       REPORT GENERATION
```

## 6. Project Folder Structure

```text
Road-Accident-Data-Analysis-and-Safety-Reporting-System/
│
├── app.py
├── README.md
├── requirements.txt
│
├── data/
│   └── road_accident_sample_500.csv
│
├── R/
│   └── statistical_analysis.R
│
├── reports/
│   └── plots/
│
└── .gitignore
```

## 7. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/Road-Accident-Data-Analysis-and-Safety-Reporting-System.git

cd Road-Accident-Data-Analysis-and-Safety-Reporting-System
```

Replace `your-username` with your actual GitHub username.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Alternatively, install the packages directly:

```bash
pip install streamlit pandas numpy matplotlib seaborn scipy
```

### Step 5: Install R Programming

Download and install R from the official website:

https://cran.r-project.org/

You can also install RStudio for a better development experience:

https://posit.co/download/rstudio-desktop/

### Step 6: Install Required R Packages

Open R or RStudio and execute:

```r
install.packages(c(
  "arules",
  "dplyr",
  "ggplot2",
  "lubridate"
))
```

### Step 7: Configure the Dataset

Place the road accident CSV dataset inside the `data/` directory.

Expected dataset path:

```text
data/road_accident_sample_500.csv
```

The application reads the accident records directly from the CSV file using Pandas.

### Step 8: Run the Application

Execute the following command in the terminal:

```bash
streamlit run app.py
```

The Streamlit application will open in your default web browser.

## 8. Project Outputs

The project generates the following outputs:

- Statistical test results.
- Apriori association rules.
- Bayesian probability estimates.
- Monthly accident statistics.
- Accident trend analysis.
- Accident severity visualization.
- Weather condition visualization.
- Road type visualization.
- Casualty distribution histogram.
- Statistical analysis reports.

## 9. Applications

- Identifying accident-prone conditions.
- Understanding relationships between weather and accident severity.
- Analyzing accident patterns across different road types.
- Studying monthly accident trends.
- Understanding accident severity distribution.
- Supporting road safety research and planning.
- Providing data-driven insights for road safety awareness.

## 10. Future Enhancements

- Real-time accident data integration.
- Interactive geographical accident maps.
- Automated PDF report generation.
- Accident hotspot detection.
- Advanced historical trend analysis.
- User authentication.
- Machine learning-based accident severity prediction.
- Accident risk prediction.

## 11. Important Notes

- This project uses CSV files for data storage.
- No MySQL or other database server is required.
- Statistical conclusions depend on dataset quality and size.
- Statistical associations do not establish causation.
- Statistical tests should be interpreted after checking their assumptions.
- Bayesian estimates depend on the selected prior distribution.
- Meaningful time-series analysis requires sufficient historical observations.
- This project is intended for educational and analytical purposes.

## 12. Author

**Project Name:** Road Accident Data Analysis and Safety Reporting System

**Technologies:** Python, R, Streamlit, Pandas, NumPy, CSV

**Domain:** Data Analytics and Road Safety

---

⭐ If you find this project useful, consider giving the repository a star on GitHub.
