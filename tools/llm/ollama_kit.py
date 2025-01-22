import ollama

from config import llm_config


def ollama_image_describe(jpg_image_bytes: bytes, config) -> str:
    model_name = "llama3.2-vision"
    image_describe_prompt = llm_config.receive_llm_ollama_image_describe_prompt(model_name, config)
    response = ollama.chat(
        model=model_name,
        messages=[{
            'role': 'user',
            'content': image_describe_prompt,
            'images': [jpg_image_bytes],
        }]
    )
    return response.message.content
