import streamlit as st
import pandas as pd
import json
import os
from pdf2image import convert_from_bytes
from io import BytesIO
import base64
from openai import OpenAI

# Retrieve API key securely
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set it as an environment variable.")
client = OpenAI(api_key=api_key)

client = OpenAI()

os.environ['OPENAI_API_KEY']="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"

def process_images_extract_json(base64_images):
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": """Review the image carefully and understand the type of data it contains (e.g., text, tables, numerical data).
                        include all the details from the image.
                        return the data which can easily be converted to dataframe.
                        return only json, josn should follow this format:
                        {
                            "Entity1": [
                                {
                                "Field1": "Value1",
                                "Field2": "Value2"
                                },
                                {
                                "Field1": "Value3",
                                "Field2": "Value4"
                                }
                            ],
                            "Entity2": [
                                {
                                "Attribute1": "Detail1",
                                "Attribute2": "Detail2"
                                },
                                {
                                "Attribute1": "Detail3",
                                "Attribute2": "Detail4"
                                }
                            ],
                            "Entity3": [
                                {
                                "Property1": "Info1",
                                "Property2": "Info2"
                                },
                                {
                                "Property1": "Info3",
                                "Property2": "Info4"
                                }
                            ]
                            }
                            """,
            },
            *base64_images,
        ],
        }
    ],
    )

    resp = response.choices[0].message.content
    json_data = resp.split("```json")[1].split("```")[0]
    data = json.loads(json_data)

    return data

def process_images_to_base64json(images):
    

    base64_images = []
    for img in images:
        
        image_buffer = BytesIO()
        img.save(image_buffer, format='JPEG')
        base64_image = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
        base64_images.append({
                "type": "image_url",
                "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
                },
            })
        #st.image(img, caption='Uploaded PDF', use_column_width=True)
    
    return base64_images



st.title("GERMANY Scope: Intelligent PDF Data Extraction")
st.subheader("Convert PDF Documents into Multiple Excel Files with Ease")

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file is not None:
    st.write("Processing PDF...")
    poppler_path = r"E:\image_conversion\testing\web_testing\poppler-24.08.0\Library\bin" 
    
    # Convert PDF to images
    images = convert_from_bytes(uploaded_file.read(), poppler_path = poppler_path)
    
    # Process images to JSON
    base64_images = process_images_to_base64json(images)
    
    json_data = process_images_extract_json(base64_images)
    
    st.write("**Extraction Complete!**")
    
    # Provide download links for each Excel file
    for key, value in json_data.items():
        try:
            try:
                st.write(f"**{key}**")
                st.dataframe(pd.DataFrame(json_data[key]))
            except:
                st.dataframe(pd.DataFrame(json_data[key], index=[0]))
        except:
            print(f"Error in converting {key} to excel")
            pass
