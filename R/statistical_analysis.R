
# ============================================================
# ROAD ACCIDENT DATA ANALYSIS AND SAFETY REPORTING SYSTEM
# Statistical Analysis using R
# Python + R + MySQL + Streamlit
# ============================================================

options(warn = -1)

suppressPackageStartupMessages({
  library(arules)
  library(dplyr)
  library(ggplot2)
  library(lubridate)
})

# ============================================================
# 1. LOAD DATA
# ============================================================

cat("\n🚗 Loading accident data...\n")

# Accept CSV path from Streamlit.
# If no argument is supplied, use sample CSV.

args <- commandArgs(trailingOnly = TRUE)

if (length(args) >= 1) {
  input_file <- args[1]
} else {
  input_file <- "data/road_accident_sample_500.csv"
}

if (!file.exists(input_file)) {
  stop(paste("Input file not found:", input_file))
}

df <- read.csv(
  input_file,
  stringsAsFactors = FALSE
)

names(df) <- tolower(trimws(names(df)))

cat("Total records:", nrow(df), "\n")
cat("Total columns:", ncol(df), "\n")

if (nrow(df) == 0) {
  stop("Dataset is empty.")
}

# Create output folders

dir.create("reports", showWarnings = FALSE)

dir.create(
  "reports/plots",
  recursive = TRUE,
  showWarnings = FALSE
)

# ============================================================
# 2. FIND REQUIRED COLUMNS
# ============================================================

find_col <- function(options) {

  result <- intersect(options, names(df))

  if (length(result) > 0) {
    return(result[1])
  }

  NA_character_
}

date_col <- find_col(c(
  "accident_date",
  "date",
  "crash_date"
))

severity_col <- find_col(c(
  "severity",
  "accident_severity"
))

casualty_col <- find_col(c(
  "casualties",
  "casualty_count",
  "number_of_casualties"
))

weather_col <- find_col(c(
  "weather",
  "weather_conditions"
))

road_col <- find_col(c(
  "road_type",
  "road_surface"
))

city_col <- find_col(c(
  "city",
  "location"
))

cause_col <- find_col(c(
  "cause",
  "accident_cause",
  "main_cause"
))

# Find a second numerical column for correlation

numeric_candidates <- names(df)[
  sapply(df, is.numeric)
]

second_numeric_col <- NA_character_

if (length(numeric_candidates) >= 2) {
  second_numeric_col <- numeric_candidates[2]
}

# Convert casualty data into numeric format

if (!is.na(casualty_col)) {

  df[[casualty_col]] <- suppressWarnings(
    as.numeric(df[[casualty_col]])
  )
}

cat("\nDetected columns:\n")

cat("Date:", date_col, "\n")
cat("Severity:", severity_col, "\n")
cat("Casualties:", casualty_col, "\n")
cat("Weather:", weather_col, "\n")
cat("Road:", road_col, "\n")
cat("City:", city_col, "\n")
cat("Cause:", cause_col, "\n")

# ============================================================
# 3. STATISTICAL TESTS
# ============================================================

cat("\n====================================================\n")
cat("3. STATISTICAL TESTING\n")
cat("====================================================\n")


# ------------------------------------------------------------
# 3.1 MANN-WHITNEY U TEST
# ------------------------------------------------------------

cat("\n1. MANN-WHITNEY U TEST\n")

if (!is.na(severity_col) && !is.na(casualty_col)) {

  test_data <- df %>%
    mutate(
      fatal_status = ifelse(
        tolower(trimws(.data[[severity_col]])) == "fatal",
        "Fatal",
        "Non-Fatal"
      )
    ) %>%
    filter(
      !is.na(.data[[casualty_col]])
    )

  test_data$fatal_status <- factor(
    test_data$fatal_status
  )

  if (
    nlevels(droplevels(test_data$fatal_status)) == 2
  ) {

    mw_test <- wilcox.test(
      test_data[[casualty_col]] ~
        test_data$fatal_status,
      exact = FALSE
    )

    print(mw_test)

    if (mw_test$p.value < 0.05) {
      cat("Significant difference found.\n")
    } else {
      cat("No significant difference found.\n")
    }

  } else {
    cat("Two severity groups are required.\n")
  }

} else {
  cat("Required columns not found.\n")
}


# ------------------------------------------------------------
# 3.2 INDEPENDENT T-TEST
# ------------------------------------------------------------

cat("\n2. INDEPENDENT T-TEST\n")

if (!is.na(casualty_col) && !is.na(road_col)) {

  test_data <- df %>%
    filter(
      !is.na(.data[[casualty_col]]),
      !is.na(.data[[road_col]])
    )

  test_data[[road_col]] <- as.factor(
    test_data[[road_col]]
  )

  if (
    nlevels(droplevels(test_data[[road_col]])) == 2
  ) {

    t_test <- t.test(
      test_data[[casualty_col]] ~
        test_data[[road_col]]
    )

    print(t_test)

  } else {
    cat("T-test requires exactly two road-type groups.\n")
  }

} else {
  cat("Required columns not found.\n")
}


# ------------------------------------------------------------
# 3.3 SHAPIRO-WILK NORMALITY TEST
# ------------------------------------------------------------

cat("\n3. SHAPIRO-WILK NORMALITY TEST\n")

if (!is.na(casualty_col)) {

  values <- na.omit(df[[casualty_col]])

  if (
    length(values) >= 3 &&
    length(values) <= 5000 &&
    length(unique(values)) > 1
  ) {

    normality <- shapiro.test(values)

    print(normality)

    if (normality$p.value > 0.05) {
      cat("Data is consistent with normality.\n")
    } else {
      cat("Evidence of non-normality found.\n")
    }

  } else {
    cat("Insufficient data for Shapiro-Wilk test.\n")
  }

}


# ------------------------------------------------------------
# 3.4 ONE-WAY ANOVA
# ------------------------------------------------------------

cat("\n4. ONE-WAY ANOVA\n")

if (!is.na(casualty_col) && !is.na(road_col)) {

  test_data <- df %>%
    filter(
      !is.na(.data[[casualty_col]]),
      !is.na(.data[[road_col]])
    )

  test_data$road_group <- as.factor(
    test_data[[road_col]]
  )

  if (nlevels(droplevels(test_data$road_group)) >= 2) {

    anova_model <- aov(
      test_data[[casualty_col]] ~ road_group,
      data = test_data
    )

    print(summary(anova_model))

    cat("\nANOVA Residual Normality Test:\n")

    residuals_data <- residuals(anova_model)

    if (
      length(residuals_data) >= 3 &&
      length(residuals_data) <= 5000
    ) {
      print(shapiro.test(residuals_data))
    }

  } else {
    cat("At least two road groups are required.\n")
  }

}


# ------------------------------------------------------------
# 3.5 KRUSKAL-WALLIS TEST
# ------------------------------------------------------------

cat("\n5. KRUSKAL-WALLIS TEST\n")

if (!is.na(casualty_col) && !is.na(road_col)) {

  test_data <- df %>%
    filter(
      !is.na(.data[[casualty_col]]),
      !is.na(.data[[road_col]])
    )

  test_data$road_group <- as.factor(
    test_data[[road_col]]
  )

  if (nlevels(droplevels(test_data$road_group)) >= 2) {

    kw_test <- kruskal.test(
      test_data[[casualty_col]] ~
        test_data$road_group
    )

    print(kw_test)

  } else {
    cat("At least two groups are required.\n")
  }

}


# ------------------------------------------------------------
# 3.6 CHI-SQUARE / FISHER EXACT TEST
# ------------------------------------------------------------

cat("\n6. CHI-SQUARE / FISHER EXACT TEST\n")

if (!is.na(severity_col) && !is.na(weather_col)) {

  test_data <- df %>%
    filter(
      !is.na(.data[[severity_col]]),
      !is.na(.data[[weather_col]])
    )

  tab <- table(
    test_data[[severity_col]],
    test_data[[weather_col]]
  )

  print(tab)

  if (all(dim(tab) == c(2, 2))) {

    fisher_result <- fisher.test(tab)

    print(fisher_result)

  } else if (all(dim(tab) > 1)) {

    chi_result <- chisq.test(
      tab,
      simulate.p.value = TRUE,
      B = 5000
    )

    print(chi_result)

  } else {
    cat("Not enough categories for contingency testing.\n")
  }

} else {
  cat("Severity or weather column not found.\n")
}


# ------------------------------------------------------------
# 3.7 SPEARMAN CORRELATION
# ------------------------------------------------------------

cat("\n7. SPEARMAN CORRELATION\n")

if (
  !is.na(casualty_col) &&
  !is.na(second_numeric_col) &&
  casualty_col != second_numeric_col
) {

  correlation_data <- df %>%
    select(
      all_of(c(casualty_col, second_numeric_col))
    ) %>%
    na.omit()

  if (
    nrow(correlation_data) >= 3 &&
    length(unique(correlation_data[[1]])) > 1 &&
    length(unique(correlation_data[[2]])) > 1
  ) {

    spearman_result <- cor.test(
      correlation_data[[1]],
      correlation_data[[2]],
      method = "spearman",
      exact = FALSE
    )

    print(spearman_result)

  } else {
    cat("Insufficient variation or observations.\n")
  }

} else {
  cat("Two different numerical columns are required.\n")
}


# ============================================================
# 4. APRIORI ASSOCIATION ANALYSIS
# ============================================================

cat("\n====================================================\n")
cat("4. APRIORI ASSOCIATION ANALYSIS\n")
cat("====================================================\n")

selected_columns <- intersect(
  c(
    weather_col,
    road_col,
    severity_col,
    cause_col
  ),
  names(df)
)

selected_columns <- unique(
  selected_columns[!is.na(selected_columns)]
)

if (length(selected_columns) >= 2) {

  rules_data <- df %>%
    select(all_of(selected_columns)) %>%
    mutate(
      across(
        everything(),
        ~ trimws(as.character(.))
      )
    ) %>%
    mutate(
      across(
        everything(),
        ~ ifelse(
          is.na(.) | . == "",
          "Unknown",
          .
        )
      )
    ) %>%
    mutate(
      across(
        everything(),
        as.factor
      )
    )

  transactions <- as(
    rules_data,
    "transactions"
  )

  # ----------------------------------------------------------
  # 4.1 GENERAL ASSOCIATION RULES
  # ----------------------------------------------------------

  cat("\nTop 5 Association Rules:\n")

  rules <- apriori(
    transactions,
    parameter = list(
      supp = 0.05,
      conf = 0.50,
      target = "rules"
    ),
    control = list(
      verbose = FALSE
    )
  )

  if (length(rules) > 0) {

    sorted_rules <- sort(
      rules,
      by = "lift",
      decreasing = TRUE
    )

    inspect(head(sorted_rules, 5))

  } else {
    cat("No rules found. Try reducing support.\n")
  }


  # ----------------------------------------------------------
  # 4.2 RULES LEADING TO MINOR SEVERITY
  # ----------------------------------------------------------

  cat("\nRules Leading to Minor Severity:\n")

  if (!is.na(severity_col)) {

    severity_values <- levels(
      rules_data[[severity_col]]
    )

    minor_value <- severity_values[
      tolower(trimws(severity_values)) == "minor"
    ]

    if (length(minor_value) > 0) {

      minor_rhs <- paste0(
        severity_col,
        "=",
        minor_value[1]
      )

      minor_rules <- apriori(
        transactions,
        parameter = list(
          supp = 0.02,
          conf = 0.50,
          target = "rules"
        ),
        appearance = list(
          default = "lhs",
          rhs = minor_rhs
        ),
        control = list(
          verbose = FALSE
        )
      )

      if (length(minor_rules) > 0) {

        inspect(
          head(
            sort(
              minor_rules,
              by = "confidence",
              decreasing = TRUE
            ),
            5
          )
        )

      } else {
        cat("No minor severity rules found.\n")
      }

    } else {
      cat("Minor severity category not found.\n")
    }

  }

} else {
  cat("Not enough categorical columns for Apriori.\n")
}


# ============================================================
# 5. BAYESIAN THEORY
# ============================================================

cat("\n====================================================\n")
cat("5. BAYESIAN ANALYSIS\n")
cat("====================================================\n")

weather_results <- NULL

if (!is.na(severity_col) && !is.na(weather_col)) {

  bayes_data <- df %>%
    filter(
      !is.na(.data[[severity_col]]),
      !is.na(.data[[weather_col]]),
      trimws(.data[[weather_col]]) != ""
    )

  bayes_data$is_fatal <- (
    tolower(trimws(bayes_data[[severity_col]])) == "fatal"
  )

  cat("\nProbability of Fatal Accident by Weather:\n")

  weather_results <- bayes_data %>%
    group_by(
      weather = .data[[weather_col]]
    ) %>%
    summarise(
      total = n(),
      fatal = sum(is_fatal),
      .groups = "drop"
    ) %>%
    mutate(
      # Beta(1,1) prior

      posterior_alpha = fatal + 1,

      posterior_beta = total - fatal + 1,

      posterior_mean = (
        posterior_alpha /
        (posterior_alpha + posterior_beta)
      ),

      lower_95 = qbeta(
        0.025,
        posterior_alpha,
        posterior_beta
      ),

      upper_95 = qbeta(
        0.975,
        posterior_alpha,
        posterior_beta
      )
    )

  print(weather_results)

  cat("\nBayesian Interpretation:\n")

  cat("Posterior probabilities use a Beta(1,1) prior.\n")
  cat("Intervals represent 95% credible intervals.\n")

} else {

  cat("Severity or weather column not found.\n")

}


# ============================================================
# 6. TIME SERIES ANALYSIS
# ============================================================

cat("\n====================================================\n")
cat("6. TIME SERIES ANALYSIS\n")
cat("====================================================\n")

time_data <- NULL

if (!is.na(date_col)) {

  df$analysis_date <- as.Date(
    parse_date_time(
      df[[date_col]],
      orders = c(
        "ymd",
        "dmy",
        "mdy",
        "Ymd",
        "d/m/Y",
        "m/d/Y"
      )
    )
  )

  time_data <- df %>%
    filter(!is.na(analysis_date)) %>%
    mutate(
      month = floor_date(
        analysis_date,
        "month"
      )
    ) %>%
    group_by(month) %>%
    summarise(
      total_accidents = n(),

      total_casualties = if (!is.na(casualty_col)) {
        sum(.data[[casualty_col]], na.rm = TRUE)
      } else {
        NA_real_
      },

      .groups = "drop"
    ) %>%
    arrange(month)

  cat("\nMonthly Accident Statistics:\n")

  print(time_data)

  if (nrow(time_data) >= 2) {

    cat("\nMonthly Accident Trend:\n")

    time_model <- lm(
      total_accidents ~ as.numeric(month),
      data = time_data
    )

    print(summary(time_model))

    # Three-month moving average

    time_data$moving_average <- as.numeric(
      stats::filter(
        time_data$total_accidents,
        filter = rep(1 / 3, 3),
        sides = 1
      )
    )

    cat("\nMoving Average:\n")

    print(time_data)

  } else {

    cat("At least two monthly observations are required.\n")

  }

} else {

  cat("Date column not found. Time series skipped.\n")

}


# ============================================================
# 7. GGPLOT2 VISUALIZATIONS
# ============================================================

cat("\n====================================================\n")
cat("7. DATA VISUALIZATION USING GGPLOT2\n")
cat("====================================================\n")


# ------------------------------------------------------------
# 7.1 ACCIDENT SEVERITY
# ------------------------------------------------------------

if (!is.na(severity_col)) {

  p1 <- ggplot(
    df,
    aes(x = .data[[severity_col]])
  ) +
    geom_bar(fill = "steelblue") +
    labs(
      title = "Accidents by Severity",
      x = "Severity",
      y = "Number of Accidents"
    ) +
    theme_minimal()

  ggsave(
    "reports/plots/severity.png",
    plot = p1,
    width = 8,
    height = 5,
    dpi = 150
  )

  cat("Severity chart saved.\n")
}


# ------------------------------------------------------------
# 7.2 WEATHER ANALYSIS
# ------------------------------------------------------------

if (!is.na(weather_col)) {

  p2 <- ggplot(
    df,
    aes(x = .data[[weather_col]])
  ) +
    geom_bar(fill = "orange") +
    labs(
      title = "Accidents by Weather Condition",
      x = "Weather",
      y = "Accident Count"
    ) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(
        angle = 45,
        hjust = 1
      )
    )

  ggsave(
    "reports/plots/weather.png",
    plot = p2,
    width = 8,
    height = 5,
    dpi = 150
  )

  cat("Weather chart saved.\n")
}


# ------------------------------------------------------------
# 7.3 ROAD TYPE ANALYSIS
# ------------------------------------------------------------

if (!is.na(road_col)) {

  p3 <- ggplot(
    df,
    aes(x = .data[[road_col]])
  ) +
    geom_bar(fill = "darkgreen") +
    labs(
      title = "Accidents by Road Type",
      x = "Road Type",
      y = "Accident Count"
    ) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(
        angle = 45,
        hjust = 1
      )
    )

  ggsave(
    "reports/plots/road_type.png",
    plot = p3,
    width = 8,
    height = 5,
    dpi = 150
  )

  cat("Road type chart saved.\n")
}


# ------------------------------------------------------------
# 7.4 MONTHLY ACCIDENT TREND
# ------------------------------------------------------------

if (
  !is.null(time_data) &&
  nrow(time_data) > 0
) {

  p4 <- ggplot(
    time_data,
    aes(
      x = month,
      y = total_accidents
    )
  ) +
    geom_line(
      color = "blue",
      linewidth = 1
    ) +
    geom_point(
      color = "red",
      size = 2
    ) +
    labs(
      title = "Monthly Road Accident Trend",
      x = "Month",
      y = "Number of Accidents"
    ) +
    theme_minimal()

  ggsave(
    "reports/plots/monthly_trend.png",
    plot = p4,
    width = 8,
    height = 5,
    dpi = 150
  )

  cat("Monthly trend chart saved.\n")
}


# ------------------------------------------------------------
# 7.5 CASUALTY DISTRIBUTION
# ------------------------------------------------------------

if (!is.na(casualty_col)) {

  p5 <- ggplot(
    df,
    aes(x = .data[[casualty_col]])
  ) +
    geom_histogram(
      bins = 20,
      fill = "skyblue",
      color = "black"
    ) +
    labs(
      title = "Distribution of Accident Casualties",
      x = "Casualty Count",
      y = "Frequency"
    ) +
    theme_minimal()

  ggsave(
    "reports/plots/casualty_histogram.png",
    plot = p5,
    width = 8,
    height = 5,
    dpi = 150
  )

  cat("Casualty histogram saved.\n")
}


# ============================================================
# 8. SAVE ANALYSIS OUTPUT
# ============================================================

cat("\n====================================================\n")
cat("8. SAVING ANALYSIS REPORTS\n")
cat("====================================================\n")

# Save processed analysis data

write.csv(
  df,
  "reports/accident_analysis_data.csv",
  row.names = FALSE
)

# Save Bayesian results

if (!is.null(weather_results)) {

  write.csv(
    weather_results,
    "reports/bayesian_analysis.csv",
    row.names = FALSE
  )

}

# Save monthly time-series results

if (!is.null(time_data)) {

  write.csv(
    time_data,
    "reports/monthly_accident_analysis.csv",
    row.names = FALSE
  )

}


# ============================================================
# 9. FINAL MESSAGE
# ============================================================

cat("\n====================================================\n")
cat("ROAD ACCIDENT ANALYSIS COMPLETED SUCCESSFULLY!\n")
cat("====================================================\n")

cat("Statistical tests completed where applicable.\n")
cat("Apriori analysis completed where applicable.\n")
cat("Bayesian analysis completed where applicable.\n")
cat("Time series analysis completed where applicable.\n")
cat("ggplot2 charts saved successfully.\n")

cat("\nReports saved in: reports/\n")
cat("Charts saved in: reports/plots/\n")

cat("\nAll analysis tasks finished!\n")
