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

# ✅ No filters – use full dataset
filtered_data = q1_pivot.copy()

# Sidebar Navigation
section = st.sidebar.radio(
    "Navigate to Section:",
    ["Descriptive Stats", "Female vs Male %", "Gender Gap Over Time",
     "Cross-Country Averages", "Gender Comparison by Country",
     "Trends by Country", "Cross-Country (Both Genders)",
     "Combined Gender-Country Trends", "Coverage Table",
     "Summary Findings", "Policy Implications"]
)

# TAB 1
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

# TAB 2
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
    We calculate the **average share of women in informal employment** compared to men.

    * 100% = parity  
    * >100% = women more likely  
    * <100% = men more likely  

    **Findings:**  
    - Cambodia: Women ~111% of men.  
    - Brazil: Men more affected.  
    - Argentina & Colombia: Near parity.  
    - France & UK: Balanced and low.  
    """)

# ⚙️ Repeat same pattern for Tabs 3–10 using your detailed markdown texts
