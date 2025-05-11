import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

# Set page configuration
st.set_page_config(page_title="India's Data Visualization", page_icon=":bar_chart:", layout="wide")

# Cache data loading to improve performance
@st.cache_data
def load_data():
    try:
        return pd.read_csv("india.csv")
    except FileNotFoundError:
        st.error("Error: 'india.csv' not found. Please ensure the file exists in the correct directory.")
        st.stop()
    except pd.errors.EmptyDataError:
        st.error("Error: 'india.csv' is empty. Please provide a valid CSV file.")
        st.stop()

df = load_data()

# List of states
list_of_states = ["Overall India"] + list(df['State'].unique())

# Sidebar
st.sidebar.title("India's Data Visualization")
st.sidebar.markdown("**Help**: Select a numerical column (e.g., Population) for size and any column for color.")
selected_state = st.sidebar.selectbox("Select the state", list_of_states)

# Primary and secondary columns
primary_columns = [
    "Population", "Male", "Female", "Sex_Ratio", "Literate", "Male_Literate",
    "Female_Literate", "Literacy_Rate", "Female_Literacy_Rate", "SC", "ST",
    "SC_Proportion", "ST_Proportion", "Total_Power_Parity",
    "Power_Parity_Above_Rs_545000", "Housholds_with_Electric_Lighting",
    "Having_latrine_facility_within_the_premises_Total_Households"
]
primary = st.sidebar.selectbox("Select the primary variable (size)", primary_columns)
secondary_columns = [
    "Population", "Male", "Female", "Sex_Ratio", "Literate", "Male_Literate",
    "Female_Literate", "Literacy_Rate", "Female_Literacy_Rate", "SC", "ST",
    "SC_Proportion", "ST_Proportion", "Total_Power_Parity",
    "Power_Parity_Above_Rs_545000", "Housholds_with_Electric_Lighting",
    "Having_latrine_facility_within_the_premises_Total_Households",
    "State", "District"
]
secondary = st.sidebar.selectbox("Select the secondary variable (color)", secondary_columns)

# Filters
st.sidebar.subheader("Filters")
min_population = st.sidebar.slider("Minimum Population", 0, int(df['Population'].max()), 0)
min_literacy = st.sidebar.slider("Minimum Literacy Rate (%)", 0.0, 100.0, 0.0)

# Chart type selection
chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar", "Pie", "Box"])

# Plot button
plot = st.sidebar.button("Plot Graph")
reset = st.sidebar.button("Reset")

# Reset functionality
if reset:
    st.experimental_rerun()

# Notes
st.text("**Note:** The data is from Census 2011 and has not been updated since then.")
st.text("Size represents the primary parameter.")
st.text("Color represents the secondary parameter.")

# Help section
with st.expander("About this Project"):
    st.markdown("""
    This project visualizes India's 2011 Census data. Select a state, primary (size), and secondary (color) parameters to explore districts on a map.
    - **Data Source**: Census 2011
    - **Primary Parameter**: Controls bubble size (numerical, e.g., Population)
    - **Secondary Parameter**: Controls bubble color (numerical or categorical, e.g., Literacy Rate, State)
    - **Filters**: Use sliders to filter districts by population or literacy rate.
    - **Tabs**: Explore map, charts (Bar, Pie, Box), and summary statistics with correlation heatmap.
    """)

# Apply filters
filtered_df = df[df['Population'] >= min_population]
filtered_df = filtered_df[filtered_df['Literacy_Rate'] >= min_literacy]

# Tabs for organization
tab1, tab2, tab3 = st.tabs(["Map", "Charts", "Summary"])

# Plotting logic
if plot:
    # Validation
    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust the filters.")
    else:
        with tab1:  # Map Tab
            with st.spinner("Generating map..."):
                if selected_state == "Overall India":
                    state_df = filtered_df
                    zoom = 3
                    title = "Overall India"
                else:
                    state_df = filtered_df[filtered_df['State'] == selected_state]
                    zoom = 6
                    title = f"{selected_state}"
                
                if state_df.empty:
                    st.warning(f"No data available for {selected_state} with the current filters.")
                else:
                    # Scatter map
                    figure = px.scatter_mapbox(
                        state_df, lat="Latitude", lon="Longitude",
                        hover_name="District", hover_data=["Population", "Literacy_Rate", "Sex_Ratio"],
                        color=secondary, size=primary,
                        color_continuous_scale=px.colors.sequential.Plasma,
                        size_max=15, zoom=zoom, mapbox_style="carto-positron",
                        width=1200, height=700
                    )
                    figure.update_layout(title=title, title_x=0.5)
                    st.plotly_chart(figure, use_container_width=True)

        with tab2:  # Charts Tab
            if selected_state != "Overall India" and not state_df.empty:
                # Bar Chart
                if chart_type == "Bar":
                    st.subheader(f"{primary} by District in {selected_state}")
                    fig_bar = px.bar(
                        state_df, x="District", y=primary,
                        title=f"{primary} in {selected_state}",
                        color=secondary
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                # Pie Chart
                elif chart_type == "Pie":
                    st.subheader(f"{primary} Distribution in {selected_state}")
                    fig_pie = px.pie(
                        state_df, names="District", values=primary,
                        title=f"{primary} Distribution in {selected_state}"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                # Box Plot
                elif chart_type == "Box":
                    st.subheader(f"{primary} Distribution in {selected_state}")
                    fig_box = px.box(
                        state_df, x="State", y=primary,
                        title=f"{primary} Distribution in {selected_state}",
                        color=secondary
                    )
                    st.plotly_chart(fig_box, use_container_width=True)

            else:
                st.warning("Charts are available only for specific states, not 'Overall India'.")

        with tab3:  # Summary Tab
            # Correlation Heatmap
            st.subheader("Correlation Heatmap (Numerical Columns)")
            numerical_cols = state_df.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) > 1:
                # Shorten column names for readability
                short_names = {
                    "Population": "Pop",
                    "Male": "M",
                    "Female": "F",
                    "Sex_Ratio": "SexRatio",
                    "Literate": "Lit",
                    "Male_Literate": "MLit",
                    "Female_Literate": "FLit",
                    "Literacy_Rate": "LitRate",
                    "Female_Literacy_Rate": "FLitRate",
                    "SC": "SC",
                    "ST": "ST",
                    "SC_Proportion": "SCProp",
                    "ST_Proportion": "STProp",
                    "Total_Power_Parity": "PowerParity",
                    "Power_Parity_Above_Rs_545000": "HighParity",
                    "Housholds_with_Electric_Lighting": "ElecLight",
                    "Having_latrine_facility_within_the_premises_Total_Households": "Latrine"
                }
                # Apply short names
                corr_df = state_df[numerical_cols].corr()
                short_labels = [short_names.get(col, col) for col in numerical_cols]
                
                # Create heatmap
                fig_heatmap = ff.create_annotated_heatmap(
                    z=corr_df.values,
                    x=short_labels,
                    y=short_labels,
                    annotation_text=corr_df.round(2).values,
                    colorscale="Plasma",
                    showscale=True
                )
                # Update layout for better readability
                fig_heatmap.update_layout(
                    title="Correlation Heatmap",
                    width=1000,  # Increased width
                    height=800,  # Increased height
                    xaxis=dict(tickangle=45, tickfont=dict(size=10)),  # Rotate x-axis labels
                    yaxis=dict(tickfont=dict(size=10)),  # Adjust y-axis font
                    margin=dict(l=100, r=100, t=100, b=100)  # Adjust margins
                )
                # Adjust annotation font size
                for i in range(len(fig_heatmap.layout.annotations)):
                    fig_heatmap.layout.annotations[i].font.size = 8
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.warning("Not enough numerical columns for correlation heatmap.")

            # Summary Stats
            if selected_state != "Overall India" and not state_df.empty:
                st.subheader(f"Summary for {selected_state}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Population", f"{state_df['Population'].sum():,}")
                col2.metric("Average Literacy Rate", f"{state_df['Literacy_Rate'].mean():.2f}%")
                col3.metric("Total Districts", len(state_df))

                # Top 5 districts
                st.subheader(f"Top 5 Districts by {primary}")
                top_districts = state_df.nlargest(5, primary)[['District', primary]]
                st.table(top_districts)

            else:
                st.subheader("Summary for Overall India")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Population", f"{filtered_df['Population'].sum():,}")
                col2.metric("Average Literacy Rate", f"{filtered_df['Literacy_Rate'].mean():.2f}%")
                col3.metric("Total Districts", len(filtered_df))

    # Download button
    if not state_df.empty:
        st.download_button(
            label="Download Filtered Data",
            data=state_df.to_csv(index=False).encode('utf-8'),
            file_name=f"{selected_state}_filtered_data.csv",
            mime='text/csv'
        )

# Show raw data option
if st.sidebar.checkbox("Show raw data"):
    st.subheader("Raw Data")
    st.write(filtered_df if selected_state == "Overall India" else filtered_df[filtered_df['State'] == selected_state])