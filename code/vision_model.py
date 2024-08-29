import torch
from transformers import AutoProcessor, PaliGemmaForConditionalGeneration, BitsAndBytesConfig
from PIL import Image

class VisionModel:
    def __init__(self, model_id="brucewayne0459/paligemma_derm"):
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = PaliGemmaForConditionalGeneration.from_pretrained(
            model_id, 
            device_map="auto",quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16))

    def analyze_image(self, image):
        input_text = "Is there any human skin disease in the image?"
        inputs = self.processor(text=input_text, images=image, return_tensors="pt", padding="longest").to("cuda" if torch.cuda.is_available() else "cpu")
        with torch.no_grad():
            vision_outputs = self.model.generate(**inputs, max_new_tokens=50, do_sample=False)  # Greedy decoding
        decoded_output = self.processor.decode(vision_outputs[0], skip_special_tokens=True).replace(input_text, "").strip()
        return decoded_output

    def identify_disease(self, image):
        disease_identification_text = "Identify the skin disease."
        inputs = self.processor(text=disease_identification_text, images=image, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        with torch.no_grad():
            disease_output = self.model.generate(**inputs, max_new_tokens=50, do_sample=False)  # Greedy decoding
        decoded_output = self.processor.decode(disease_output[0], skip_special_tokens=True).replace(disease_identification_text, "").strip()
        return decoded_output

    def locate_disease(self, image):
        disease_location = "Where is the skin disease located on the human body?"
        inputs = self.processor(text=disease_location, images=image, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        with torch.no_grad():
            disease_location_output = self.model.generate(**inputs, max_new_tokens=50, do_sample=False)  # Greedy decoding
        skin_disease_location = self.processor.decode(disease_location_output[0], skip_special_tokens=True).replace(disease_location, "").strip()
        return skin_disease_location

    def process_image(self, image):
        analysis_result = self.analyze_image(image)
        if "yes" in analysis_result.lower():
            disease = self.identify_disease(image)
            location = self.locate_disease(image)
            return f"The identified skin disease from the image is {disease}. The location of the {disease} is on {location}."
        else:
            return "No skin disease detected in the image."
