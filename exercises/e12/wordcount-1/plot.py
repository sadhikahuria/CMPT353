import argparse
from pathlib import Path

import matplotlib

matplotlib.use('Agg')

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd
import seaborn as sns
from scipy import stats


SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60


parser = argparse.ArgumentParser(description='Create figures for pup inflation.')
parser.add_argument('input_csv', help='CSV file containing the dog-rates tweets')
parser.add_argument(
    '--output-dir',
    default='.',
    help='directory for the generated PNG files (default: current directory)',
)
args = parser.parse_args()

output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)

data = pd.read_csv(args.input_csv)
data['rating'] = pd.to_numeric(
    data['text'].str.extract(r'(\d+(?:\.\d+)?)/10', expand=False),
    errors='coerce',
)
data = data[data['rating'].notna() & (data['rating'] <= 25)].copy()
data['created_at'] = pd.to_datetime(data['created_at'], format='ISO8601', utc=True)
data = data.sort_values('created_at')

# Use elapsed years instead of Unix time so the slope has useful units.
first_date = data['created_at'].min()
data['elapsed_years'] = (
    (data['created_at'] - first_date).dt.total_seconds() / SECONDS_PER_YEAR
)
fit = stats.linregress(data['elapsed_years'], data['rating'])
data['prediction'] = fit.intercept + fit.slope * data['elapsed_years']

sns.set_theme(style='whitegrid', context='notebook')

# Figure 1: the individual ratings and the fitted time trend.
fig, ax = plt.subplots(figsize=(9, 5))
sns.scatterplot(
    data=data,
    x='created_at',
    y='rating',
    color='#3B82A0',
    alpha=0.28,
    s=24,
    linewidth=0,
    ax=ax,
)
ax.plot(
    data['created_at'],
    data['prediction'],
    color='#C64B40',
    linewidth=2.5,
    label=f'Linear trend: +{fit.slope:.2f} rating points/year',
)
ax.set(
    title='Dog ratings increased over time',
    xlabel='Tweet date',
    ylabel='Rating (out of 10)',
    ylim=(-0.5, 18),
)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.legend(frameon=False, loc='lower right')
sns.despine(ax=ax)
fig.tight_layout()
ratings_path = output_dir / 'ratings_over_time.png'
fig.savefig(ratings_path, dpi=300, bbox_inches='tight')
plt.close(fig)

# Figure 2: show how the mix of low and high ratings changed each year.
data['year'] = data['created_at'].dt.year
data['rating_group'] = pd.cut(
    data['rating'],
    bins=[float('-inf'), 10, 11, 12, 13, float('inf')],
    labels=['10 or lower', '11', '12', '13', 'Above 13'],
)
rating_mix = pd.crosstab(
    data['year'], data['rating_group'], normalize='index', dropna=False
) * 100

fig, ax = plt.subplots(figsize=(9, 5))
rating_mix.plot.bar(
    stacked=True,
    width=0.72,
    color=sns.color_palette('colorblind', n_colors=rating_mix.shape[1]),
    ax=ax,
)
ax.set(
    title='Higher ratings became more common',
    xlabel='Tweet year',
    ylabel='Share of rated tweets',
    ylim=(0, 100),
)
ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
ax.tick_params(axis='x', rotation=0)
ax.legend(
    title='Rating',
    frameon=False,
    ncol=5,
    loc='upper center',
    bbox_to_anchor=(0.5, -0.15),
)
fig.text(0.99, 0.01, '2019 includes data through May 8.', ha='right', fontsize=9)
sns.despine(ax=ax)
fig.tight_layout(rect=(0, 0.08, 1, 1))
mix_path = output_dir / 'rating_mix_by_year.png'
fig.savefig(mix_path, dpi=300, bbox_inches='tight')
plt.close(fig)

print(f'Usable ratings: {len(data):,}')
print(f'Date range: {data["created_at"].min().date()} to {data["created_at"].max().date()}')
print(f'Trend: {fit.slope:+.3f} rating points/year')
print(f'R-squared: {fit.rvalue ** 2:.4f}')
print(f'p-value: {fit.pvalue:.3g}')
print(f'Saved {ratings_path}')
print(f'Saved {mix_path}')
