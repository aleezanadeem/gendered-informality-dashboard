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

# Pivot for informality rate
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
    "Descriptive Stats", "Female vs Male %", "Gender Gap Over Time",
    "Cross-Country Averages", "Gender Comparison by Country",
    "Trends by Country", "Cross-Country (Both Genders)",
    "Combined Gender-Country Trends", "Coverage Table",
    "Summary Findings", "Policy Implications"
])

# -------- TAB 1 --------
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
    **What it means:**  
    This table summarizes key informality statistics for each country and gender.

    - **Informality Rate** = proportion of creative sector workers who are informal.  
    - **Columns**: Mean, median, minimum, maximum, and observation count.  

    **Why do it:**  
    To provide a baseline understanding of gendered informality distributions.  

    **Findings:**  
    - Cambodia shows very high informality across genders.  
    - France & UK have the lowest rates.  
    - Brazil, Argentina, and Colombia are in between.  
    """)

# -------- TAB 2 --------
with tabs[1]:
    st.subheader("Female vs Male Informality Percentages")
    desc_stats = filtered_data.groupby(['ref_area', 'sex']).agg(
        mean_informality=('informality_rate', 'mean')
    ).reset_index()
    pivot_gender = desc_stats.pivot(index='ref_area', columns='sex', values='mean_informality').reset_index()
    if set(['SEX_F', 'SEX_M']).issubset(pivot_gender.columns):
        pivot_gender['female_vs_male_pct'] = (pivot_gender['SEX_F'] / pivot_gender['SEX_M']) * 100
        fig, ax = plt.subplots(figsize=(10,6))
        bars = ax.bar(pivot_gender['ref_area'], pivot_gender['female_vs_male_pct'], color='skyblue')
        ax.axhline(100, color='red', linestyle='--')
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{bar.get_height():.1f}%', ha='center', va='bottom')
        st.pyplot(fig)
    else:
        st.info("This chart requires both Male and Female selected in filters.")
    st.markdown("""
    **What it means:**  
    We calculate the **average share of women in informal employment** in the creative sector for each country 
    and compare it to the **average share of men**.

    * 100% = parity → men and women equally likely.  
    * >100% = women more likely.  
    * <100% = men more likely.  

    **Why do it:**  
    Provides a normalized measure of gender inequality.  

    **Findings:**  
    - Cambodia: Women’s share ~111% of men’s.  
    - Brazil: Men more affected.  
    - Argentina & Colombia: Near parity.  
    - France & UK: Balanced and low.  
    """)

# -------- TAB 3 --------
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
        st.pyplot(fig)
    else:
        st.info("Please select both Male and Female to view Gender Gap.")
    st.markdown("""
    **What it means:**  
    For each country and year, we calculate the **difference in informality rates between women and men**:

    * Positive values → women more likely.  
    * Negative values → men more likely.  
    * Zero line → parity.  

    **Why do it:**  
    Shows direction & magnitude of inequality year by year.  

    **Findings:**  
    - Cambodia: Consistently above zero.  
    - Brazil: Consistently below zero.  
    - Argentina: Near zero, fluctuates.  
    - France & UK: Minimal gender gaps.  
    """)

# -------- TAB 4 --------
with tabs[3]:
    st.subheader("Cross-Country Informality Averages")
    cross_country_avg = filtered_data.groupby(['ref_area','time'])['informality_rate'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(12,6))
    for country in cross_country_avg['ref_area'].unique():
        subset = cross_country_avg[cross_country_avg['ref_area'] == country]
        ax.plot(subset['time'], subset['informality_rate'], marker='o', label=country)
    ax.legend()
    st.pyplot(fig)
    st.markdown("""
    **What it means:**  
    This graph plots the **average informality rate** for each country over time, combining both men and women.

    **Findings:**  
    - Cambodia: Persistently highest.  
    - France & UK: Lowest and stable.  
    - Brazil & Argentina: Moderate, slightly declining.  
    - Colombia: Moderate, between Europe and Latin America.  
    """)

# -------- TAB 5 --------
with tabs[4]:
    st.subheader("Average Informality Rates by Gender and Country")
    desc_stats = filtered_data.groupby(['ref_area', 'sex']).agg(
        mean_informality=('informality_rate', 'mean')
    ).reset_index()
    pivot_gender = desc_stats.pivot(index='ref_area', columns='sex', values='mean_informality').reset_index()
    if 'SEX_M' in pivot_gender.columns and 'SEX_F' in pivot_gender.columns:
        bar_width = 0.35
        fig, ax = plt.subplots(figsize=(12,6))
        bars_m = ax.bar(pivot_gender.index - bar_width/2, pivot_gender['SEX_M'], width=bar_width, label='Male')
        bars_f = ax.bar(pivot_gender.index + bar_width/2, pivot_gender['SEX_F'], width=bar_width, label='Female')
        ax.set_xticks(pivot_gender.index)
        ax.set_xticklabels(pivot_gender['ref_area'])
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("This chart requires both Male and Female selected in filters.")
    st.markdown("""
    **What it means:**  
    Side‑by‑side bars show the **average share of men and women in informal employment** within the creative sector.

    * **X-axis**: Countries.  
    * **Y-axis**: Informality rate (proportion informal).  
    * Higher bar = larger share of that gender in informal jobs.  

    **Why do it:**  
    Provides a clear, direct comparison between genders in each country.  

    **Findings:**  
    - Brazil & Colombia: Men more likely.  
    - Cambodia: Women more likely.  
    - Argentina: Near parity.  
    - France & UK: Both genders consistently low.  
    """)

# -------- TAB 6 --------
with tabs[5]:
    st.subheader("Trend of Informality Rates in Creative Occupations (Each Country)")
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
    **What it means:**  
    Shows informality trends for each country, split by gender.  

    **Why do it:**  
    Allows country‑specific analysis of male vs female informality.  

    **Findings:**  
    - Cambodia: Women consistently more likely.  
    - Brazil: Men consistently more likely.  
    - Argentina: Gender gap small and fluctuating.  
    - France & UK: Both genders low and stable.  
    """)

# -------- TAB 7 --------
with tabs[6]:
    st.subheader("Cross-Country Comparison of Informality Rates (Both Genders)")
    fig, ax = plt.subplots(figsize=(12,6))
    for country in filtered_data['ref_area'].unique():
        avg_country = filtered_data[filtered_data['ref_area'] == country].groupby('time')['informality_rate'].mean()
        ax.plot(avg_country.index, avg_country.values, marker='o', label=country)
    ax.legend()
    st.pyplot(fig)
    st.markdown("""
    **What it means:**  
    This graph shows the **average informality rate (men + women)** for each country.  

    **Why do it:**  
    Provides a global overview of informality, not split by gender.  

    **Findings:**  
    - Cambodia: Consistently highest.  
    - France & UK: Consistently lowest.  
    - Brazil & Argentina: Mid-level with slight declines.  
    - Colombia: Moderate, between Europe and Latin America.  
    """)

# -------- TAB 8 --------
with tabs[7]:
    st.subheader("Informality Rates in Creative Occupations by Country and Gender (Combined)")
    fig, ax = plt.subplots(figsize=(12,6))
    for country in filtered_data['ref_area'].unique():
        subset = filtered_data[filtered_data['ref_area'] == country]
        for gender in genders:
            gender_data = subset[subset['sex'] == gender]
            ax.plot(gender_data['time'], gender_data['informality_rate'], marker='o', label=f"{country}-{gender}")
    ax.legend()
    st.pyplot(fig)
    st.markdown("""
    **What it means:**  
    Combines all countries and genders into one chart.  
    * **X-axis**: Years (2015–2024).  
    * **Y-axis**: Informality rate.  
    * Each line = Country–Gender pair.  

    **Why do it:**  
    Enables global comparisons across gender and geography in one figure.  

    **Findings:**  
    - Cambodia: Women consistently above men.  
    - Brazil: Men consistently above women.  
    - France & UK: Both genders lowest and stable.  
    - Argentina & Colombia: Moderate, close to parity.  
    """)

# -------- TAB 9 --------
with tabs[8]:
    st.subheader("Coverage Table (Year Range by Country and Gender)")
    coverage_table = filtered_data.groupby(['ref_area', 'sex']).agg(
        min_year=('time', 'min'),
        max_year=('time', 'max'),
        count_obs=('time', 'count')
    ).reset_index()
    st.dataframe(coverage_table)

# -------- TAB 10 --------
with tabs[9]:
    st.subheader("Summary Findings")
    st.markdown("""
    📊 **Summary Findings**

    * **Cambodia**  
      - Highest informality rates.  
      - Women consistently more likely.  
      - Strong gendered vulnerability in creative sector.  

    * **Brazil & Colombia**  
      - Moderate to high levels.  
      - Men more likely, but women remain vulnerable.  

    * **Argentina**  
      - Near parity; moderate informality.  

    * **France & UK**  
      - Lowest and stable.  
      - Minimal gender gaps.  

    * **Trends (2015–2024)**  
      - Europe: Stable, low.  
      - Latin America: Slight downward trend.  
      - Cambodia: Persistently high.  

    * **Data Gaps**  
      - FRA, ARG, KHM end in 2023.  
      - GBR, BRA, COL extend to 2024.  
      - Cross‑country comparisons after 2023 require caution.  
    """)

# -------- TAB 11 --------
with tabs[10]:
    st.subheader("Policy Implications")
    st.markdown("""
    ## 🎯 Policy Implications

    * **Formalization in Developing Economies**  
      *Why:* Cambodia and Latin America show moderate to high informality.  
      *Action:* Simplify registration, incentivize formal hiring, especially for freelancers.  
      *Source:* ILO Microdata Query Set v7 (Sec 2, Sec 5).  

    * **Gender-Specific Protections**  
      *Why:* Women in Cambodia more affected; men in Brazil & Colombia more affected.  
      *Action:* Cambodia – expand maternity & childcare; Brazil & Colombia – balanced protections.  
      *Source:* ILO Brief 12.  

    * **Maintain Protections in Europe**  
      *Why:* France & UK lowest, but gig work risk exists.  
      *Action:* Maintain strong protections; monitor gig economy.  
      *Source:* ILO Brief 32.  

    * **Union & Guild Support**  
      *Why:* Collective bargaining essential for freelancers.  
      *Action:* Strengthen MEAA, UNI MEI, CICADA, Colombian guilds.  

    * **Improve Data Quality & Comparability**  
      *Why:* FRA, ARG, KHM stop in 2023; UK, BRA, COL extend to 2024.  
      *Action:* Harmonize Labour Force Surveys; strengthen Cambodia & Argentina.  
      *Source:* ILO Microdata Query Set v7.  
    """)


