import streamlit as st
import pandas as pd

# Define Australian rebar sizes and their nominal mass per meter (kg/m)
# Based on common Australian standards (e.g., AS/NZS 4671)
REBAR_WEIGHTS = {
    "N10": 0.617,
    "N12": 0.888,
    "N16": 1.579,
    "N20": 2.466,
    "N24": 3.551,
    "N28": 4.834,
    "N32": 6.313,
    "N36": 7.990,
    "N40": 9.865,
    "N50": 15.420, # Added N50 as it's also common
}

# --- Helper Function to Calculate Bar Weight ---
def calculate_bar_weight(bar_size, quantity, length_per_bar_m):
    """
    Calculates the total weight for a given bar size, quantity, and length.
    Args:
        bar_size (str): The size of the rebar (e.g., "N12").
        quantity (int): The number of bars.
        length_per_bar_m (float): The length of a single bar in meters.
    Returns:
        float: Total weight in kg.
    """
    if bar_size not in REBAR_WEIGHTS:
        st.error(f"Error: Bar size '{bar_size}' not recognized.")
        return 0.0
    
    if quantity < 0 or length_per_bar_m < 0:
        st.warning("Quantity and length cannot be negative. Skipping calculation for this item.")
        return 0.0

    unit_weight = REBAR_WEIGHTS[bar_size]
    total_length = quantity * length_per_bar_m
    total_weight = total_length * unit_weight
    return total_weight, unit_weight, total_length

# --- Streamlit Application UI ---
st.set_page_config(page_title="Concrete Reinforcement Cage Weight Calculator", layout="centered")

st.title("🏗️ Concrete Reinforcement Cage Weight Calculator")
st.markdown("Calculate the total weight of your concrete reinforcement cages based on Australian standards.")

# --- Cage Type Selection ---
cage_type = st.selectbox(
    "Select the Type of Cage:",
    ("Wall Cage", "Column Cage", "Pile Cage")
)

st.markdown("---")

# --- Wall Cage Calculation Section ---
if cage_type == "Wall Cage":
    st.header("🧱 Wall Cage Details")

    st.subheader("Vertical Bars")
    col1, col2, col3 = st.columns(3)
    with col1:
        vert_bar_size = st.selectbox("Size of Vertical Bars:", list(REBAR_WEIGHTS.keys()), key="vert_size")
    with col2:
        vert_bar_qty = st.number_input("Quantity of Vertical Bars:", min_value=0, value=10, step=1, key="vert_qty")
    with col3:
        # Assuming length of vertical bar is the height of the wall
        vert_bar_length_m = st.number_input("Length of Each Vertical Bar (m):", min_value=0.0, value=3.0, step=0.1, key="vert_length")

    st.subheader("Horizontal Bars")
    col4, col5, col6 = st.columns(3)
    with col4:
        horiz_bar_size = st.selectbox("Size of Horizontal Bars:", list(REBAR_WEIGHTS.keys()), key="horiz_size")
    with col5:
        horiz_bar_qty = st.number_input("Quantity of Horizontal Bars:", min_value=0, value=10, step=1, key="horiz_qty")
    with col6:
        # Assuming length of horizontal bar is the width/length of the wall section
        horiz_bar_length_m = st.number_input("Length of Each Horizontal Bar (m):", min_value=0.0, value=6.0, step=0.1, key="horiz_length")
    
    st.subheader("Links/Ties (for maintaining spacing)")
    col7, col8, col9 = st.columns(3)
    with col7:
        link_size = st.selectbox("Size of Links:", list(REBAR_WEIGHTS.keys()), key="link_size")
    with col8:
        # Assuming length of link is its perimeter
        link_length_m = st.number_input("Length of Each Link (m) (Perimeter):", min_value=0.0, value=1.0, step=0.1, key="link_length")
    with col9:
        link_qty = st.number_input("Quantity of Links:", min_value=0, value=50, step=1, key="link_qty")
    
    st.markdown("---")

    if st.button("Calculate Wall Cage Weight"):
        st.subheader("Weight Calculation Summary")
        
        calculation_data = []
        total_cage_weight = 0.0

        # Calculate Vertical Bars weight
        vert_weight, vert_unit_weight, vert_total_length = calculate_bar_weight(vert_bar_size, vert_bar_qty, vert_bar_length_m)
        calculation_data.append({
            "Component": "Vertical Bars",
            "Bar Size": vert_bar_size,
            "Quantity": vert_bar_qty,
            "Length per Bar (m)": vert_bar_length_m,
            "Total Length (m)": vert_total_length,
            "Unit Weight (kg/m)": vert_unit_weight,
            "Total Weight (kg)": vert_weight
        })
        total_cage_weight += vert_weight

        # Calculate Horizontal Bars weight
        horiz_weight, horiz_unit_weight, horiz_total_length = calculate_bar_weight(horiz_bar_size, horiz_bar_qty, horiz_bar_length_m)
        calculation_data.append({
            "Component": "Horizontal Bars",
            "Bar Size": horiz_bar_size,
            "Quantity": horiz_bar_qty,
            "Length per Bar (m)": horiz_bar_length_m,
            "Total Length (m)": horiz_total_length,
            "Unit Weight (kg/m)": horiz_unit_weight,
            "Total Weight (kg)": horiz_weight
        })
        total_cage_weight += horiz_weight

        # Calculate Links weight
        link_weight, link_unit_weight, link_total_length = calculate_bar_weight(link_size, link_qty, link_length_m)
        calculation_data.append({
            "Component": "Links",
            "Bar Size": link_size,
            "Quantity": link_qty,
            "Length per Link (m) (Perimeter)": link_length_m,
            "Total Length (m)": link_total_length,
            "Unit Weight (kg/m)": link_unit_weight,
            "Total Weight (kg)": link_weight
        })
        total_cage_weight += link_weight
        
        # Display the table
        df = pd.DataFrame(calculation_data)
        st.dataframe(df.round(2), use_container_width=True) # Round to 2 decimal places for display

        st.success(f"**Total Estimated Wall Cage Weight: {total_cage_weight:.2f} kg**")

# --- Placeholder Sections for other cage types ---
elif cage_type == "Column Cage":
    st.header("C-Column Cage Details")
    st.info("This section is under construction. Please select 'Wall Cage' for current calculations.")
    st.write("You could add inputs for:")
    st.write("- Main vertical bar size and quantity")
    st.write("- Tie bar size, quantity, and dimensions")
    st.write("- Length of column")

elif cage_type == "Pile Cage":
    st.header("🕳️ Pile Cage Details")
    st.info("This section is under construction. Please select 'Wall Cage' for current calculations.")
    st.write("You could add inputs for:")
    st.write("- Main longitudinal bar size and quantity")
    st.write("- Spiral/helical bar size, pitch, and total length")
    st.write("- Length of pile")

st.markdown("---")
st.markdown("ℹ️ *Bar weights are based on nominal mass per meter for Australian reinforcing steel standards.*")
st.markdown("---")
