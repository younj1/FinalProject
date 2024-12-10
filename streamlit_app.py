import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="Insurance Charges Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("https://raw.githubusercontent.com/rafiky1/ccd/refs/heads/main/insurance.csv")

data = load_data()

# Sidebar Filters
with st.sidebar:
    st.title("Filters")
    st.text("Adjust filters to customize your analysis.")

    # Region filter
    selected_region = st.multiselect(
        "Select Region", data["region"].unique(), default=data["region"].unique()
    )

    # Smoker filter
    smoker_filter = st.radio("Smoker Status", options=["All", "Smokers", "Non-Smokers"], index=0)

    # BMI category filter
    data["BMI Category"] = pd.cut(
        data["bmi"],
        bins=[0, 18.5, 24.9, 29.9, 100],
        labels=["Underweight", "Normal", "Overweight", "Obese"]
    )
    bmi_categories = st.multiselect(
        "BMI Category", options=data["BMI Category"].unique(), default=data["BMI Category"].unique()
    )

    # Number of children filter
    children_range = st.slider(
        "Number of Children", 
        min_value=int(data["children"].min()), 
        max_value=int(data["children"].max()),
        value=(int(data["children"].min()), int(data["children"].max()))
    )

# Apply Filters
filtered_data = data[data["region"].isin(selected_region)]
if smoker_filter == "Smokers":
    filtered_data = filtered_data[filtered_data["smoker"] == "yes"]
elif smoker_filter == "Non-Smokers":
    filtered_data = filtered_data[filtered_data["smoker"] == "no"]
filtered_data = filtered_data[filtered_data["BMI Category"].isin(bmi_categories)]
filtered_data = filtered_data[filtered_data["children"].between(children_range[0], children_range[1])]

# Dashboard Title
st.title("📊 Insurance Charges Dashboard")
st.markdown("Dive into the story behind medical insurance costs! Learn how age, BMI, lifestyle choices, and geography shape your premiums.")

# Tabs for Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Introduction", "Overview", "Drivers of Cost", "Lifestyle & Geography", "Regional Insights"])

# Tab 1: Introduction
with tab1:
    st.header("📚 Introduction")
    st.markdown(
        """ 
        Welcome to the Insurance Charges Dashboard! This project aims to analyze medical insurance costs and their determinants.

        ### Objectives:
        - Explore the relationship between age, BMI, smoker status, and insurance charges.
        - Provide insights through interactive data visualizations.
        - Enable users to filter and explore the data dynamically.

        ### Dataset Overview:
        - **Source:** Public dataset of medical insurance charges.
        - **Columns:** Age, Sex, BMI, Children, Smoker, Region, Charges.
        - **Collection Period:** Specific timeframe not specified.
        """
    )

# Tab 2: Overview
with tab2:
    st.header("🚀 Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Charges", f"${filtered_data['charges'].mean():,.2f}")
    col2.metric("Total Records", len(filtered_data))
    col3.metric("Average BMI", f"{filtered_data['bmi'].mean():.2f}")

    st.markdown("### Smoker vs. Non-Smoker Distribution")
    smoker_fig = px.pie(
        filtered_data,
        names="smoker",
        title="Smoker vs. Non-Smoker Distribution",
    )
    st.plotly_chart(smoker_fig)

# Tab 3: Drivers of Cost
with tab3:
    st.header("📈 Drivers of Insurance Costs")
    col1, col2 = st.columns(2)
    with col1:
        scatter_fig1 = px.scatter(
            filtered_data,
            x="age",
            y="charges",
            color="smoker",
            title="Charges vs. Age",
            labels={"charges": "Insurance Charges", "age": "Age"},
        )
        st.plotly_chart(scatter_fig1)
    with col2:
        scatter_fig2 = px.scatter(
            filtered_data,
            x="bmi",
            y="charges",
            color="smoker",
            title="Charges vs. BMI",
            labels={"charges": "Insurance Charges", "bmi": "BMI"},
        )
        st.plotly_chart(scatter_fig2)

    st.markdown("### Correlation Heatmap: Numeric Features")
    correlation_matrix = filtered_data.select_dtypes(include=["float64", "int64"]).corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlation Between Numeric Features")
    st.pyplot(fig)

# Tab 4: Lifestyle & Geography
with tab4:
    st.header("💡 Lifestyle Choices and Geography")
    st.markdown("### Charges by Number of Children")
    children_bar = px.bar(
        filtered_data,
        x="children",
        y="charges",
        color="children",
        title="Charges by Number of Children",
        labels={"children": "Number of Children", "charges": "Insurance Charges"},
    )
    st.plotly_chart(children_bar)

# Tab 5: Regional Insights
with tab5:
    st.header("🌍 Regional Analysis")
    st.markdown("### Charges by Region")
    regional_fig = px.box(
        filtered_data,
        x="region",
        y="charges",
        color="region",
        title="Charges Distribution by Region",
    )
    st.plotly_chart(regional_fig)

    st.markdown(
        """ 
        ### Future Enhancements:
        - Incorporate additional datasets for predictive modeling.
        - Add machine learning algorithms to predict charges based on user input.
        - Explore more advanced visualization techniques to enhance insights.
        """
    )


