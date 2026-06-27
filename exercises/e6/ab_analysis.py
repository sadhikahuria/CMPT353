import sys
import pandas as pd
from scipy import stats


OUTPUT_TEMPLATE = (
    '"Did more/less users use the search feature?" p-value:  {more_users_p:.3g}\n'
    '"Did users search more/less?" p-value:  {more_searches_p:.3g} \n'
    '"Did more/less instructors use the search feature?" p-value:  {more_instr_p:.3g}\n'
    '"Did instructors search more/less?" p-value:  {more_instr_searches_p:.3g}'
)

def search_used_p(data):
    table = pd.crosstab(data['uid'] %2, data['search_count'] >0)
    return stats.chi2_contingency(table)[1]

def search_count_p(data):
    og = data[data['uid'] %2 == 0]['search_count']
    improved = data[data['uid'] %2 == 1]['search_count']
    return stats.mannwhitneyu(og, improved, alternative='two-sided')[1]

def main():
    data_file= sys.argv[1]
    data = pd.read_json(data_file,orient='records',lines=True)
    instructors = data[data['is_instructor']]

    print(OUTPUT_TEMPLATE.format(
        more_users_p=search_used_p(data),
        more_searches_p=search_count_p(data),
        more_instr_p=search_used_p(instructors),
        more_instr_searches_p=search_count_p(instructors),
    ))

if __name__ == '__main__':
    main()