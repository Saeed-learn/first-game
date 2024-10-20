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
            d.add(elm.Line().down())
    
    elif circuit_type == 'Hybrid':
        # Hybrid circuits will include both series and parallel
        d.add(elm.Line().down())
        d.add(elm.Resistor().label(f'{values[0]}Ω'))
        d.add(elm.Line().right())
        d.add(elm.Capacitor().label(f'{values[1]}F'))
        d.add(elm.Line().down())
        d.add(elm.Inductor().label(f'{values[2]}H'))
        d.add(elm.Line().left())
        d.add(elm.Line().up())

    # Get SVG data from the drawing
    return d.get_imagedata('svg')

# Streamlit App Layout
st.title('Electrical Engineering Mind Game')
st.subheader('Guess the Equivalent Value of the Circuit!')

# Circuit component options
components = ['Resistor', 'Capacitor', 'Inductor']
component = st.selectbox('Choose the component', components)

# Circuit type options
circuit_types = ['Series', 'Parallel', 'Hybrid']
circuit_type = st.selectbox('Choose the circuit type', circuit_types)

# Button to generate a new circuit
if st.button('Generate New Circuit'):
    # Generate random values for components
    comp_values = [random.uniform(1, 100) for _ in range(3)]  # Random values between 1 and 100
    st.session_state.comp_values = comp_values  # Store in session state for editing
    st.session_state.component = component
    st.session_state.circuit_type = circuit_type

# If a circuit has been generated, allow editing the values
if 'comp_values' in st.session_state:
    st.markdown('### Edit the component values:')
    comp1 = st.number_input(f'Enter value for {st.session_state.component} 1', 
                             min_value=0.0, value=st.session_state.comp_values[0])
    comp2 = st.number_input(f'Enter value for {st.session_state.component} 2', 
                             min_value=0.0, value=st.session_state.comp_values[1])
    comp3 = st.number_input(f'Enter value for {st.session_state.component} 3', 
                             min_value=0.0, value=st.session_state.comp_values[2])

    # Calculate total value based on circuit type
    def calculate_total_value(circuit_type, component, values):
        if circuit_type == 'Series':
            return sum(values)
        elif circuit_type == 'Parallel':
            return 1 / sum(1 / v for v in values if v != 0)
        elif circuit_type == 'Hybrid':
            series_value = sum(values[:2])  # Assuming first two values are in series
            parallel_value = 1 / sum(1 / v for v in values[1:] if v != 0)  # Last two in parallel
            return series_value + parallel_value

    # Display the total value as a challenge to the user
    total_value = calculate_total_value(st.session_state.circuit_type, 
                                        st.session_state.component, 
                                        [comp1, comp2, comp3])
    st.markdown(f'### Total {st.session_state.component} Value: ?')

    # Draw the circuit diagram and display
    circuit_svg = draw_circuit_svg(st.session_state.component, 
                                    st.session_state.circuit_type, 
                                    [comp1, comp2, comp3])

    # Render the SVG image in the app
    svg_data = circuit_svg.decode("utf-8")
    st.write(f'<div>{svg_data}</div>', unsafe_allow_html=True)

    # Allow user to guess the total value
    guess = st.number_input('Guess the total value:', min_value=0.0)

    # Button to submit guess
    if st.button('Submit Guess'):
        if abs(guess - total_value) < 0.1:
            st.success(f'Correct! The total {st.session_state.component} value is approximately {total_value:.2f}.')
        else:
            st.error(f'Incorrect. The total {st.session_state.component} value is approximately {total_value:.2f}. Try again!')
