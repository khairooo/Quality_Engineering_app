import streamlit as st
import pandas as pd
import requests

# Debug: Print a message to confirm the app is running
print("Streamlit app is running...")

# Function to load the Excel file
def load_excel(file):
    try:
        df = pd.read_excel(file)
        print("Excel file loaded successfully.")  # Debug
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        print(f"Error loading Excel file: {e}")  # Debug
        return None

# Function to interact with Groq API
def ask_groq(question, data):
    # Convert the DataFrame to a string for context
    data_str = data.to_string()
    print("Data converted to string for Groq.")  # Debug
    
    # Create a prompt for Groq
    prompt = f"""
    You are a data analyst. Below is the data from an Excel file:
    {data_str}

    Answer the following question based on the data:
    {question}
    """
    print(f"Prompt sent to Groq: {prompt}")  # Debug
    
    # Groq API settings
    GROQ_API_KEY = st.secrets["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"]
    GROQ_API_URL = "https://huggingface.co/meta-llama/Llama-Guard-3-8B"  # Example endpoint, check Groq docs for the correct one
    
    # Prepare the request payload
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "mixtral-8x7b-32768",  # Replace with the model you want to use
        "messages": [
            {"role": "system", "content": "You are a data analyst. Analyze the data and provide accurate answers."},
            {"role": "user", "content": prompt},
        ],
    }
    
    # Query Groq API
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print("Groq response received.")  # Debug
            return result["choices"][0]["message"]["content"]
        else:
            st.error(f"Error querying Groq: {response.status_code} - {response.text}")
            print(f"Error querying Groq: {response.status_code} - {response.text}")  # Debug
            return "Sorry, I couldn't process your request."
    except Exception as e:
        st.error(f"Error querying Groq: {e}")
        print(f"Error querying Groq: {e}")  # Debug
        return "Sorry, I couldn't process your request."

# Streamlit app
def main():
    st.title("Excel AI Assistant with Groq")
    st.write("Upload an Excel file and ask questions about the data.")

    # File upload
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])
    if uploaded_file is not None:
        df = load_excel(uploaded_file)
        if df is not None:
            st.write("### Data Preview")
            st.dataframe(df.head())

            # Question input
            question = st.text_input("Ask a question about the data:")
            if question:
                with st.spinner("Thinking..."):
                    answer = ask_groq(question, df)
                    st.write("### Answer:")
                    st.write(answer)

if __name__ == "__main__":
    main()
