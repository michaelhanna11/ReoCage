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
        tuple: (Total weight in kg, Unit weight in kg/m, Total length in m)
    """
    if bar_size not in REBAR_WEIGHTS:
        st.error(f"Error: Bar size '{bar_size}' not recognized.")
        return 0.0, 0.0, 0.0 # Return all zeros if size is not recognized
    
    if quantity < 0 or length_per_bar_m < 0:
        st.warning(f"Quantity ({quantity}) and length ({length_per_bar_m}) cannot be negative for {bar_size}. Skipping calculation for this item.")
        return 0.0, REBAR_WEIGHTS[bar_size], 0.0 # Return 0 weight, but correct unit weight

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

    # --- Vertical Bars Input ---
    st.subheader("Vertical Bars")
    vertical_bar_inputs = []
    for i in range(3): # Allow for up to 3 different vertical bar types
        st.markdown(f"**Vertical Bar Type {i+1}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            size = st.selectbox(f"Size (Type {i+1}):", list(REBAR_WEIGHTS.keys()), key=f"vert_size_{i}", index=0 if i == 0 else 0)
        with col2:
            qty = st.number_input(f"Quantity (Type {i+1}):", min_value=0, value=0, step=1, key=f"vert_qty_{i}")
        with col3:
            length = st.number_input(f"Length per Bar (m) (Type {i+1}):", min_value=0.0, value=0.0, step=0.1, key=f"vert_length_{i}")
        vertical_bar_inputs.append({"size": size, "qty": qty, "length": length})
    
    # --- Horizontal Bars Input ---
    st.subheader("Horizontal Bars")
    horizontal_bar_inputs = []
    for i in range(3): # Allow for up to 3 different horizontal bar types
        st.markdown(f"**Horizontal Bar Type {i+1}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            size = st.selectbox(f"Size (Type {i+1}):", list(REBAR_WEIGHTS.keys()), key=f"horiz_size_{i}", index=0 if i == 0 else 0)
        with col2:
            qty = st.number_input(f"Quantity (Type {i+1}):", min_value=0, value=0, step=1, key=f"horiz_qty_{i}")
        with col3:
            length = st.number_input(f"Length per Bar (m) (Type {i+1}):", min_value=0.0, value=0.0, step=0.1, key=f"horiz_length_{i}")
        horizontal_bar_inputs.append({"size": size, "qty": qty, "length": length})

    # --- Links/Ties Input ---
    st.subheader("Links/Ties (for maintaining spacing)")
    link_bar_inputs = []
    for i in range(3): # Allow for up to 3 different link types
        st.markdown(f"**Link Type {i+1}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            size = st.selectbox(f"Size (Type {i+1}):", list(REBAR_WEIGHTS.keys()), key=f"link_size_{i}", index=0 if i == 0 else 0)
        with col2:
            # Assuming length of link is its perimeter
            length = st.number_input(f"Length of Each Link (m) (Perimeter) (Type {i+1}):", min_value=0.0, value=0.0, step=0.1, key=f"link_length_{i}")
        with col3:
            qty = st.number_input(f"Quantity (Type {i+1}):", min_value=0, value=0, step=1, key=f"link_qty_{i}")
        link_bar_inputs.append({"size": size, "qty": qty, "length": length})
    
    st.markdown("---")

    if st.button("Calculate Wall Cage Weight"):
        st.subheader("Weight Calculation Summary")
        
        calculation_data = []
        total_cage_weight = 0.0

        # Calculate Vertical Bars weight for all types
        for i, bar_input in enumerate(vertical_bar_inputs):
            if bar_input["qty"] > 0 and bar_input["length"] > 0: # Only calculate if quantity and length are positive
                vert_weight, vert_unit_weight, vert_total_length = calculate_bar_weight(
                    bar_input["size"], bar_input["qty"], bar_input["length"]
                )
                calculation_data.append({
                    "Component": f"Vertical Bars (Type {i+1})",
                    "Bar Size": bar_input["size"],
                    "Quantity": bar_input["qty"],
                    "Length per Bar (m)": bar_input["length"],
                    "Total Length (m)": vert_total_length,
                    "Unit Weight (kg/m)": vert_unit_weight,
                    "Total Weight (kg)": vert_weight
                })
                total_cage_weight += vert_weight

        # Calculate Horizontal Bars weight for all types
        for i, bar_input in enumerate(horizontal_bar_inputs):
            if bar_input["qty"] > 0 and bar_input["length"] > 0: # Only calculate if quantity and length are positive
                horiz_weight, horiz_unit_weight, horiz_total_length = calculate_bar_weight(
                    bar_input["size"], bar_input["qty"], bar_input["length"]
                )
                calculation_data.append({
                    "Component": f"Horizontal Bars (Type {i+1})",
                    "Bar Size": bar_input["size"],
                    "Quantity": bar_input["qty"],
                    "Length per Bar (m)": bar_input["length"],
                    "Total Length (m)": horiz_total_length,
                    "Unit Weight (kg/m)": horiz_unit_weight,
                    "Total Weight (kg)": horiz_weight
                })
                total_cage_weight += horiz_weight

        # Calculate Links weight for all types
        for i, bar_input in enumerate(link_bar_inputs):
            if bar_input["qty"] > 0 and bar_input["length"] > 0: # Only calculate if quantity and length are positive
                link_weight, link_unit_weight, link_total_length = calculate_bar_weight(
                    bar_input["size"], bar_input["qty"], bar_input["length"]
                )
                calculation_data.append({
                    "Component": f"Links (Type {i+1})",
                    "Bar Size": bar_input["size"],
                    "Quantity": bar_input["qty"],
                    "Length per Link (m) (Perimeter)": bar_input["length"],
                    "Total Length (m)": link_total_length,
                    "Unit Weight (kg/m)": link_unit_weight,
                    "Total Weight (kg)": link_weight
                })
                total_cage_weight += link_weight
        
        # Display the table
        if calculation_data:
            df = pd.DataFrame(calculation_data)
            st.dataframe(df.round(2), use_container_width=True) # Round to 2 decimal places for display
            st.success(f"**Total Estimated Wall Cage Weight: {total_cage_weight:.2f} kg**")
        else:
            st.info("No bar details entered or quantities/lengths are zero. Please enter values to calculate weight.")


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
