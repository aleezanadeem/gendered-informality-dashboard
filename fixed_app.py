import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Query 1: Gendered Informality in Creative Occupations", layout="wide")

st.title("Query 1: Gendered Informality in Creative Occupations")

# Load dataset
q1_file = "EMP_TEM2_SEX_EC4_IFL_NB_A.csv"
q1_data = pd.read_csv(q1_file)

# Filter for Level 2
q1_filtered = q1_data[
    (q1_data['classif1'] == 'EC4_MEDIAISIC_YES') &
    (q1_data['classif2'].isin(['IFL_NATURE_FORMAL', 'IFL_NATURE_INFORMAL'])) &
    (q1_data['ref_area'].isin(['GBR', 'FRA', 'BRA', 'ARG', 'KHM', 'COL'])) &
    (q1_data['sex'].isin(['SEX_M', 'SEX_F']))
][['ref_area', 'time', 'sex', 'classif2', 'obs_value']]

# Pivot for informality
q1_pivot = q1_filtered.pivot_table(
    index=['ref_area', 'time', 'sex'],
    columns='classif2',
    values='obs_value',
    aggfunc='sum'
).reset_index()

q1_pivot['informality_rate'] = q1_pivot['IFL_NATURE_INFORMAL'] / (
    q1_pivot['IFL_NATURE_FORMAL'] + q1_pivot['IFL_NATURE_INFORMAL']
)

# Sidebar Filters
st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Select Countries", q1_pivot['ref_area'].unique(),
                                   default=q1_pivot['ref_area'].unique())
genders = st.sidebar.multiselect("Select Genders", ['SEX_M', 'SEX_F'], default=['SEX_M','SEX_F'])
year_range = st.sidebar.slider("Select Year Range", int(q1_pivot['time'].min()), int(q1_pivot['time'].max()),
                               (2015, 2024))

# Apply Filters
filtered_data = q1_pivot[
    (q1_pivot['ref_area'].isin(countries)) &
    (q1_pivot['sex'].isin(genders)) &
    (q1_pivot['time'] >= year_range[0]) &
    (q1_pivot['time'] <= year_range[1])
]

# Tabs
tabs = st.tabs([
    "Descriptive Stats", "Female vs Male %", "Gender Gap Over Time", "Cross-Country Averages",
    "Gender Comparison by Country", "Trends by Country", "Cross-Country (Both Genders)",
    "Combined Gender-Country Trends", "Coverage Table", "Summary Findings", "Policy Implications"
])

with tabs[0]:
    st.subheader("Descriptive Statistics")
    desc_stats = filtered_data.groupby(['ref_area', 'sex']).agg(
        mean_informality=('informality_rate', 'mean'),
        median_informality=('informality_rate', 'median'),
        min_informality=('informality_rate', 'min'),
        max_informality=('informality_rate', 'max'),
        count_obs=('informality_rate', 'count')
    ).reset_index()
    st.dataframe(desc_stats)
    st.markdown("""
    **What it means:** Provides averages, medians, and ranges of informality rates by country and gender.  
    **Why do it:** Establishes a baseline for understanding gender differences.  
    **Findings:** Cambodia shows the highest levels; France & UK the lowest; Latin America in the middle.  
    """)

with tabs[1]:
    st.subheader("Female vs Male Informality Percentages")
    pivot_gender = desc_stats.pivot(index='ref_area', columns='sex', values='mean_informality').reset_index()
    pivot_gender['female_vs_male_pct'] = (pivot_gender['SEX_F'] / pivot_gender['SEX_M']) * 100
    fig, ax = plt.subplots(figsize=(10,6))
    bars = ax.bar(pivot_gender['ref_area'], pivot_gender['female_vs_male_pct'], color='skyblue')
    ax.axhline(100, color='red', linestyle='--')
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{bar.get_height():.1f}%', 
                ha='center', va='bottom')
    ax.set_title("Female Informality as % of Male Informality")
    ax.set_ylabel("Female % of Male Rate")
    ax.set_xlabel("Country")
    ax.grid(axis='y')
    st.pyplot(fig)
    st.markdown("""
    **What it means:** Compares women’s informality as a % of men’s.  
    **Why do it:** Normalizes data to highlight gender inequality.  
    **Findings:** Cambodia >100% (women worse off); Brazil <100% (men worse off); France & UK low and balanced.  
    """)

with tabs[2]:
    st.subheader("Gender Gap Over Time")
    if 'SEX_F' in filtered_data['sex'].unique() and 'SEX_M' in filtered_data['sex'].unique():
        gender_gap = filtered_data.pivot_table(
            index=['ref_area','time'], columns='sex', values='informality_rate', aggfunc='mean'
        ).reset_index()
        gender_gap['gender_gap'] = gender_gap['SEX_F'] - gender_gap['SEX_M']
        fig, ax = plt.subplots(figsize=(12,6))
        for country in gender_gap['ref_area'].unique():
            subset = gender_gap[gender_gap['ref_area'] == country]
            ax.plot(subset['time'], subset['gender_gap'], marker='o', label=country)
        ax.axhline(0, color='black', linestyle='--')
        ax.set_title("Gender Gap in Informality (Female - Male)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Gap (Positive = Women Higher)")
        ax.legend()
        st.pyplot(fig)
        st.markdown("""
        **What it means:** Shows female rate minus male rate by year.  
        **Why do it:** Highlights direction & size of gender inequality.  
        **Findings:** Cambodia positive (women worse off), Brazil negative (men worse off), France & UK near zero.  
        """)
    else:
        st.info("Please select both Male and Female to view Gender Gap.")

with tabs[3]:
    st.subheader("Cross-Country Informality Averages")
    cross_country_avg = filtered_data.groupby(['ref_area','time'])['informality_rate'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(12,6))
    for country in cross_country_avg['ref_area'].unique():
        subset = cross_country_avg[cross_country_avg['ref_area'] == country]
        ax.plot(subset['time'], subset['informality_rate'], marker='o', label=country)
    ax.set_title("Cross-Country Average Informality Rates")
    ax.set_xlabel("Year")
    ax.set_ylabel("Informality Rate")
    ax.legend()
    st.pyplot(fig)
    st.markdown("""
    **What it means:** Averages men & women’s rates by country.  
    **Why do it:** Shows long-term trends across countries.  
    **Findings:** Cambodia highest; France & UK lowest; Latin America mid-level, declining.  
    """)

with tabs[4]:
    st.subheader("Average Informality Rates by Gender and Country")
    bar_width = 0.35
    pivot_gender = desc_stats.pivot(index='ref_area', columns='sex', values='mean_informality').reset_index()
    fig, ax = plt.subplots(figsize=(12,6))
    bars_m = ax.bar(pivot_gender.index - bar_width/2, pivot_gender['SEX_M'], width=bar_width, label='Male')
    bars_f = ax.bar(pivot_gender.index + bar_width/2, pivot_gender['SEX_F'], width=bar_width, label='Female')
    ax.set_xticks(pivot_gender.index)
    ax.set_xticklabels(pivot_gender['ref_area'])
    ax.set_title("Average Informality Rates by Gender and Country")
    ax.set_ylabel("Mean Informality Rate")
    ax.legend()
    for bar in list(bars_m) + list(bars_f):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{bar.get_height():.2f}', ha='center', va='bottom')
    st.pyplot(fig)
    st.markdown("""
    **What it means:** Side-by-side bars compare male vs female rates.  
    **Why do it:** Direct gender comparison within each country.  
    **Findings:** Cambodia women worse off; Brazil & Colombia men worse off; France & UK lowest overall.  
    """)

with tabs[5]:
    st.subheader("Trends by Country and Gender")
    for country in filtered_data['ref_area'].unique():
        fig, ax = plt.subplots(figsize=(8,5))
        subset = filtered_data[filtered_data['ref_area'] == country]
        for gender in genders:
            gender_data = subset[subset['sex'] == gender]
            ax.plot(gender_data['time'], gender_data['informality_rate'], marker='o', label=gender)
        ax.set_title(f"Trend of Informality Rates ({country})")
        ax.set_xlabel("Year")
        ax.set_ylabel("Informality Rate")
        ax.legend(title="Gender")
        st.pyplot(fig)
    st.markdown("""
    **What it means:** Shows trends for each country separately.  
    **Why do it:** Lets us see country-level gender patterns.  
    **Findings:** Cambodia: women worse off; Brazil: men worse off; Europe: stable, low.  
    """)

with tabs[6]:
    st.subheader("Cross-Country Comparison (Both Genders)")
    fig, ax = plt.subplots(figsize=(12,6))
    for country in filtered_data['ref_area'].unique():
        avg_country = filtered_data[filtered_data['ref_area'] == country].groupby('time')['informality_rate'].mean()
        ax.plot(avg_country.index, avg_country.values, marker='o', label=country)
    ax.set_title("Cross-Country Comparison of Informality Rates")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Informality Rate")
    ax.legend()
    st.pyplot(fig)
    st.markdown("""
    **What it means:** Combines men and women averages.  
    **Why do it:** Overview of global creative sector informality.  
    **Findings:** Cambodia highest; Europe lowest; Latin America mid-level.  
    """)

with tabs[7]:
    st.subheader("Informality Rates by Country and Gender (Combined)")
    fig, ax = plt.subplots(figsize=(12,6))
    for country in filtered_data['ref_area'].unique():
        subset = filtered_data[filtered_data['ref_area'] == country]
        for gender in genders:
            gender_data = subset[subset['sex'] == gender]
            ax.plot(gender_data['time'], gender_data['informality_rate'], marker='o', label=f"{country}-{gender}")
    ax.set_title("Informality Rates in Creative Occupations by Country and Gender")
    ax.set_xlabel("Year")
    ax.set_ylabel("Informality Rate")
    ax.legend()
    st.pyplot(fig)
    st.markdown("""
    **What it means:** Combines all countries and genders in one chart.  
    **Why do it:** Allows cross-country and cross-gender comparison at once.  
    **Findings:** Confirms Cambodia worst, France & UK best, others mid-level.  
    """)

with tabs[8]:
    st.subheader("Coverage Table (Year Range by Country and Gender)")
    coverage_table = filtered_data.groupby(['ref_area', 'sex']).agg(
        min_year=('time', 'min'),
        max_year=('time', 'max'),
        count_obs=('time', 'count')
    ).reset_index()
    st.dataframe(coverage_table)

with tabs[9]:
    st.subheader("Summary Findings")
    st.markdown("""
    - Cambodia: Highest informality, women more likely to be in informal employment.
    - Brazil & Colombia: Men more likely, though women remain vulnerable.
    - Argentina: Near parity; moderate informality.
    - France & UK: Lowest and most stable; narrow gender gaps.
    - Trends: Europe stable, Latin America slightly declining, Cambodia persistently high.
    - Data Gaps: FRA, ARG, KHM end in 2023; GBR, BRA, COL extend to 2024.
    """)

with tabs[10]:
    st.subheader("Policy Implications")
    st.markdown("""
    - Formalization in Developing Economies: Simplify registration and incentivize formal hiring.
    - Gender-Specific Protections: Cambodia – maternity & childcare support; Brazil & Colombia – balanced social protections.
    - Maintain Protections in Europe: Safeguard against gig-economy erosion.
    - Union & Guild Support: Strengthen MEAA, UNI MEI, CICADA, and Colombian musician guilds.
    - Improve Data Quality: Harmonize surveys and strengthen Cambodia & Argentina statistics.
    """)

