from dotenv import load_dotenv
load_dotenv()  # Load all the environment variables

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Configure the Google Gemini API with the new model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini 1.5 Flash API and get response
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to handle image upload
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize Streamlit app with theme
st.set_page_config(page_title="Gemini Health App", page_icon=":apple:", layout="wide", initial_sidebar_state="expanded")

# Add a custom CSS style
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# Add a sidebar for user input
with st.sidebar:
    st.header("Gemini Health App")
    input = st.text_input("Input Prompt:", key="input")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.title("Gemini Health App")
    st.write("Analyze food images and calculate total calories.")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    with col2:
        st.image(image, caption="Uploaded Image.", use_container_width=True)

submit = st.button("Tell me the total calories")

input_prompt = """
You are an expert nutritionist. Analyze the food items in the image and calculate the total calories. Provide the details of each food item with calorie intake in the format below:

1. Item 1 - no of calories
2. Item 2 - no of calories
----
----
"""

# Function to determine if the food should be consumed
def should_consume_food(calories, threshold=600):
    if calories <= threshold:
        return "The total calorie count is within a healthy limit. It is okay to consume the food."
    else:
        return "The total calorie count exceeds the healthy limit. Consider portion control or choose alternatives."

# If submit button is clicked
if submit:
    if uploaded_file is not None:
        with st.spinner("Analyzing the image..."):
            image_data = input_image_setup(uploaded_file)
            response = get_gemini_response(input_prompt, image_data, input)
            st.subheader("The Response is")
            st.write(response)

            try:
                # Extract calorie numbers from the response
                calorie_lines = [line for line in response.split('\n') if '-' in line]
                total_calories = 0
                for line in calorie_lines:
                    try:
                        total_calories += int(line.split('-')[1].strip().split()[0])
                    except ValueError:
                        continue  # Skip lines that don't contain valid integers

                st.subheader("Total Calories")
                st.write(total_calories)

                # Suggest whether to consume the food
                suggestion = should_consume_food(total_calories)
                st.subheader("Suggestion")
                st.write(suggestion)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.error("Please upload an image.")
