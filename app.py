import streamlit as st
import random
import schemdraw
import schemdraw.elements as elm
from PIL import Image

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    body {
        background-color: #f0f4f7;
        font-family: 'Arial', sans-serif;
    }
    .title {
        color: #333;
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton button {
        background-color: #0073e6;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 20px;
        margin: 10px;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #005bb5;
    }
    .result {
        font-size: 24px;
        font-weight: bold;
        color: #0073e6;
        margin: 20px 0;
    }
    .instruction {
        font-size: 18px;
        color: #555;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Title for the game
st.markdown('<h1 class="title">Electrical Circuit Puzzle with Visuals</h1>', unsafe_allow_html=True)

# Function to draw the circuit diagram
def draw_circuit(component, config, values):
    with schemdraw.Drawing() as d:
        if config == "Series":
            for i in range(3):
                if component == "Resistor":
                    d.add(elm.Resistor().label(f'{values[i]}Ω'))
                elif component == "Capacitor":
                    d.add(elm.Capacitor().label(f'{values[i]}F'))
                else:
                    d.add(elm.Inductor().label(f'{values[i]}H'))
        else:  # Parallel circuit
            d.add(elm.Line())
            d.push()
            for i in range(3):
                d.add(elm.Line().down())
                if component == "Resistor":
                    d.add(elm.Resistor().label(f'{values[i]}Ω').down())
                elif component == "Capacitor":
                    d.add(elm.Capacitor().label(f'{values[i]}F').down())
                else:
                    d.add(elm.Inductor().label(f'{values[i]}H').down())
                d.add(elm.Line().left().tox(0))
                d.pop()
            d.add(elm.Line().right())

        d.save('circuit.png')

# Variables for gameplay
if 'target_value' not in st.session_state:
    st.session_state.target_value = random.uniform(10, 500)  # Random target between 10 and 500 (ohms, farads, or henrys)
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'high_scores' not in st.session_state:
    st.session_state.high_scores = []

# Component selection (Resistor, Capacitor, Inductor)
component = st.radio("Select Component Type:", ['Resistor', 'Capacitor', 'Inductor'])

# Circuit configuration based on the selected component
if component == 'Resistor':
    circuit_type = st.radio("Choose Circuit Type:", ['Series', 'Parallel'])
    st.markdown(f'<p class="instruction">Your goal is to match the target resistance of {st.session_state.target_value:.2f}Ω.</p>', unsafe_allow_html=True)
elif component == 'Capacitor':
    circuit_type = st.radio("Choose Circuit Type:", ['Series', 'Parallel'])
    st.markdown(f'<p class="instruction">Your goal is to match the target capacitance of {st.session_state.target_value:.2f}F.</p>', unsafe_allow_html=True)
else:  # Inductor
    circuit_type = st.radio("Choose Circuit Type:", ['Series', 'Parallel'])
    st.markdown(f'<p class="instruction">Your goal is to match the target inductance of {st.session_state.target_value:.2f}H.</p>', unsafe_allow_html=True)

# Difficulty selection for range of values
difficulty = st.radio("Select Difficulty Level:", ['Easy', 'Medium', 'Hard'])

if difficulty == 'Easy':
    component_range = (1, 50)  # Range for all components (ohms, farads, henrys)
elif difficulty == 'Medium':
    component_range = (1, 100)
else:
    component_range = (1, 200)

# Sliders for component values
comp1 = st.slider(f'{component} 1', min_value=component_range[0], max_value=component_range[1], step=1, value=50)
comp2 = st.slider(f'{component} 2', min_value=component_range[0], max_value=component_range[1], step=1, value=50)
comp3 = st.slider(f'{component} 3', min_value=component_range[0], max_value=component_range[1], step=1, value=50)

# Calculate the total value based on component and circuit type
if component == 'Resistor':
    if circuit_type == 'Series':
        total_value = comp1 + comp2 + comp3
    else:  # Parallel for Resistors
        total_value = 1 / ((1/comp1) + (1/comp2) + (1/comp3))

elif component == 'Capacitor':
    if circuit_type == 'Series':  # Capacitors in series add like resistors in parallel
        total_value = 1 / ((1/comp1) + (1/comp2) + (1/comp3))
    else:  # Capacitors in parallel add directly
        total_value = comp1 + comp2 + comp3

else:  # Inductor
    if circuit_type == 'Series':  # Inductors in series add directly like resistors
        total_value = comp1 + comp2 + comp3
    else:  # Inductors in parallel add like resistors in parallel
        total_value = 1 / ((1/comp1) + (1/comp2) + (1/comp3))

# Display the total value
unit = 'Ω' if component == 'Resistor' else ('F' if component == 'Capacitor' else 'H')
st.markdown(f'<p class="result">Total {component} Value: {total_value:.2f}{unit}</p>', unsafe_allow_html=True)

# Draw the circuit diagram based on user inputs
draw_circuit(component, circuit_type, [comp1, comp2, comp3])

# Load and display the circuit image
image = Image.open('circuit.png')
st.image(image, caption='Circuit Diagram')

# Button for submitting the guess
if st.button('Submit Guess'):
    st.session_state.attempts += 1

    # Score calculation: closer guesses get more points
    difference = abs(total_value - st.session_state.target_value)
    if difference == 0:
        st.session_state.score += 100  # Perfect match!
        st.markdown(f'<p class="result">🎉 Perfect! You matched the target in {st.session_state.attempts} attempts with a total score of {st.session_state.score}!</p>', unsafe_allow_html=True)
        if st.button('Play Again'):
            st.session_state.target_value = random.uniform(10, 500)
            st.session_state.attempts = 0
            st.session_state.score = 0
    else:
        # Provide feedback and add to score
        st.session_state.score += max(1, 100 - int(difference))  # Points decrease as difference increases
        if total_value < st.session_state.target_value:
            st.markdown(f'<p class="result">📉 Too low! Increase the {component} value.</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="result">📈 Too high! Decrease the {component} value.</p>', unsafe_allow_html=True)

    # Show progress bar
    st.progress(min(100, int(100 - difference)))

# Show leaderboard
st.markdown("## Leaderboard")
if st.session_state.attempts > 0:
    st.session_state.high_scores.append(st.session_state.score)
    st.session_state.high_scores = sorted(st.session_state.high_scores, reverse=True)[:5]  # Keep top 5 scores
    st.write(st.session_state.high_scores)

# Provide hint after 3 attempts
if st.session_state.attempts >= 3:
    st.markdown(f"Hint: Try adjusting the {component} values closer to {st.session_state.target_value:.2f}")

# Theme selection: Light or Dark mode
theme_choice = st.selectbox("Choose Theme:", ['Light', 'Dark'])
if theme_choice == 'Dark':
    st.markdown('<style>body {background-color: #2E2E2E; color: white;}</style>', unsafe_allow_html=True)
else:
    st.markdown('<style>body {background-color: white; color: black;}</style>', unsafe_allow_html=True)
