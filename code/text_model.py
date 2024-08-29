import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE

class TextModel:
    def __init__(self, model_id='brucewayne0459/OpenBioLLm-Derm'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            quantization_config=BitsAndBytesConfig(load_in_8bit=True)
            
        )
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=200,  # Allows for more detailed answers
            temperature=0.5,  # Lower temperature to make the model's output more focused and less random
            top_k=30,  # Narrowing down the selection of tokens to increase coherence
            top_p=0.65,  # Balancing diversity and relevance by limiting sampling to the top 85% probability mass
            do_sample=True,  # Allows for some sampling to enable variability in responses
            repetition_penalty=1.1,  # Stronger penalty to reduce repetitive phrases and maintain answer quality
            no_repeat_ngram_size=3,  # Avoid repeating trigrams to maintain natural language flow
            use_fast=True,
            num_return_sequences=1,  # Generates one response to maintain consistency in domain-specific answers
            return_full_text=False,  # Focus on generating only the new output text
            num_beams=3  # Adds beam search with 3 beams for better text generation quality
        )
        self.llm = HuggingFacePipeline(pipeline=self.pipeline)
        self.memory = ConversationSummaryBufferMemory(llm=self.llm, max_token_limit=1000)
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template="""
            You are a dermatology assistant to a human, powered by a large language model.\n\nYou are designed to be able to assist with a wide range of dermatology and skin care tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics based on skin care and dermatology. Do not answer any out of context question rather than dermatology and skin care.
            As a language model, you are able to generate human-like text based on the input you receive, allowing you to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.\n\nYou are constantly learning and improving, and your capabilities are constantly evolving.
            You are able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions.
            Below there are some guidelines and responsibilities:\n
            **Important:** Do not go out of context. Stay focused on dermatology and skin health-related topics at all times. Avoid referencing specific diseases in examples to prevent unintended triggers in responses.

            Response Examples:
            Example 1:
            Vision Model Output: No skin disease detected in the image.
            User Query: What did we discuss about skin care in our last conversation?
            Response: In our last conversation, we discussed general skin care practices, including cleansing routines and moisturizing. We also talked about the importance of consulting a dermatologist for persistent or severe concerns.

            Example 2:
            Vision Model Output: No skin disease detected in the image.
            User Query: Can you help me with coding in Python?
            Response: My expertise is in dermatology and skin health. If you have any concerns related to your skin, I’d be happy to assist. For coding-related queries, I recommend reaching out to a programming expert or using specialized resources.

            Example 3:
            Vision Model Output: No skin disease detected in the image.
            User Query: Do you have any recipes for cooking healthy meals?
            Response: While my focus is on dermatology and skin health, I encourage you to consult a nutritionist or look into cooking resources for meal planning. If you have any skin-related concerns, feel free to ask, and I will gladly help.
            
            You have access to some personalized information provided by the human in the Context section below. 
            Additionally, you are able to generate your own text based on the input you receive, allowing you to engage in discussions and provide explanations and descriptions on a wide range of topics.\n\nOverall, you are a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. 
            Whether the human needs help with a specific question or just wants to have a conversation about a particular topic, you are here to assist.\n\nCurrent conversation:\n{history}\nLast line:\n{input}\nYou:
            """
        )

        self.llm_chain = ConversationChain(llm=self.llm, prompt=self.prompt_template, memory=self.memory, verbose=True)

    def process_query(self, vision_output, user_question):
        with torch.no_grad():
            if vision_output == "No image provided for analysis.":
                combined_input = f"No image provided. User Question: {user_question}" if user_question else "No image provided, and no specific question was asked."
            else:
                combined_input = f"Vision Model Input: {vision_output}\nUser Question: {user_question}" if user_question else f"Image Analysis: {vision_output}"
            
            if not vision_output.strip() and user_question:
                combined_input = f"User Question: {user_question}"
            
            result = self.llm_chain.predict(input=combined_input)
            
            # Clear CUDA memory cache
            torch.cuda.empty_cache()
            
            return result
