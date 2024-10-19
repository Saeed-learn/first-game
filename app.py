import streamlit as st
from io import BytesIO
import schemdraw
import schemdraw.elements as elm
import random

# Function to draw the circuit and return SVG data
def draw_circuit_svg(component, circuit_type, values):
    d = schemdraw.Drawing()
    
    if circuit_type == 'Series':
        for value in values:
            if component == 'Resistor':
                d.add(elm.Resistor().label(f'{value}Ω'))
            elif component == 'Capacitor':
                d.add(elm.Capacitor().label(f'{value}F'))
            elif component == 'Inductor':
                d.add(elm.Inductor().label(f'{value}H'))
            d.add(elm.Line().right())
    elif circuit_type == 'Parallel':
        d.add(elm.Line().down())
        for value in values:
            d.push()
            if component == 'Resistor':
                d.add(elm.Resistor().label(f'{value}Ω'))
            elif component == 'Capacitor':
                d.add(elm.Capacitor().label(f'{value}F'))
            elif component == 'Inductor':
                d.add(elm.Inductor().label(f'{value}H'))
            d.pop()

    # Get SVG data from the drawing
    return d.get_imagedata('svg')

# Streamlit App Layout
st.title('Electrical Engineering Mind Game')
st.subheader('Guess the Equivalent Value of the Circuit!')

# Circuit component options
components = ['Resistor', 'Capacitor', 'Inductor']
component = st.selectbox('Choose the component', components)

# Circuit type options
circuit_types = ['Series', 'Parallel']
circuit_type = st.selectbox('Choose the circuit type', circuit_types)

# User inputs for the individual component values
comp1 = st.number_input(f'Enter value for {component} 1', min_value=0.0, value=10.0)
comp2 = st.number_input(f'Enter value for {component} 2', min_value=0.0, value=10.0)
comp3 = st.number_input(f'Enter value for {component} 3', min_value=0.0, value=10.0)

# Calculate total value based on circuit type
def calculate_total_value(circuit_type, component, values):
    if circuit_type == 'Series':
        return sum(values)
    elif circuit_type == 'Parallel':
        return 1 / sum(1 / v for v in values if v != 0)

# Display the total value as a challenge to the user
total_value = calculate_total_value(circuit_type, component, [comp1, comp2, comp3])
st.markdown(f'### Total {component} Value: ?')

# Draw the circuit diagram and display
circuit_svg = draw_circuit_svg(component, circuit_type, [comp1, comp2, comp3])

# Render the SVG image in the app
svg_data = circuit_svg.decode("utf-8")
st.write(f'<div>{svg_data}</div>', unsafe_allow_html=True)

# Allow user to guess the total value
guess = st.number_input('Guess the total value:', min_value=0.0)

# Button to submit guess
if st.button('Submit Guess'):
    if abs(guess - total_value) < 0.1:
        st.success(f'Correct! The total {component} value is approximately {total_value:.2f}.')
    else:
        st.error(f'Incorrect. The total {component} value is approximately {total_value:.2f}. Try again!')

# Variables for gameplay
if 'target_value' not in st.session_state:
    st.session_state.target_value = random.uniform(1, 100)
