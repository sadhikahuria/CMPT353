import sys
import pandas as pd
from scipy import stats


OUTPUT_TEMPLATE = (
    "Initial T-test p-value: {initial_ttest_p:.3g}\n"
    "Original data normality p-values: {initial_weekday_normality_p:.3g} {initial_weekend_normality_p:.3g}\n"
    "Original data equal-variance p-value: {initial_levene_p:.3g}\n"
    "Transformed data normality p-values: {transformed_weekday_normality_p:.3g} {transformed_weekend_normality_p:.3g}\n"
    "Transformed data equal-variance p-value: {transformed_levene_p:.3g}\n"
    "Weekly data normality p-values: {weekly_weekday_normality_p:.3g} {weekly_weekend_normality_p:.3g}\n"
    "Weekly data equal-variance p-value: {weekly_levene_p:.3g}\n"
    "Weekly T-test p-value: {weekly_ttest_p:.3g}\n"
    "Mann-Whitney U-test p-value: {utest_p:.3g}"
)


def main():
    reddit_counts = sys.argv[1]
    counts = pd.read_json(reddit_counts, lines=True)

    canada = counts[(counts['subreddit'] == 'canada') & (counts['date'].dt.year.isin([2012, 2013]))].copy()
    canada['weekday'] = canada['date'].dt.weekday < 5

    weekday_counts = canada[canada['weekday']]['comment_count']
    weekend_counts = canada[~canada['weekday']]['comment_count']

    initial_ttest_p = stats.ttest_ind(weekday_counts, weekend_counts).pvalue
    initial_weekday_normality_p = stats.normaltest(weekday_counts).pvalue
    initial_weekend_normality_p = stats.normaltest(weekend_counts).pvalue
    initial_levene_p = stats.levene(weekday_counts, weekend_counts).pvalue

    transformed_weekday = weekday_counts ** 0.5
    transformed_weekend = weekend_counts ** 0.5
    transformed_weekday_normality_p = stats.normaltest(transformed_weekday).pvalue
    transformed_weekend_normality_p = stats.normaltest(transformed_weekend).pvalue
    transformed_levene_p = stats.levene(transformed_weekday, transformed_weekend).pvalue

    canada['isoyear'] = canada['date'].apply(lambda d: d.isocalendar()[0])
    canada['isoweek'] = canada['date'].apply(lambda d: d.isocalendar()[1])

    weekly_weekday = canada[canada['weekday']].groupby(['isoyear', 'isoweek'])['comment_count'].mean()
    weekly_weekend = canada[~canada['weekday']].groupby(['isoyear', 'isoweek'])['comment_count'].mean()

    weekly_weekday_normality_p = stats.normaltest(weekly_weekday).pvalue
    weekly_weekend_normality_p = stats.normaltest(weekly_weekend).pvalue
    weekly_levene_p = stats.levene(weekly_weekday, weekly_weekend).pvalue
    weekly_ttest_p = stats.ttest_ind(weekly_weekday, weekly_weekend).pvalue

    utest_p = stats.mannwhitneyu(weekday_counts, weekend_counts, alternative='two-sided').pvalue

    print(OUTPUT_TEMPLATE.format(
        initial_ttest_p=initial_ttest_p,
        initial_weekday_normality_p=initial_weekday_normality_p,
        initial_weekend_normality_p=initial_weekend_normality_p,
        initial_levene_p=initial_levene_p,
        transformed_weekday_normality_p=transformed_weekday_normality_p,
        transformed_weekend_normality_p=transformed_weekend_normality_p,
        transformed_levene_p=transformed_levene_p,
        weekly_weekday_normality_p=weekly_weekday_normality_p,
        weekly_weekend_normality_p=weekly_weekend_normality_p,
        weekly_levene_p=weekly_levene_p,
        weekly_ttest_p=weekly_ttest_p,
        utest_p=utest_p,
    ))


if __name__ == '__main__':
    main()