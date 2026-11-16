
# ============================================================
# ROAD ACCIDENT DATA ANALYSIS AND SAFETY REPORTING SYSTEM
# Statistical Analysis using R
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

df <- read.csv("data/road_accident_sample_500.csv",
               stringsAsFactors = FALSE)

names(df) <- tolower(trimws(names(df)))

cat("Total records:", nrow(df), "\n")
cat("Total columns:", ncol(df), "\n")

# Find columns safely
find_col <- function(options) {
  result <- intersect(options, names(df))
  if (length(result) > 0) result[1] else NA_character_
}

date_col <- find_col(c("accident_date", "date", "crash_date"))
severity_col <- find_col(c("severity", "accident_severity"))
casualty_col <- find_col(c("casualties", "casualty_count",
                           "number_of_casualties"))
weather_col <- find_col(c("weather", "weather_conditions"))
road_col <- find_col(c("road_type", "road_surface"))
city_col <- find_col(c("city", "location"))

# Convert numerical data
if (!is.na(casualty_col)) {
  df[[casualty_col]] <- as.numeric(df[[casualty_col]])
}

# ============================================================
# 2. STATISTICAL TESTS
# ============================================================

cat("\n====================================================\n")
cat("2. STATISTICAL TESTING\n")
cat("====================================================\n")

# ------------------------------------------------------------
# 2.1 MANN-WHITNEY U TEST
# ------------------------------------------------------------

cat("\n1. MANN-WHITNEY U TEST\n")

if (!is.na(severity_col) && !is.na(casualty_col)) {

  df$fatal_status <- ifelse(
    tolower(trimws(df[[severity_col]])) == "fatal",
    "Fatal", "Non-Fatal"
  )

  test_data <- df %>%
    filter(!is.na(.data[[casualty_col]]))

  mw_test <- wilcox.test(
    test_data[[casualty_col]] ~ test_data$fatal_status,
    exact = FALSE
  )

  print(mw_test)

  if (mw_test$p.value < 0.05) {
    cat("Significant difference found.\n")
  } else {
    cat("No significant difference found.\n")
  }

} else {
  cat("Required columns not found.\n")
}


# ------------------------------------------------------------
# 2.2 INDEPENDENT T-TEST
# ------------------------------------------------------------

cat("\n2. INDEPENDENT T-TEST\n")

if (!is.na(casualty_col) && !is.na(road_col)) {

  test_data <- df %>%
    filter(!is.na(.data[[casualty_col]]),
           !is.na(.data[[road_col]]))

  test_data[[road_col]] <- as.factor(test_data[[road_col]])

  if (nlevels(droplevels(test_data[[road_col]])) == 2) {

    print(t.test(
      test_data[[casualty_col]] ~ test_data[[road_col]]
    ))

  } else {
    cat("T-test requires exactly two road-type groups.\n")
  }
}


# ------------------------------------------------------------
# 2.3 SHAPIRO-WILK NORMALITY TEST
# ------------------------------------------------------------

cat("\n3. SHAPIRO-WILK NORMALITY TEST\n")

if (!is.na(casualty_col)) {

  values <- na.omit(df[[casualty_col]])

  if (length(values) >= 3 &&
      length(values) <= 5000 &&
      length(unique(values)) > 1) {

    normality <- shapiro.test(values)
    print(normality)

    if (normality$p.value > 0.05) {
      cat("Data is consistent with normality.\n")
    } else {
      cat("Evidence of non-normality found.\n")
    }
  }
}


# ------------------------------------------------------------
# 2.4 ANOVA TEST
# ------------------------------------------------------------

cat("\n4. ONE-WAY ANOVA\n")

if (!is.na(casualty_col) && !is.na(road_col)) {

  test_data <- df %>%
    filter(!is.na(.data[[casualty_col]]),
           !is.na(.data[[road_col]]))

  test_data[[road_col]] <- as.factor(test_data[[road_col]])

  if (nlevels(droplevels(test_data[[road_col]])) >= 2) {

    anova_model <- aov(
      test_data[[casualty_col]] ~ test_data[[road_col]]
    )

    print(summary(anova_model))

  }
}


# ------------------------------------------------------------
# 2.5 KRUSKAL-WALLIS TEST
# ------------------------------------------------------------

cat("\n5. KRUSKAL-WALLIS TEST\n")

if (!is.na(casualty_col) && !is.na(road_col)) {

  test_data <- df %>%
    filter(!is.na(.data[[casualty_col]]),
           !is.na(.data[[road_col]]))

  if (length(unique(test_data[[road_col]])) >= 2) {

    print(kruskal.test(
      test_data[[casualty_col]] ~
        as.factor(test_data[[road_col]])
    ))
  }
}


# ------------------------------------------------------------
# 2.6 CHI-SQUARE / FISHER EXACT TEST
# ------------------------------------------------------------

cat("\n6. CHI-SQUARE / FISHER EXACT TEST\n")

if (!is.na(severity_col) && !is.na(weather_col)) {

  test_data <- df %>%
    filter(!is.na(.data[[severity_col]]),
           !is.na(.data[[weather_col]]))

  tab <- table(
    test_data[[severity_col]],
    test_data[[weather_col]]
  )

  print(tab)

  if (all(dim(tab) == c(2, 2))) {

    print(fisher.test(tab))

  } else if (all(dim(tab) > 1)) {

    print(chisq.test(tab, simulate.p.value = TRUE,
                     B = 5000))
  }
}


# ------------------------------------------------------------
# 2.7 SPEARMAN CORRELATION
# ------------------------------------------------------------

cat("\n7. SPEARMAN CORRELATION\n")

if (!is.na(casualty_col) && !is.na(city_col)) {

  cat("Spearman requires two numerical variables.\n")
  cat("Use a second numerical column if available.\n")
}

# ============================================================
# 3. APRIORI ASSOCIATION ANALYSIS
# ============================================================

cat("\n====================================================\n")
cat("3. APRIORI ASSOCIATION ANALYSIS\n")
cat("====================================================\n")

selected_columns <- intersect(
  c("weather", "road_type", "severity",
    "cause", "accident_cause"),
  names(df)
)

if (length(selected_columns) >= 2) {

  rules_data <- df %>%
    select(all_of(selected_columns)) %>%
    mutate(across(everything(), as.character)) %>%
    mutate(across(everything(),
                  ~ ifelse(is.na(.) | trimws(.) == "",
                           "Unknown", trimws(.)))) %>%
    mutate(across(everything(), as.factor))

  transactions <- as(rules_data, "transactions")

  # Generate association rules
  rules <- apriori(
    transactions,
    parameter = list(
      supp = 0.05,
      conf = 0.50,
      target = "rules"
    ),
    control = list(verbose = FALSE)
  )

  cat("\nTop 5 Association Rules:\n")

  if (length(rules) > 0) {
    inspect(head(sort(rules, by = "lift"), 5))
  } else {
    cat("No rules found. Try reducing support.\n")
  }

  # Rules leading to Minor severity
  cat("\nRules Leading to Minor Severity:\n")

  if ("severity" %in% selected_columns &&
      "Minor" %in% levels(rules_data$severity)) {

    minor_rules <- apriori(
      transactions,
      parameter = list(
        supp = 0.02,
        conf = 0.50,
        target = "rules"
      ),
      appearance = list(
        default = "lhs",
        rhs = "severity=Minor"
      ),
      control = list(verbose = FALSE)
    )

    if (length(minor_rules) > 0) {
      inspect(head(sort(minor_rules, by = "confidence"), 5))
    } else {
      cat("No minor severity rules found.\n")
    }
  }

} else {
  cat("Not enough categorical columns for Apriori.\n")
}


# ============================================================
# 4. BAYESIAN THEORY
# ============================================================

cat("\n====================================================\n")
cat("4. BAYESIAN ANALYSIS\n")
cat("====================================================\n")

if (!is.na(severity_col) && !is.na(weather_col)) {

  bayes_data <- df %>%
    filter(!is.na(.data[[severity_col]]),
           !is.na(.data[[weather_col]]))

  bayes_data$is_fatal <- tolower(
    trimws(bayes_data[[severity_col]])
  ) == "fatal"

  cat("\nProbability of Fatal Accident by Weather:\n")

  weather_results <- bayes_data %>%
    group_by(weather = .data[[weather_col]]) %>%
    summarise(
      total = n(),
      fatal = sum(is_fatal),
      .groups = "drop"
    ) %>%
    mutate(
      # Beta(1,1) prior
      posterior_mean = (fatal + 1) / (total + 2),

      lower_95 = qbeta(
        0.025, fatal + 1, total - fatal + 1
      ),

      upper_95 = qbeta(
        0.975, fatal + 1, total - fatal + 1
      )
    )

  print(weather_results)

  cat("\nBayesian interpretation:\n")
  cat("Posterior probability estimates are based on\n")
  cat("observed fatal accidents and a Beta(1,1) prior.\n")

} else {
  cat("Severity or weather column not found.\n")
}


# ============================================================
# 5. TIME SERIES ANALYSIS
# ============================================================

cat("\n====================================================\n")
cat("5. TIME SERIES ANALYSIS\n")
cat("====================================================\n")

if (!is.na(date_col)) {

  df$analysis_date <- as.Date(
    parse_date_time(
      df[[date_col]],
      orders = c("ymd", "dmy", "mdy", "Ymd",
                 "d/m/Y", "m/d/Y")
    )
  )

  time_data <- df %>%
    filter(!is.na(analysis_date)) %>%
    mutate(month = floor_date(analysis_date, "month")) %>%
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

    # Moving average
    time_data$moving_average <- as.numeric(
      stats::filter(
        time_data$total_accidents,
        rep(1/3, 3),
        sides = 1
      )
    )
  }

} else {
  cat("Date column not found. Time series skipped.\n")
}


# ============================================================
# 6. VISUALIZATION USING GGPLOT2
# ============================================================

cat("\n====================================================\n")
cat("6. DATA VISUALIZATION USING GGPLOT2\n")
cat("====================================================\n")


# ------------------------------------------------------------
# 6.1 Accident Severity Chart
# ------------------------------------------------------------

if (!is.na(severity_col)) {

  p1 <- ggplot(df, aes(x = .data[[severity_col]])) +
    geom_bar(fill = "steelblue") +
    labs(
      title = "Accidents by Severity",
      x = "Severity",
      y = "Number of Accidents"
    ) +
    theme_minimal()

  print(p1)
}


# ------------------------------------------------------------
# 6.2 Weather Analysis
# ------------------------------------------------------------

if (!is.na(weather_col)) {

  p2 <- ggplot(df, aes(x = .data[[weather_col]])) +
    geom_bar(fill = "orange") +
    labs(
      title = "Accidents by Weather Condition",
      x = "Weather",
      y = "Accident Count"
    ) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45,
                                     hjust = 1))

  print(p2)
}


# ------------------------------------------------------------
# 6.3 Road Type Analysis
# ------------------------------------------------------------

if (!is.na(road_col)) {

  p3 <- ggplot(df, aes(x = .data[[road_col]])) +
    geom_bar(fill = "darkgreen") +
    labs(
      title = "Accidents by Road Type",
      x = "Road Type",
      y = "Accident Count"
    ) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45,
                                     hjust = 1))

  print(p3)
}


# ------------------------------------------------------------
# 6.4 Monthly Accident Trend
# ------------------------------------------------------------

if (exists("time_data") && nrow(time_data) > 0) {

  p4 <- ggplot(time_data,
               aes(x = month, y = total_accidents)) +
    geom_line(color = "blue", linewidth = 1) +
    geom_point(color = "red", size = 2) +
    labs(
      title = "Monthly Road Accident Trend",
      x = "Month",
      y = "Number of Accidents"
    ) +
    theme_minimal()

  print(p4)
}


# ------------------------------------------------------------
# 6.5 Casualty Distribution
# ------------------------------------------------------------

if (!is.na(casualty_col)) {

  p5 <- ggplot(df, aes(x = .data[[casualty_col]])) +
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

  print(p5)
}


# ============================================================
# 7. SAVE ANALYSIS OUTPUT
# ============================================================

dir.create("reports", showWarnings = FALSE)

write.csv(
  df,
  "reports/accident_analysis_data.csv",
  row.names = FALSE
)

if (exists("weather_results")) {
  write.csv(
    weather_results,
    "reports/bayesian_analysis.csv",
    row.names = FALSE
  )
}

if (exists("time_data")) {
  write.csv(
    time_data,
    "reports/monthly_accident_analysis.csv",
    row.names = FALSE
  )
}

cat("\n====================================================\n")
cat("ROAD ACCIDENT ANALYSIS COMPLETED SUCCESSFULLY!\n")
cat("====================================================\n")
cat("Statistical tests completed.\n")
cat("Apriori analysis completed where applicable.\n")
cat("Bayesian analysis completed where applicable.\n")
cat("Time series analysis completed where applicable.\n")
cat("ggplot2 visualizations generated.\n")
cat("Reports saved in reports/ folder.\n")
