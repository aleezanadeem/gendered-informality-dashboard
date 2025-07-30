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
   **Female vs Male Informality Percentages** Graph

**What it means:**
We calculate the **average share of women in informal employment** in the creative sector for each country and compare it to the **average share of men**.

* A value of **100%** = parity → men and women are equally likely to be in informal jobs.
* A value of **>100%** = women are **more likely to be in informal employment** (i.e., a higher proportion of women in the creative sector lack formal work protections compared to men).
* A value of **<100%** = men are **more likely to be in informal employment** than women.

**Why do it:**
Because absolute informality rates differ across countries, comparing women to men as a percentage provides a **normalized measure of gender inequality**.

* It highlights whether women face **greater relative risk of informal work** or whether men do.
* The **red dashed line at 100%** marks equality for easy interpretation: values above it show women disadvantaged, values below it show men disadvantaged.

**Findings:**

* **Cambodia**: Women’s share of informal employment is \~111% of men’s → women are at a clear disadvantage, with more women than men working without formal contracts or protections.
* **Brazil**: Women’s share is \~75% of men’s → men are more affected by informality than women in creative jobs.
* **Argentina & Colombia**: Rates are close to parity, meaning women and men are similarly likely to be informal.
* **France & UK**: Both genders show balanced and low informality, reflecting stronger labor protections.
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
    **Gender Gap Over Time** Graph

**What it means:**
For each country and year, we calculate the **difference in informality rates between women and men**:

$$
\text{Gender Gap} = \text{Female Informality Rate} - \text{Male Informality Rate}
$$

* **Positive values** → a higher proportion of women in creative jobs are in informal employment compared to men (women more likely to lack formal work protections).
* **Negative values** → a higher proportion of men are in informal employment compared to women.
* **Zero line** → parity: men and women have the same informality rate.

**Why do it:**

* Instead of plotting men and women separately, this graph condenses the difference into **one line per country**, making it easy to see **who is more disadvantaged** in informal work over time.
* It highlights not just whether inequality exists, but **its direction and magnitude** year by year.

**Findings:**

* **Cambodia**: Consistently above zero, meaning women are more likely to be in informal jobs year after year.
* **Brazil**: Consistently below zero, meaning men are more likely to be in informal jobs.
* **Argentina**: The line fluctuates near zero, showing small shifts back and forth but no persistent, large gender imbalance.
* **France & UK**: Stays close to zero, indicating very small gender gaps and relatively equal exposure to informal employment.

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
    **Cross-Country Average Informality Rates Graph**

**What it means:**
This graph plots the **average informality rate** for each country over time, combining both men and women.

* **X-axis**: Years (2015–2024).
* **Y-axis**: Proportion of creative-sector workers in informal employment (higher values = larger share of workers without formal contracts or protections).
* Each line = one country’s trend.

So if a country’s line is higher, it means a **greater proportion of creative workers (both genders) are in informal jobs**.

**Why do it:**

* Looking at averages across men and women provides a **broad picture** of how informal employment evolves in each country.
* Helps identify **which countries have the largest informality challenges** and whether they are improving or worsening over time.
* Makes it possible to compare **long-term national patterns** side by side.

**Findings:**

* **Cambodia**: Persistently the highest — meaning the majority of creative workers lack formal labor protections.
* **France & UK**: The lowest and very stable — showing strong formal employment systems in the creative sector.
* **Brazil and Argentina**: Mid-level informality, with slight declines, suggesting slow improvements.
* **Colombia**: Moderate levels, falling between Latin America and Europe.
* **Important Note**: Data coverage ends in 2023 for **France, Argentina, and Cambodia**, while the UK, Brazil, and Colombia extend to 2024. Cross-country comparisons beyond 2023 must therefore be interpreted cautiously.
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
**Average Informality Rates by Gender and Country**

**What it means:**
This chart compare the **average share of men and women in informal employment** within the creative sector in each country.

* **X-axis**: Countries.
* **Y-axis**: Average informality rate (proportion of creative workers in informal jobs).
* Blue lines = men, Orange bars = women.
* Higher bars = a greater proportion of that gender working without formal contracts or protections.

So, for example, if the male bar is taller than the female bar, it means **a larger share of men in that country are in informal employment** compared to women.

**Why do it:**

* This visualization makes the **gender comparison very clear for each country** at a glance.
* It avoids normalizations and instead shows the **absolute difference in informality rates**.
* Helps identify whether gender inequality in informal work disadvantages **men** or **women** in each country.

**Findings:**

* **Brazil & Colombia**: Men’s bars are higher → men are more likely to be in informal creative employment.
* **Cambodia**: Women’s bar is higher → women are more likely to be in informal creative employment.
* **Argentina**: Male and female bars are nearly the same → informality is relatively balanced between genders.
* **France & UK**: Both genders have very low bars, indicating a **low risk of informality** overall and minimal gender gap.
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

## Trend of Informality Rates in Creative Occupations (Each Country)

**What it means:**
This chart shows the **year‑by‑year trend in informality rates** for men and women in the creative sector, with a separate graph for each country.

* **X-axis**: Years (2015–2024).
* **Y-axis**: Informality rate (proportion of creative workers without formal contracts or protections).
* Two lines per country:

  * **Blue line = Men**
  * **Orange line = Women**
* The distance between the lines reflects the size of the gender gap in that country.

**Why do it:**

* Enables **country‑specific exploration** of how informality evolves over time.
* Helps identify whether informality is trending upward or downward in each country.
* Clearly shows **gender differences within each country**, rather than only aggregated comparisons.

**Findings:**

* **Cambodia**: Women’s line consistently above men’s, showing women are more likely to work informally each year.
* **Brazil**: Men’s line consistently above women’s, meaning men are more exposed to informal creative employment.
* **Argentina**: Male and female lines stay close, fluctuating slightly but generally near parity.
* **France & UK**: Both genders remain at the bottom, with very low and stable informality rates.
* **Colombia**: Moderate informality, with men slightly more affected than women in most years.
 
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
  **Cross-Country Comparison of Informality Rates (Both Genders)**

**What it means:**
This graph shows the **average informality rate** (men and women combined) for each country across the years.

* **X-axis**: Years (2015–2024).
* **Y-axis**: Proportion of all creative‑sector workers (men + women) in informal employment.
* Each line = one country’s combined trend.

So, a country’s line being higher means a **greater share of creative workers (both genders) are in informal jobs** in that country.

**Why do it:**

* Provides a **big-picture view** of how informal employment in the creative sector differs across countries.
* Makes it easy to spot **which countries consistently face higher risks of informal work** and which ones maintain low levels.
* Useful for policy discussions because it focuses on overall workforce conditions rather than gender splits.

**Findings:**

* **Cambodia**: Consistently the highest line → most creative workers lack formal contracts and protections.
* **France & UK**: The lowest and very stable → strong labor institutions keep informal work limited.
* **Brazil & Argentina**: Moderate levels, showing small but steady improvements (slight downward slope).
* **Colombia**: Falls in between Europe and Latin America → moderate levels of informality.
* **Important Note**: Data for **France, Argentina, and Cambodia** stops at 2023, while **UK, Brazil, and Colombia** extend to 2024.
  → Cross-country comparisons after 2023 should be treated with caution.

 
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
**Informality Rates in Creative Occupations by Country and Gender (Combined Line Graph)**

**What it means:**
This chart displays **informality rates over time for both men and women across all six countries** in one figure.

* **X-axis**: Years (2015–2024).
* **Y-axis**: Informality rate = proportion of creative-sector workers in informal employment.
* Each line = a unique **Country–Gender pair** (e.g., “Brazil – Male” or “Cambodia – Female”).

So, when two lines for a country diverge, it means men and women are experiencing **different levels of exposure to informal employment**.

**Why do it:**

* Allows a **global view** of how men and women fare across all countries at once.
* Useful for spotting both **within-country gender gaps** and **cross-country differences**.
* Helps policymakers see **whether inequality is gender-driven, country-driven, or both**.

**Findings:**

* **Cambodia**: Both genders are at high risk, but women’s line is consistently above men’s → women more likely to be in informal creative employment.
* **Brazil**: Men’s line is consistently above women’s → men more likely to be in informal jobs.
* **France & UK**: Both genders remain at the bottom of the graph → consistently low rates and very small gender gaps.
* **Argentina & Colombia**: Show moderate levels; Argentina’s male and female lines are close, while Colombia shows men slightly higher.
* **Important Note**: Data for **France, Argentina, and Cambodia** only extends to 2023, while **UK, Brazil, and Colombia** include 2024. Comparisons in 2024 should therefore focus on countries with available data.
 
    """)


# -------- TAB 10 --------
elif section == "Summary Findings":
    st.subheader("Summary Findings")
    st.markdown("""
  📊 Summary Findings

* **Cambodia**

  * Has the **highest informality rates** among the six countries.
  * Women are consistently **more likely to be in informal creative employment** than men, meaning a greater share of female creative workers lack formal contracts or labor protections.
  * This highlights a strong gendered vulnerability in Cambodia’s creative sector.

* **Brazil & Colombia**

  * Both show **moderate to high levels of informality** compared to Europe.
  * In both countries, **men are more likely than women to be in informal jobs**.
  * However, women remain vulnerable: while men’s rates are higher, female creative workers are still exposed to precarious work.

* **Argentina**

  * Displays **near parity** between men and women, with rates close together.
  * Informality is **moderate**, higher than Europe but not as severe as Cambodia.
  * Gender differences are small, though both groups face significant informality.

* **France & United Kingdom**

  * Consistently report the **lowest informality rates**.
  * Gender gaps are minimal: men and women are almost equally likely to be in formal creative employment.
  * Reflects **strong labor protections** and more robust institutional frameworks in European creative industries.

* **Trends (2015–2024)**

  * **Europe**: Stable low informality, showing no evidence of deterioration.
  * **Latin America (Brazil, Argentina, Colombia)**: Slight downward trend, indicating gradual improvements in formalization.
  * **Cambodia**: Persistently high informality, with little sign of improvement across the period.

* **Data Gaps & Reliability Considerations**

  * Data coverage ends in **2023 for France, Argentina, and Cambodia**, while **UK, Brazil, and Colombia** extend through **2024**.
  * **Cross‑country comparisons after 2023 must be treated cautiously**, since some countries have missing data for the final year.
  * As this is a **Level 2 (Aggregate) query**, reliability is expected to be high (>80%), so we did not filter observations.
  * Nonetheless, uneven data coverage remains a limitation for cross‑country analyses. 
    """)

# -------- TAB 11 --------
elif section == "Policy Implications":
    st.subheader("Policy Implications")
    st.markdown("""
   
## 🎯 Policy Implications

* **Formalization in Developing Economies**

  * *Why:* Cambodia and Latin America (Brazil, Argentina, Colombia) show moderate to high informality in the creative sector.
  * *Action:* Simplify registration, cut barriers, and incentivize formal hiring, especially for freelancers and project‑based workers.
  * *Source:* ILO Microdata Query Set v7 (Sec 2, Sec 5).

* **Gender-Specific Protections**

  * *Why:* Women in Cambodia face higher risks, while men in Brazil and Colombia are more affected — both remain vulnerable.
  * *Action:* In Cambodia: expand maternity and childcare support; in Brazil & Colombia: ensure balanced social protection for both genders.
  * *Source:* ILO Brief 12, *Statistical Profile of the Media and Culture Sector*.

* **Maintain Protections in Europe**

  * *Why:* France and the UK have the lowest rates, but temporary and gig work could pose risks.
  * *Action:* Maintain strong protections and monitor gig‑economy expansion.
  * *Source:* ILO Brief 32, *Statistical Profile of the Media and Culture Sector*.

* **Union & Guild Support**

  * *Why:* Collective bargaining strengthens protections for freelancers and temporary creative workers.
  * *Action:* Support MEAA, UNI MEI, CICADA Cambodia, and Colombian musician guilds in advocacy.

* **Improve Data Quality & Comparability**

  * *Why:* FRA, ARG, and KHM data end in 2023; UK, BRA, and COL extend to 2024 → limits comparisons.
  * *Action:* Harmonize Labour Force Surveys and strengthen statistical capacity in Cambodia and Argentina.
  * *Source:* ILO Microdata Query Set v7.

 
    """)

