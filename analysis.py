
import pandas as pd
from scipy.stats import chi2_contingency, pearsonr

def get_summary(df):
    return {
        "Total Accidents": len(df),
        "Total Casualties": int(df["casualties"].sum()),
        "Fatal Accidents": int((df["severity"] == "Fatal").sum()),
        "Average Casualties": round(df["casualties"].mean(), 2)
    }


def severity_analysis(df):
    return df["severity"].value_counts()


def city_analysis(df):
    return df["city"].value_counts().head(10)


def cause_analysis(df):
    return df["main_cause"].value_counts()


def monthly_analysis(df):
    return df.groupby(df["date"].dt.month).size()


def weekday_analysis(df):
    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    counts = df["date"].dt.day_name().value_counts()
    return counts.reindex(weekday_order, fill_value=0)


def weather_analysis(df):
    return df["weather"].value_counts()


def road_analysis(df):
    return df["road_type"].value_counts()


def time_analysis(df):
    hours = pd.to_datetime(
        df["time"], format="%H:%M", errors="coerce"
    ).dt.hour

    return pd.cut(
        hours,
        bins=[-1, 5, 11, 17, 23],
        labels=["Night", "Morning", "Afternoon", "Evening"]
    ).value_counts().reindex(
        ["Morning", "Afternoon", "Evening", "Night"],
        fill_value=0
    )


def severity_weather_test(df):
    table = pd.crosstab(df["weather"], df["severity"])

    chi2, p_value, dof, expected = chi2_contingency(table)

    return {
        "chi_square": round(chi2, 3),
        "p_value": round(p_value, 4),
        "degrees_of_freedom": dof
    }


def casualties_correlation(df):
    correlation, p_value = pearsonr(
        df["vehicles_involved"],
        df["casualties"]
    )

    return {
        "correlation": round(correlation, 3),
        "p_value": round(p_value, 4)
    }
