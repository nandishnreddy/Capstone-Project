import os
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Configs & Paths
# -------------------------------
OUTPUT_DIR = Path("week3_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------
# 1) Load & Clean Data
# -------------------------------
def load_data():
    candidates = ["combined_trends.csv", "combine_trends.csv"]
    csv_path = None
    for c in candidates:
        if Path(c).exists():
            csv_path = c
            break
    if csv_path is None:
        raise FileNotFoundError("Could not find combined_trends.csv or combine_trends.csv")

    df = pd.read_csv(csv_path)

    # Ensure required columns exist
    required = ["tool_name", "platform", "start_week", "end_week", "popularity_score"]
    lower_map = {c.lower(): c for c in df.columns}
    for r in required:
        if r not in lower_map:
            raise ValueError(f"Missing required column: {r}")

    # Clean types & labels
    df["tool_name"] = df[lower_map["tool_name"]].astype(str).str.strip().str.title()
    df["platform"] = df[lower_map["platform"]].astype(str).str.strip()
    df["start_week"] = pd.to_datetime(df[lower_map["start_week"]]).dt.date
    df["end_week"] = pd.to_datetime(df[lower_map["end_week"]]).dt.date
    df["popularity_score"] = pd.to_numeric(df[lower_map["popularity_score"]], errors="coerce").fillna(0.0)

    # Normalize common platform name variants
    platform_fix = {
        "stackoverflow": "StackOverflow",
        "stack overflow": "StackOverflow",
        "hackernews": "HackerNews",
        "github": "GitHub",
        "producthunt": "ProductHunt",
        "youtube": "YouTube",
    }
    df["platform"] = df["platform"].str.lower().replace(platform_fix).str.title()

    # Optional category column
    if "category" in df.columns:
        df["category"] = df["category"].astype(str).str.strip().str.title()
    else:
        df["category"] = "Unknown"

    return df


df = load_data()
sns.set(style="whitegrid")

# -------------------------------
# 2) Basic EDA Plots
# -------------------------------
# Records per platform
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x="platform", order=df["platform"].value_counts().index)
plt.title("Records Per Platform")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "eda_records_per_platform.png")
plt.close()

# Weekly platform totals
weekly_platform = df.groupby(["start_week", "platform"], as_index=False)["popularity_score"].sum()
plt.figure(figsize=(10, 6))
for p, sub in weekly_platform.groupby("platform"):
    plt.plot(sub["start_week"], sub["popularity_score"], marker="o", label=p)
plt.title("Weekly Popularity Sum by Platform")
plt.xlabel("Week");
plt.ylabel("Sum(popularity_score)")
plt.legend();
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "eda_weekly_sum_by_platform.png")
plt.close()

# -------------------------------
# 3) Trend Logic (Weekly Trend Score)
# -------------------------------
weekly = (
    df.groupby(["tool_name", "start_week"], as_index=False)
    .agg(total_popularity=("popularity_score", "sum"),
         platform_count=("platform", "nunique"))
)
weekly = weekly.sort_values(["tool_name", "start_week"])
weekly["prev_total"] = weekly.groupby("tool_name")["total_popularity"].shift(1)
weekly["growth_pct_raw"] = (weekly["total_popularity"] - weekly["prev_total"]) / weekly["prev_total"]
weekly["growth_pct_raw"] = weekly["growth_pct_raw"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
weekly["growth_norm"] = ((weekly["growth_pct_raw"].clip(-1, 1) + 1.0) / 2.0)


def minmax_norm(s: pd.Series) -> pd.Series:
    smin, smax = s.min(), s.max()
    return (s - smin) / (smax - smin) if smax > smin else pd.Series(0, index=s.index)


weekly["engagement_norm"] = weekly.groupby("start_week")["total_popularity"].transform(minmax_norm)
total_platforms_week = df.groupby("start_week")["platform"].nunique().rename("total_platforms_week")
weekly = weekly.merge(total_platforms_week, on="start_week", how="left")
weekly["presence_norm"] = (weekly["platform_count"] / weekly["total_platforms_week"].replace(0, np.nan)).fillna(0).clip(
    0, 1)
weekly["trend_score"] = 0.4 * weekly["growth_norm"] + 0.3 * weekly["engagement_norm"] + 0.3 * weekly["presence_norm"]
weekly["rank"] = weekly.groupby("start_week")["trend_score"].rank(method="min", ascending=False)
weekly.sort_values(["start_week", "rank"], inplace=True)
weekly.to_csv(OUTPUT_DIR / "trend_scores_weekly.csv", index=False)

# Top 5 weekly tools
top5 = weekly[weekly["rank"] <= 5].copy()
top5.to_csv(OUTPUT_DIR / "weekly_top5.csv", index=False)

# -------------------------------
# 3a) Weekly Top 10 Tools Plot
# -------------------------------
top10_tools = (
    df.groupby("tool_name")["popularity_score"].sum()
    .sort_values(ascending=False).head(10).index.tolist()
)
weekly_top10 = (
    df[df["tool_name"].isin(top10_tools)]
    .groupby(["start_week", "tool_name"], as_index=False)["popularity_score"].sum()
)
plt.figure(figsize=(12, 6))
for t, sub in weekly_top10.groupby("tool_name"):
    plt.plot(sub["start_week"], sub["popularity_score"], marker="o", label=t)
plt.title("Weekly Popularity (Top 10 Tools Overall)")
plt.xlabel("Week");
plt.ylabel("Sum(popularity_score)")
plt.legend(ncol=2);
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top10_weekly_trends.png")
plt.close()

# -------------------------------
# 4) Category-wise Top 5 Tools
# -------------------------------
df['total_score'] = df['popularity_score']
tool_scores = df.groupby(['category', 'tool_name'], as_index=False)['total_score'].sum()

for cat in df['category'].unique():
    cat_df = tool_scores[tool_scores['category'] == cat]
    top5_cat = cat_df.sort_values('total_score', ascending=False).head(5)
    print(f"\nTop 5 Tools in Category: {cat}")
    print(top5_cat[['tool_name', 'total_score']])

    plt.figure(figsize=(10, 6))
    sns.barplot(data=top5_cat, x='tool_name', y='total_score', palette="viridis")
    plt.title(f"Top 5 Tools in {cat}")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    safe_cat = re.sub(r'[^a-zA-Z0-9]', '_', cat)
    plt.savefig(OUTPUT_DIR / f"top5_{safe_cat}.png")
    plt.close()

# -------------------------------
# 5) Overall Top 5 Tools Across Platforms & Categories
# -------------------------------
overall_scores = df.groupby('tool_name', as_index=False)['total_score'].sum()
top5_overall = overall_scores.sort_values('total_score', ascending=False).head(5)
print("\nTop 5 AIML Tools Across All Categories & Platforms:")
print(top5_overall)

plt.figure(figsize=(10, 6))
sns.barplot(data=top5_overall, x='tool_name', y='total_score', palette="viridis")
plt.title("Top 5 AIML Tools Across All Categories & Platforms")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top5_AIML_Tools_Overall.png")
plt.close()

print(f"\n✅ All outputs saved to: {OUTPUT_DIR.resolve()}")
