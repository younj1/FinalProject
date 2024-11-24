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
    # Load both CSV files
    df1 = pd.read_csv("https://raw.githubusercontent.com/rafiky1/ccd/refs/heads/main/insurance.csv")
    df2 = pd.read_csv("https://raw.githubusercontent.com/younj1/FinalProject/refs/heads/main/healthcare_dataset.csv")
    
    return df1, df2

# Load the datasets
data1, data2 = load_data()

# Merge data1 and data2 on common features (assuming 'patient_id' is the shared column, adjust as needed)
# If there's no shared column, we can combine them based on matching index or other columns
data = data1.copy()
data["health_condition"] = data2["health_condition"]  # Add health condition from data2
data["education"] = data2["education"]  # Add other features like education from data2

# Sidebar
with st.sidebar:
    st.title("🔍 Filters")
    
    selected_region = st.multiselect(
        "Filter by Region", data["region"].unique(), default=data["region"].unique()
    )
    
    # Include Smokers Only checkbox
    include_smokers = st.checkbox("Include Smokers Only", value=False)
    include_nonsmokers = st.checkbox("Include Non-Smokers Only", value=False)
    
    bmi_range = st.slider("Select BMI Range", min_value=int(data['bmi'].min()), max_value=int(data['bmi'].max()), value=(18, 30))
    age_range = st.slider("Age Range", int(data["age"].min()), int(data["age"].max()), (18, 60))
    theme = st.radio("Choose Theme", ["Light Theme", "Dark Theme"], index=0)

# Apply Filters
filtered_data = data[data["region"].isin(selected_region)]

# Handle Smoker and Non-Smoker Filters
if include_smokers and include_nonsmokers:
    st.warning("Please select either Smokers Only or Non-Smokers Only, not both.")
    include_smokers = False  # Automatically uncheck one
elif include_smokers:
    filtered_data = filtered_data[filtered_data["smoker"] == "yes"]
elif include_nonsmokers:
    filtered_data = filtered_data[filtered_data["smoker"] == "no"]

# Filter by BMI range
filtered_data = filtered_data[(filtered_data['bmi'] >= bmi_range[0]) & (filtered_data['bmi'] <= bmi_range[1])]

# Filter by age range
filtered_data = filtered_data[(filtered_data["age"] >= age_range[0]) & (filtered_data["age"] <= age_range[1])]

# Set Theme
template = "plotly_white" if theme == "Light Theme" else "plotly_dark"

# Dashboard Title
st.title("📊 Insurance Charges Dashboard")
st.markdown("Dive into the story behind medical insurance costs! Learn how age, BMI, lifestyle choices, and geography shape your premiums.")

# Tabs for Navigation
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Drivers of Cost", "Lifestyle & Geography", "Regional Insights"])

# Tab 1: Overview
with tab1:
    st.header("🚀 Overview")
    
    # Metrics in columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Charges", f"${filtered_data['charges'].mean():,.2f}")
    col2.metric("Total Records", len(filtered_data))
    col3.metric("Average BMI", f"{filtered_data['bmi'].mean():.2f}")
    
    # Smoker vs Non-Smoker Distribution
    st.markdown("### Smoker vs. Non-Smoker Distribution")
    
    # Define color scheme based on the checkbox
    color_map = {"yes": "red", "no": "blue"}
    
    smoker_fig = px.pie(
        filtered_data,
        names="smoker",
        title=f"Smoker vs. Non-Smoker Distribution ({len(filtered_data)} records)",
        template=template,
        color="smoker",
        color_discrete_map=color_map  # Apply the dynamic color map
    )
    st.plotly_chart(smoker_fig)

    # Move the table to the bottom of the tab
    st.markdown("### Data Sample")
    st.dataframe(filtered_data[['age', 'bmi', 'charges', 'smoker', 'region', 'health_condition', 'education']].head(10), height=400)

# Tab 2: Drivers of Cost
with tab2:
    st.header("📈 Drivers of Insurance Costs")
    col1, col2 = st.columns(2)
    with col1:
        scatter_fig1 = px.scatter(
            filtered_data,
            x="age",
            y="charges",
            color="smoker",
            title=f"Charges vs. Age ({len(filtered_data)} records)",
            labels={"charges": "Insurance Charges", "age": "Age"},
            template=template,
            hover_data=["age", "charges", "health_condition"]
        )
        st.plotly_chart(scatter_fig1)
    with col2:
        scatter_fig2 = px.scatter(
            filtered_data,
            x="bmi",
            y="charges",
            color="smoker",
            title=f"Charges vs. BMI ({len(filtered_data)} records)",
            labels={"charges": "Insurance Charges", "bmi": "BMI"},
            template=template,
            hover_data=["bmi", "charges", "health_condition"]
        )
        st.plotly_chart(scatter_fig2)

    st.markdown("### Correlation Matrix: Numeric Features")
    # Compute the correlation matrix for numerical columns
    correlation_matrix = filtered_data.select_dtypes(include=["float64", "int64"]).corr()

    # Display the full correlation matrix
    st.write(correlation_matrix)

    # Create a heatmap for visualizing the correlation matrix using Plotly
    try:
        fig = px.imshow(
            correlation_matrix,
            color_continuous_scale='RdBu',  # Use a valid colorscale
            title="Correlation Heatmap",
            labels={'x': 'Features', 'y': 'Features'},
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            aspect="auto"
        )
        st.plotly_chart(fig)
    except ValueError as e:
        st.error(f"Error generating the heatmap: {e}")

# Tab 3: Lifestyle & Geography
with tab3:
    st.header("💡 Lifestyle Choices and Insurance Costs")
    st.markdown("### Charges by Health Condition")
    health_condition_bar = px.bar(
        filtered_data,
        x="health_condition",
        y="charges",
        color="health_condition",
        title=f"Charges by Health Condition ({len(filtered_data)} records)",
        labels={"health_condition": "Health Condition", "charges": "Insurance Charges"},
        template=template,
    )
    st.plotly_chart(health_condition_bar)

    st.markdown("### Stacked Bar Chart: Charges by Region and Smoker Status")
    stacked_bar = px.bar(
        filtered_data,
        x="region",
        y="charges",
        color="smoker",
        title="Charges by Region and Smoker Status",
        barmode="stack",
        template=template,
    )
    st.plotly_chart(stacked_bar)

    st.markdown("### Charges by BMI Category")
    filtered_data["BMI Category"] = pd.cut(
        filtered_data["bmi"],
        bins=[0, 18.5, 24.9, 29.9, 100],
        labels=["Underweight", "Normal", "Overweight", "Obese"],
    )
    bmi_fig = px.box(
        filtered_data,
        x="BMI Category",
        y="charges",
        color="BMI Category",
        title="Charges by BMI Category",
        labels={"BMI Category": "BMI Category", "charges": "Insurance Charges"},
        template=template,
    )
    st.plotly_chart(bmi_fig)

# Tab 4: Regional Insights
with tab4:
    st.header("🌍 Regional Analysis")
    
    st.markdown("### Charges by Region")
    regional_fig = px.box(
        filtered_data,
        x="region",
        y="charges",
        color="region",
        title="Charges Distribution by Region",
        template=template,
    )
    st.plotly_chart(regional_fig)

    st.markdown("### Grouped Bar Chart: Average Charges by Children and Smoker Status")
    grouped_data = filtered_data.groupby(["children", "smoker"])["charges"].mean().reset_index()
    grouped_bar = px.bar(
        grouped_data,
        x="children",
        y="charges",
        color="smoker",
        barmode="group",
        title="Average Charges by Number of Children and Smoker Status",
        labels={"children": "Number of Children", "charges": "Insurance Charges"},
        template=template,
    )
    st.plotly_chart(grouped_bar)

    st.markdown("### Charges by Age Group")
    filtered_data["Age Group"] = pd.cut(
        filtered_data["age"],
        bins=[18, 35, 50, 65, 100],
        labels=["Young Adults (18-35)", "Middle-Aged (36-50)", "Older Adults (51-65)", "Seniors (65+)"],
    )
    age_group_bar = px.box(
        filtered_data,
        x="Age Group",
        y="charges",
        color="Age Group",
        title="Charges by Age Group",
        labels={"Age Group": "Age Group", "charges": "Insurance Charges"},
        template=template,
    )
    st.plotly_chart(age_group_bar)

# Display Columns of data2 at the bottom
st.markdown("### Columns in the Healthcare Dataset (data2):")
st.write(data2.columns)
