# Road Accident Data Analysis and Safety Reporting System

## 1. Project Overview

The **Road Accident Data Analysis and Safety Reporting System** is a data analytics project developed using Python, R, Streamlit, and MySQL.

The main objective is to analyze historical road accident data, identify accident patterns, understand factors contributing to accidents, and generate meaningful statistical reports to support road safety awareness and decision-making.

## 2. Technologies Used

| Technology          | Purpose                 |
| ------------------- | ----------------------- |
| Python              | Data processing         |
| R Programming       | Statistical analysis    |
| Streamlit           | Interactive dashboard   |
| MySQL               | Database management     |
| Pandas              | Data manipulation       |
| NumPy               | Numerical operations    |
| Matplotlib, Seaborn | Data visualization      |
| ggplot2             | R visualization         |
| dplyr               | Data manipulation in R  |
| arules              | Association rule mining |
| lubridate           | Date and time analysis  |

## 3. Main Features

- Accident data management using MySQL.
- Data cleaning and preprocessing using Python.
- Interactive Streamlit dashboard.
- Statistical analysis using R.
- Apriori association rule mining.
- Bayesian probability analysis.
- Monthly accident trend analysis.
- Data visualization and report generation.

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

## 5. Project Architecture

```text
       ROAD ACCIDENT DATA
                |
                v
         MYSQL DATABASE
                |
                v
       PYTHON APPLICATION
                |
                v
        DATA PROCESSING
                |
                v
         CLEANED DATA
                |
                v
        R ANALYSIS MODULE
                |
       +--------+--------+
       |        |        |
       v        v        v
   Statistical Apriori Bayesian
     Testing   Analysis Analysis
       |        |        |
       +--------+--------+
                |
                v
        TIME SERIES ANALYSIS
                |
                v
          GGPLOT2 CHARTS
                |
                v
        STREAMLIT DASHBOARD
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

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install R

Download and install R:

https://cran.r-project.org/

### Step 5: Install Required R Packages

Open R or RStudio and execute:

```r
install.packages(c(
  "arules",
  "dplyr",
  "ggplot2",
  "lubridate"
))
```

### Step 6: Configure MySQL

Create the project database:

```sql
CREATE DATABASE road_accident_db;
```

Configure your MySQL connection credentials in the Python application.

### Step 7: Run the Application

```bash
streamlit run app.py
```

## 8. Project Outputs

- Statistical test results.
- Apriori association rules.
- Bayesian probability estimates.
- Monthly accident statistics.
- Accident trend analysis.
- Accident severity visualization.
- Weather condition visualization.
- Road type visualization.
- Casualty distribution histogram.

## 9. Applications

- Identifying accident-prone conditions.
- Understanding relationships between weather and accident severity.
- Analyzing accident patterns across different road types.
- Studying monthly accident trends.
- Supporting road safety research and planning.

## 10. Future Enhancements

- Real-time accident data integration.
- Interactive geographical accident maps.
- Automated PDF report generation.
- Accident hotspot detection.
- Advanced historical trend analysis.
- User authentication.

## 11. Important Notes

- Statistical conclusions depend on dataset quality and size.
- Statistical associations do not establish causation.
- Statistical tests should be interpreted after checking their assumptions.
- Bayesian estimates depend on the selected prior distribution.
- Meaningful time-series analysis requires sufficient historical observations.
- This project is intended for educational and analytical purposes.

---

**Project Name:** Road Accident Data Analysis and Safety Reporting System

**Technologies:** Python, R, Streamlit, MySQL

**Domain:** Data Analytics and Road Safety
