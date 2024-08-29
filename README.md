# Skin Disease and Skincare Chatbot

This project is a chatbot specialized in diagnosing skin diseases and addressing skincare issues. The chatbot is powered by a fine-tuned version of OpenBioLLM, an expert language model in the medical domain. The model has been fine-tuned specifically for skin problems and skincare by training it on curated data from the internet. Additionally, the chatbot features a vision component that can identify diseases in images using a fine-tuned version of the Peli-Gemma vision model, trained on 22,000 skin disease images. The chatbot also maintains chat history to keep conversations in context.

## Model Links

- [Peli-Gemma Vision Model (fine-tuned for dermatology)](https://huggingface.co/brucewayne0459/paligemma_derm)
- [OpenBioLLM-Derm (fine-tuned for dermatology)](https://huggingface.co/brucewayne0459/OpenBioLLm-Derm)

## Running the Chatbot Locally

To run the chatbot locally, remove the `ngrok` command line at the end of the `main.py` file and execute it.

## Running the Chatbot on Google Colab (Free Version)

If you want to run the chatbot on Google Colab, follow these steps:

### Step 1: Get an API Key from Ngrok

Since Colab does not have an inbuilt browser, you will need an API key from Ngrok.

### Step 2: Upload `static.zip` to Colab

Upload the `static.zip` file to your Colab environment and run the following commands:

```bash
!unzip static.zip
!pip install bitsandbytes
!pip install fastapi
!pip install uvicorn
!pip install langchain
!pip install langchain_community
!pip install python-multipart
!pip install pyngrok
!ngrok config add-authtoken Your_ngrok_key
!python main.py
