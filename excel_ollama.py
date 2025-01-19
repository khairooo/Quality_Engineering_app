import streamlit as st
import pandas as pd
import ollama

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

# Function to interact with Ollama
def ask_ollama(question, data):
    # Convert the DataFrame to a string for context
    data_str = data.to_string()
    print("Data converted to string for Ollama.")  # Debug
    
    # Create a prompt for Ollama
    prompt = f"""
    You are a data analyst. Below is the data from an Excel file:
    {data_str}

    Answer the following question based on the data:
    {question}
    """
    print(f"Prompt sent to Ollama: {prompt}")  # Debug
    
    # Query Ollama
    try:
        response = ollama.generate(model='mistral:latest', prompt=prompt)
        print("Ollama response received.")  # Debug
        return response['response']
    except Exception as e:
        st.error(f"Error querying Ollama: {e}")
        print(f"Error querying Ollama: {e}")  # Debug
        return "Sorry, I couldn't process your request."

# Streamlit app
def main():
    st.title("Excel AI Assistant with Ollama")
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
                    answer = ask_ollama(question, df)
                    st.write("### Answer:")
                    st.write(answer)

if __name__ == "__main__":
    main()