import streamlit as st
import pandas as pd
import io
import requests
import os
from datetime import datetime

# Import ReportLab modules
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY # Added TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

# --- Constants for PDF Report (Customized from Wind Load Calculator) ---
# Replace with your actual logo URL. Using a placeholder image for demonstration.
LOGO_URL = "https://placehold.co/100x40/FF0000/FFFFFF?text=COMPANY+LOGO"
FALLBACK_LOGO_URL = "https://placehold.co/100x40/0000FF/FFFFFF?text=FALLBACK+LOGO" 
COMPANY_NAME = "Your Company Name Pty Ltd" # From Wind Load Calculator
COMPANY_ADDRESS = "123 Main Street, Sydney NSW 2000, Australia" # From Wind Load Calculator
PROGRAM = "Rebar Calc App" # From Wind Load Calculator
PROGRAM_VERSION = "1.0" # From Wind Load Calculator

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

# --- PDF Report Functions ---
# This function is used to download the logo to a local file for ReportLab
def download_logo():
    """Download company logo for PDF report."""
    logo_file = None
    for url in [LOGO_URL, FALLBACK_LOGO_URL]:
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                logo_file = "company_logo.png"
                with open(logo_file, 'wb') as f:
                    f.write(response.content)
                break
        except Exception:
            # Catch all exceptions during download attempts
            pass
    return logo_file if logo_file and os.path.exists(logo_file) else None

# Helper function to draw header/footer on each page of the PDF
def _draw_header_footer(canvas, doc):
    canvas.saveState()
    
    # Draw Header (Company Name and Address)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(60*mm, A4[1] - 15*mm, COMPANY_NAME)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(60*mm, A4[1] - 20*mm, COMPANY_ADDRESS)
    
    # Draw Logo
    logo_file = "company_logo.png" # Assuming it was downloaded by generate_pdf_report
    if os.path.exists(logo_file):
        try:
            logo = Image(logo_file, width=40*mm, height=15*mm)
            logo.drawOn(canvas, 15*mm, A4[1] - 25*mm) # Position logo at top-left
        except Exception:
            pass # Ignore if image drawing fails
    
    # Draw Footer
    canvas.setFont('Helvetica', 8)
    footer_text = f"{PROGRAM} {PROGRAM_VERSION} | {COMPANY_NAME} © | Page {doc.page}"
    canvas.drawCentredString(A4[0]/2.0, 10*mm, footer_text)
    
    canvas.restoreState()

# Main PDF generation function
def generate_pdf_report(calculation_data, total_weight, cage_type, project_name, project_number, input_details):
    """Generate a professional PDF report with company branding and header on all pages."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=20*mm, bottomMargin=15*mm) # Reduced top margin
    
    styles = getSampleStyleSheet()
    
    # Custom styles (adopted from Wind Load Calculator)
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Title'],
        fontSize=14, # Reduced from 16
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=8 # Reduced from 12
    )
    
    subtitle_style = ParagraphStyle(
        name='SubtitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle( # Renamed from heading1_style for clarity
        name='HeadingStyle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10
    )
    
    heading2_style = ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=8
    )
    
    heading3_style = ParagraphStyle(
        name='Heading3',
        parent=styles['Heading3'],
        fontSize=11, # Reduced from 12
        spaceAfter=4 # Reduced from 6
    )
    
    normal_style = ParagraphStyle(
        name='NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        spaceAfter=8
    )
    
    bold_style = ParagraphStyle(name='BoldStyle', parent=styles['Normal'], fontSize=9, spaceAfter=4, fontName='Helvetica-Bold') # Added
    justified_style = ParagraphStyle(name='JustifiedStyle', parent=styles['Normal'], fontSize=9, spaceAfter=4, alignment=TA_JUSTIFY) # Added

    table_header_style = ParagraphStyle(
        name='TableHeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    table_cell_style = ParagraphStyle(
        name='TableCellStyle',
        parent=styles['Normal'],
        fontSize=8, # Reduced from 9
        leading=9, # Reduced from 11
        alignment=TA_LEFT
    )
    
    table_cell_center_style = ParagraphStyle(
        name='TableCellCenter',
        parent=styles['Normal'],
        fontSize=8, # Reduced from 9
        leading=9, # Reduced from 11
        alignment=TA_CENTER
    )
    
    elements = []

    # Attempt to download logo once before building the document
    download_logo() 
    
    # Title and project info
    elements.append(Paragraph(f"Concrete Reinforcement Cage Weight Report", title_style))
    elements.append(Paragraph(f"for {cage_type}", subtitle_style))
    
    # Project Info
    project_info_text = (
        f"<b>Project:</b> {project_name}<br/>"
        f"<b>Number:</b> {project_number}<br/>"
        f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}"
    )
    elements.append(Paragraph(project_info_text, normal_style))
    elements.append(Spacer(1, 8*mm))
    
    # --- Introduction Section ---
    elements.append(Paragraph("Introduction", heading_style))
    intro_text = (
        "This report provides a detailed calculation of the total weight for the specified concrete reinforcement cage. "
        "The calculations are based on standard nominal mass per meter values for Australian reinforcing steel, "
        "ensuring compliance with local standards. This document summarizes the input parameters provided and "
        "presents the calculated weights for each component, culminating in the total estimated cage weight."
    )
    elements.append(Paragraph(intro_text, justified_style))
    elements.append(Spacer(1, 4*mm))

    # --- Input Details Section ---
    elements.append(Paragraph("Input Details", heading_style))
    
    input_data_table_content = [
        [
            Paragraph("Component Type", table_header_style),
            Paragraph("Bar Size", table_header_style),
            Paragraph("Quantity", table_header_style),
            Paragraph("Length per Bar (m)", table_header_style)
        ]
    ]

    # Dynamically add input details to the table
    component_name_map = {
        "vertical_bars": "Vertical Bars",
        "horizontal_bars": "Horizontal Bars",
        "links": "Links/Ties"
    }

    for category, items in input_details.items():
        for i, item in enumerate(items):
            # Only add to report if quantity or length is greater than 0
            if item["qty"] > 0 or item["length"] > 0: 
                row_component = f"{component_name_map.get(category, category.replace('_', ' ').title())} (Type {i+1})"
                row_bar_size = item["size"]
                row_quantity = str(item["qty"]) # Ensure quantity is string for Paragraph
                row_length = f"{item['length']:.2f}"
                input_data_table_content.append([
                    Paragraph(row_component, table_cell_style),
                    Paragraph(row_bar_size, table_cell_center_style),
                    Paragraph(row_quantity, table_cell_center_style), 
                    Paragraph(row_length, table_cell_center_style)
                ])
    
    if len(input_data_table_content) > 1: # Check if there's actual data beyond headers
        input_table = Table(input_data_table_content, colWidths=[60*mm, 35*mm, 35*mm, 40*mm])
        input_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Left align for component type
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'), # Center align for Bar Size, Quantity, Length
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(input_table)
    else:
        elements.append(Paragraph("No input details were provided.", normal_style))

    elements.append(Spacer(1, 8*mm))
    
    # --- Weight Calculation Summary Section ---
    elements.append(Paragraph("Weight Calculation Summary", heading_style))
    
    if calculation_data:
        # Prepare data for the table
        table_data = [
            [
                Paragraph("Component", table_header_style),
                Paragraph("Bar Size", table_header_style),
                Paragraph("Quantity", table_header_style),
                Paragraph("Length per Bar (m)", table_header_style),
                Paragraph("Total Length (m)", table_header_style),
                Paragraph("Unit Weight (kg/m)", table_header_style),
                Paragraph("Total Weight (kg)", table_header_style)
            ]
        ]
        
        for row in calculation_data:
            table_data.append([
                Paragraph(str(row["Component"]), table_cell_style),
                Paragraph(str(row["Bar Size"]), table_cell_center_style),
                Paragraph(str(row["Quantity"]), table_cell_center_style),
                Paragraph(f"{row['Length per Bar (m)']:.2f}", table_cell_center_style),
                Paragraph(f"{row['Total Length (m)']:.2f}", table_cell_center_style),
                Paragraph(f"{row['Unit Weight (kg/m)']:.3f}", table_cell_center_style),
                Paragraph(f"{row['Total Weight (kg)']:.2f}", table_cell_center_style)
            ])
            
        summary_table = Table(table_data, colWidths=[40*mm, 20*mm, 20*mm, 25*mm, 25*mm, 25*mm, 25*mm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Left align for component
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'), # Center align for numeric columns
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 6*mm))
        elements.append(Paragraph(f"**Total Estimated {cage_type} Weight: {total_weight:.2f} kg**", heading2_style))
    else:
        elements.append(Paragraph("No bar details were entered for calculation.", normal_style))

    # Build the document with header and footer on all pages
    doc.build(elements, onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer)
    buffer.seek(0)
    return buffer

# --- Streamlit Application UI ---
st.set_page_config(page_title="Concrete Reinforcement Cage Weight Calculator", layout="centered")

st.title("🏗️ Concrete Reinforcement Cage Weight Calculator")
st.markdown("Calculate the total weight of your concrete reinforcement cages based on Australian standards.")

# --- Project Details Input (in sidebar) ---
st.sidebar.header("Report Details")
project_name = st.sidebar.text_input("Project Name:", "My Reinforcement Project")
project_number = st.sidebar.text_input("Project Number:", "PRJ-001")

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
            
            # --- PDF Report Download Button ---
            st.markdown("---")
            st.subheader("Generate Report")
            
            # Collect input details for the PDF report
            input_details = {
                "vertical_bars": vertical_bar_inputs,
                "horizontal_bars": horizontal_bar_inputs,
                "links": link_bar_inputs
            }

            pdf_buffer = generate_pdf_report(
                calculation_data, 
                total_cage_weight, 
                cage_type, 
                project_name, 
                project_number,
                input_details
            )
            
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name=f"Rebar_Cage_Report_{project_number}.pdf",
                mime="application/pdf"
            )
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
