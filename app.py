import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Gendered Informality in Creative Occupations", layout="wide")

st.title("Gendered Informality in Creative Occupations")

# Load dataset
q1_file = "EMP_TEM2_SEX_EC4_IFL_NB_A.csv"
q1_data = pd.read_csv(q1_file)

# Filter dataset
q1_filtered = q1_data[
    (q1_data['classif1'] == 'EC4_MEDIAISIC_YES') &
    (q1_data['classif2'].isin(['IFL_NATURE_FORMAL', 'IFL_NATURE_INFORMAL'])) &
    (q1_data['ref_area'].isin(['GBR', 'FRA', 'BRA', 'ARG', 'KHM', 'COL'])) &
    (q1_data['sex'].isin(['SEX_M', 'SEX_F']))
]

q1_filtered = q1_filtered[['ref_area', 'time', 'sex', 'classif2', 'obs_value', 'obs_status']]

# Pivot for informality calculation
q1_pivot = q1_filtered.pivot_table(
    index=['ref_area', 'time', 'sex'],
    columns='classif2',
    values='obs_value',
    aggfunc='sum'
).reset_index()

q1_pivot['informality_rate'] = q1_pivot['IFL_NATURE_INFORMAL'] / (
    q1_pivot['IFL_NATURE_FORMAL'] + q1_pivot['IFL_NATURE_INFORMAL']
)

# Sidebar filters
st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Select Countries", q1_pivot['ref_area'].unique(), default=q1_pivot['ref_area'].unique())
genders = st.sidebar.multiselect("Select Genders", ['SEX_M', 'SEX_F'], default=['SEX_M','SEX_F'])
years = st.sidebar.slider("Select Year Range", int(q1_pivot['time'].min()), int(q1_pivot['time'].max()), (2015,2024))

# Apply filters
filtered_data = q1_pivot[(q1_pivot['ref_area'].isin(countries)) &
                         (q1_pivot['sex'].isin(genders)) &
                         (q1_pivot['time'] >= years[0]) & (q1_pivot['time'] <= years[1])]

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Descriptive Stats", "Trends", "Gender Comparison", "Cross-Country", "Policy Notes"])

with tab1:
    st.subheader("Descriptive Statistics")
    desc_stats = filtered_data.groupby(['ref_area', 'sex']).agg(
        mean_informality=('informality_rate', 'mean'),
        median_informality=('informality_rate', 'median'),
        min_informality=('informality_rate', 'min'),
        max_informality=('informality_rate', 'max')
    ).reset_index()
    st.dataframe(desc_stats)

with tab2:
    st.subheader("Trends by Country")
    for country in filtered_data['ref_area'].unique():
        fig, ax = plt.subplots(figsize=(8,5))
        subset = filtered_data[filtered_data['ref_area'] == country]
        for gender in genders:
            gender_data = subset[subset['sex'] == gender]
            ax.plot(gender_data['time'], gender_data['informality_rate'], marker='o', label=f"{gender}")
            unreliable = gender_data[q1_filtered['obs_status'] == 'Unreliable']
            ax.scatter(unreliable['time'], unreliable['informality_rate'], color='red', marker='x', s=100, label=f"{gender} Unreliable")
        ax.set_title(f"Informality Trends in {country}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Informality Rate")
        ax.legend()
        st.pyplot(fig)

with tab3:
    st.subheader("Gender Comparison")
    gender_avg = filtered_data.groupby(['ref_area', 'sex'])['informality_rate'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10,6))
    for country in gender_avg['ref_area'].unique():
        subset = gender_avg[gender_avg['ref_area'] == country]
        ax.bar([f"{country}-M", f"{country}-F"], subset['informality_rate'])
    ax.set_title("Average Informality by Gender")
    ax.set_ylabel("Mean Informality Rate")
    st.pyplot(fig)

with tab4:
    st.subheader("Cross-Country Comparison")
    fig, ax = plt.subplots(figsize=(12,6))
    for country in filtered_data['ref_area'].unique():
        avg_country = filtered_data[filtered_data['ref_area'] == country].groupby('time')['informality_rate'].mean()
        ax.plot(avg_country.index, avg_country.values, marker='o', label=country)
    ax.set_title("Cross-Country Average Informality Rates")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Informality Rate")
    ax.legend()
    st.pyplot(fig)

with tab5:
    st.subheader("Policy Implications")
    st.markdown("""
    - **Strengthen Formalization Initiatives**: Incentivize formal contracts in creative industries, especially in Latin America and Cambodia.  
    - **Gender-Focused Protections**: Provide maternity benefits, flexible protections, and enforce labor laws.  
    - **Support Unions & Guilds**: Enhance MEAA, UNI MEI, CICADA Cambodia, Colombian musician guilds for advocacy.  
    - **International Cooperation**: Leverage ILO frameworks to harmonize survey quality.  
    - **Data Quality Investment**: Address unreliable survey flags with more consistent methodologies.  

    **Source Basis:** Derived from ILO guidelines, ISIC Rev.4 frameworks, and stakeholder notes (MEAA, UNI MEI, CICADA Cambodia, Colombian musician interviews).
    """)
