def receive_llm_config_part(config):
    return config["llm"]

def receive_llm_ollama_config_path(config):
    return receive_llm_config_part(config)["ollama"]

def receive_llm_ollama_image_describe_prompt(llm_name: str, config):
    return receive_llm_ollama_config_path(config)[llm_name]["image_describe_prompt"]
