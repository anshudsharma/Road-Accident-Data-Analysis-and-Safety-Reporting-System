
options(warn=-1)
suppressPackageStartupMessages({
  library(arules)
  library(dplyr)
})

cat("🚗 Loading accident data...\n")
df <- read.csv("data/road_accident_sample_500.csv")

#Mann whitney U test
cat("\n======================================================\n")
cat("1. MANN-WHITNEY U TEST (WILCOXON RANK SUM)\n")
cat("======================================================\n")
cat("Testing if casualty counts significantly differ between Fatal and Non-Fatal accidents...\n\n")


df$fatal_status <- ifelse(df$severity == "Fatal", "Fatal", "Non-Fatal")


mw_test <- wilcox.test(casualties ~ fatal_status, data = df, exact = FALSE)
print(mw_test)

if (mw_test$p.value < 0.05) {
  cat("Result: Significant difference in casualties based on fatality status.\n")
} else {
  cat("Result: No significant difference found.\n")
}

#2 Market Base Analysis
cat("\n======================================================\n")
cat("2. AFFINITY ANALYSIS (APRIORI ALGORITHM)\n")
cat("======================================================\n")

# Use any_of() to safely select columns even if the names vary slightly in the raw CSV
rules_data <- df %>%
  select(any_of(c("weather", "road_type", "severity", "cause", "accident_cause"))) %>%
  mutate_all(as.factor)

transactions <- as(rules_data, "transactions")

cat("\nMining frequent itemsets and rules (Support >= 5%, Confidence >= 50%)...\n\n")

rules <- apriori(transactions,
                 parameter = list(supp = 0.05, conf = 0.5, target = "rules"),
                 control = list(verbose = FALSE))

cat("Top 5 Association Rules (Sorted by Lift / Strength):\n")
inspect(head(sort(rules, by = "lift"), 5))

cat("\nTop 5 Rules Leading Specifically to Minor Severity:\n")
minor_rules <- apriori(transactions,
                       parameter = list(supp = 0.02, conf = 0.5),
                       appearance = list(default = "lhs", rhs = "severity=Minor"),
                       control = list(verbose = FALSE))
inspect(head(sort(minor_rules, by = "confidence"), 5))

#Apriori
rules <- apriori(transactions,
                 parameter = list(supp = 0.05, conf = 0.5, target = "rules"),
                 control = list(verbose = FALSE))

cat("Top 5 Association Rules (Sorted by Lift / Strength):\n")
inspect(head(sort(rules, by = "lift"), 5))

cat("\nTop 5 Rules Leading Specifically to Minor Severity:\n")
minor_rules <- apriori(transactions,
                       parameter = list(supp = 0.02, conf = 0.5),
                       appearance = list(default = "lhs", rhs = "severity=Minor"),
                       control = list(verbose = FALSE))
inspect(head(sort(minor_rules, by = "confidence"), 5))
