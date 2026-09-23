from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from prometheus_fastapi_instrumentator import Instrumentator
model_name = "HuggingFaceTB/SmolLM-135M-Instruct"
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Server start වෙද්දී Model එක load වීම
    print("Loading AI Model into memory...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    )
    ml_models["tokenizer"] = tokenizer
    ml_models["model"] = model
    print("Model loaded successfully!")
    yield
    # Server shutdown වෙද්දී clean up වීම
    ml_models.clear()

app = FastAPI(title="FastAPI AI Service", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 50
    temperature: float = 0.7

@app.get("/")
def root():
    return {
        "status": "online",
        "model": model_name,
        "message": "AI Inference API is running on KVM 2 VPS"
    }
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/generate")
def generate_text(req: PromptRequest):
    tokenizer = ml_models["tokenizer"]
    model = ml_models["model"]

    # Chat format එකට prompt එක සකස් කිරීම
    messages = [{"role": "user", "content": req.prompt}]
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False)

    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    # Output text එක decode කිරීම (Prompt එක අයින් කර model response එක පමණක් ගැනීම)
    input_len = inputs["input_ids"].shape[1]
    generated_tokens = outputs[0][input_len:]
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    return {
        "prompt": req.prompt,
        "response": response_text.strip()
    }