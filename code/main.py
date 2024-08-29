from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pyngrok import ngrok
from PIL import Image
import io
import logging
from vision_model import VisionModel
from text_model import TextModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize the models
vision_model = VisionModel()
text_model = TextModel()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse, name="chat")
async def chat_interface(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/analyze_skin")
async def analyze_skin(
    file: UploadFile = File(None),  # The image file is optional
    user_question: str = Form(None)  # The user question is also optional
):
    try:
        if file and user_question:
            # Scenario 1: User uploads an image and provides a question
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert("RGB")
            vision_output = vision_model.process_image(image)
            result = text_model.process_query(vision_output, user_question)
        elif file:
            # Scenario 2: User uploads an image but does not provide a question
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert("RGB")
            vision_output = vision_model.process_image(image)
            result = f"The vision model has analyzed the image and the result is: {vision_output}."
        elif user_question:
            # Scenario 3: User only asks a text question without uploading an image
            result = text_model.process_query("", user_question)
        else:
            # Scenario 4: Neither image nor question provided
            result = "Please upload an image or ask a question for analysis."
        
        logger.info(f"Analysis result: {result}")
        return JSONResponse(content={"result": result})
   
    except Exception as e:
        logger.error(f"Error in analyze_skin: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask_question")
async def ask_question(user_question: str = Form(...)):
    try:
        logger.info(f"Received question: {user_question}")
        result = text_model.process_query("", user_question)
        logger.info(f"Text model output: {result}")
        return JSONResponse(content={"result": result})
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Set up ngrok tunnel
    ngrok_tunnel = ngrok.connect(8000)
    logger.info(f'Public URL: {ngrok_tunnel.public_url}')
   
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)