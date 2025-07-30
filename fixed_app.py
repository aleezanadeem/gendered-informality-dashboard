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

# ✅ No filters – use all data
filtered_data = q1_pivot.copy()

# Sidebar Navigation
section = st.sidebar.radio(
    "Navigate to Section:",
    ["Descriptive Stats", "Female vs Male %", "Gender Gap Over Time",
     "Cross-Country Averages", "Gender Comparison by Country",
     "Trends by Country", "Cross-Country (Both Genders)",
     "Combined Gender-Country Trends",
     "Summary Findings", "Policy Implications"]
)

# -------- TAB 1 --------
if section == "Descriptive Stats":
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
elif section == "Female vs Male %":
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
        st.info("Only one gender present. Showing available data.")
    st.markdown("""
    **What it means:**  
    We calculate the average share of women in informal employment and compare it to men.

    * 100% = parity  
    * >100% = women more likely  
    * <100% = men more likely  

    **Why do it:**  
    Provides a normalized measure of gender inequality.  

    **Findings:**  
    - Cambodia: Women ~111% of men.  
    - Brazil: Men more affected.  
    - Argentina & Colombia: Near parity.  
    - France & UK: Balanced and low.  
    """)

# -------- TAB 3 --------
elif section == "Gender Gap Over Time":
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
    Difference in informality: Female rate − Male rate.  

    * Positive = women more likely  
    * Negative = men more likely  
    * Zero = parity  

    **Why do it:**  
    Shows direction & magnitude of inequality over time.  

    **Findings:**  
    - Cambodia: Women more likely.  
    - Brazil: Men more likely.  
    - Argentina: Near zero, fluctuates.  
    - France & UK: Minimal gaps.  
    """)

# -------- TAB 4 --------
elif section == "Cross-Country Averages":
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
    Plots average informality (men + women) by country over time.  

    **Findings:**  
    - Cambodia: Highest.  
    - France & UK: Lowest and stable.  
    - Brazil & Argentina: Moderate with slight declines.  
    - Colombia: Moderate, between Europe & Latin America.  
    """)

# -------- TAB 5 --------
elif section == "Gender Comparison by Country":
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
        st.info("Only one gender present. Showing available data.")
    st.markdown("""
    **What it means:**  
    Side‑by‑side bars compare men vs women in each country.  

    **Findings:**  
    - Brazil & Colombia: Men more informal.  
    - Cambodia: Women more informal.  
    - Argentina: Near parity.  
    - France & UK: Low, balanced.  
    """)

# -------- TAB 6 --------
elif section == "Trends by Country":
    st.subheader("Trends of Informality Rates in Creative Occupations")
    for country in filtered_data['ref_area'].unique():
        fig, ax = plt.subplots(figsize=(8,5))
        subset = filtered_data[filtered_data['ref_area'] == country]
        for gender in subset['sex'].unique():
            gender_data = subset[subset['sex'] == gender]
            ax.plot(gender_data['time'], gender_data['informality_rate'], marker='o', label=gender)
        ax.set_title(f"{country} Trends")
        ax.set_xlabel("Year")
        ax.set_ylabel("Informality Rate")
        ax.legend(title="Gender")
        st.pyplot(fig)
    st.markdown("""
    **What it means:**  
    Shows trends per country, split by gender.  

    **Findings:**  
    - Cambodia: Women more likely.  
    - Brazil: Men more likely.  
    - Argentina: Small fluctuations.  
    - France & UK: Stable, low.  
    """)

# -------- TAB 7 --------
elif section == "Cross-Country (Both Genders)":
    st.subheader("Cross-Country Comparison of Informality Rates")
    fig, ax = plt.subplots(figsize=(12,6))
    for country in filtered_data['ref_area'].unique():
        avg_country = filtered_data[filtered_data['ref_area'] == country].groupby('time')['informality_rate'].mean()
        ax.plot(avg_country.index, avg_country.values, marker='o', label=country)
    ax.legend()
    st.pyplot(fig)
    st.markdown("""
    **What it means:**  
    Combines men & women to show overall rates.  

    **Findings:**  
    - Cambodia: Highest.  
    - France & UK: Lowest.  
    - Brazil & Argentina: Mid-level, slight declines.  
    - Colombia: Moderate.  
    """)

# -------- TAB 8 --------
elif section == "Combined Gender-Country Trends":
    st.subheader("Informality Rates by Country and Gender (Combined)")
    fig, ax = plt.subplots(figsize=(12,6))
    for country in filtered_data['ref_area'].unique():
        subset = filtered_data[filtered_data['ref_area'] == country]
        for gender in subset['sex'].unique():
            gender_data = subset[subset['sex'] == gender]
            ax.plot(gender_data['time'], gender_data['informality_rate'], marker='o', label=f"{country}-{gender}")
    ax.legend()
    st.pyplot(fig)
    st.markdown("""
    **What it means:**  
    Shows every Country–Gender pair in one chart.  

    **Findings:**  
    - Cambodia: Women above men.  
    - Brazil: Men above women.  
    - France & UK: Lowest, stable.  
    - Argentina & Colombia: Moderate.  
    """)


# -------- TAB 10 --------
elif section == "Summary Findings":
    st.subheader("Summary Findings")
    st.markdown("""
    📊 **Summary Findings**

    * **Cambodia**: Highest, women disadvantaged.  
    * **Brazil & Colombia**: Men more affected, women still vulnerable.  
    * **Argentina**: Near parity.  
    * **France & UK**: Lowest, balanced.  
    * **Trends**: Europe stable, Latin America improving, Cambodia persistently high.  
    * **Data Gaps**: FRA, ARG, KHM end 2023; GBR, BRA, COL extend 2024.  
    """)

# -------- TAB 11 --------
elif section == "Policy Implications":
    st.subheader("Policy Implications")
    st.markdown("""
    ## 🎯 Policy Implications

    * **Formalization in Developing Economies**  
      Simplify registration, incentivize hiring, especially for freelancers.  
      *Source:* ILO Microdata Query Set v7.  

    * **Gender-Specific Protections**  
      Cambodia: maternity & childcare; Brazil & Colombia: balanced protections.  
      *Source:* ILO Brief 12.  

    * **Maintain Protections in Europe**  
      Keep frameworks strong, monitor gig economy.  
      *Source:* ILO Brief 32.  

    * **Union & Guild Support**  
      Strengthen MEAA, UNI MEI, CICADA, Colombian guilds.  

    * **Improve Data Quality & Comparability**  
      FRA, ARG, KHM end 2023; harmonize surveys; build statistical capacity.  
      *Source:* ILO Microdata Query Set v7.  
    """)

