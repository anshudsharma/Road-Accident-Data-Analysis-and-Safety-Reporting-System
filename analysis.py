
import pandas as pd
from scipy.stats import chi2_contingency, pearsonr
from scipy.stats import mannwhitneyu
from mlxtend.frequent_patterns import apriori, association_rules

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
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
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

    categories = pd.cut(
        hours,
        bins=[-1, 5, 11, 17, 23],
        labels=["Night", "Morning", "Afternoon", "Evening"]
    )

    return categories.value_counts().reindex(
        ["Morning", "Afternoon", "Evening", "Night"],
        fill_value=0
    )


def severity_weather_test(df):
    table = pd.crosstab(df["weather"], df["severity"])

    chi2, p_value, dof, expected = chi2_contingency(table)

    expected_df = pd.DataFrame(
        expected,
        index=table.index,
        columns=table.columns
    )

    return {
        "chi_square": round(chi2, 3),
        "p_value": round(p_value, 4),
        "degrees_of_freedom": dof,
        "expected_frequencies": expected_df,
        "minimum_expected": round(expected.min(), 3),
        "cells_below_5": int((expected < 5).sum())
    }


def casualties_correlation(df):
    data = df[
        ["vehicles_involved", "casualties"]
    ].dropna()

    correlation, p_value = pearsonr(
        data["vehicles_involved"],
        data["casualties"]
    )

    return {
        "correlation": round(correlation, 3),
        "p_value": round(p_value, 4),
        "sample_size": len(data)
    }

def mann_whitney_test(df, group_col, target_col, group1, group2):
    """Performs Mann-Whitney U test between two groups."""
    data1 = df[df[group_col] == group1][target_col].dropna()
    data2 = df[df[group_col] == group2][target_col].dropna()

    stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
    return {"statistic": stat, "p_value": p_value, "g1_size": len(data1), "g2_size": len(data2)}

def apriori_association(df, columns_to_analyze, min_support=0.05):
    """Generates association rules using Apriori."""
    # One-hot encode the selected categorical columns
    df_encoded = pd.get_dummies(df[columns_to_analyze])

    # Convert to boolean for mlxtend
    df_encoded = df_encoded.astype(bool)

    # Generate frequent itemsets
    frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)

    if frequent_itemsets.empty:
        return None

    # Generate rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)

    # Clean up output for display
    rules["antecedents"] = rules["antecedents"].apply(lambda x: ', '.join(list(x)))
    rules["consequents"] = rules["consequents"].apply(lambda x: ', '.join(list(x)))

    return rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].sort_values(by='lift', ascending=False)
