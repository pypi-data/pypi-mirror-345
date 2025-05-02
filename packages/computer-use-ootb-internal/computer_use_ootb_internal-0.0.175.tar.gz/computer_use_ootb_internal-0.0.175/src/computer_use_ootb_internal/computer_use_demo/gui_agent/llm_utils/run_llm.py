import base64
import logging


def run_llm(messages, system, llm="gpt-4o-mini", max_tokens=512, temperature=0, stop=None):
    log_prompt(messages)
    
    # if not isinstance(messages, list):
    #     raise ValueError(f"Invalid messages type: {type(messages)}")
    
    # turn string prompt into list
    if isinstance(messages, str):
        messages = [messages]
    elif isinstance(messages, list):
        pass
    else:
        raise ValueError(f"Invalid prompt type: {type(messages)}")
    
    if llm.startswith("gpt"): # gpt series
        from .oai import run_oai_interleaved
        response, token_usage = run_oai_interleaved(
            messages=messages, 
            system=system, 
            llm=llm, 
            max_tokens=max_tokens, 
            temperature=temperature
        )
    elif llm.startswith("gemini"): # gemini series
        from .gemini import run_gemini_interleaved

        response, token_usage = run_gemini_interleaved(
            messages=messages, 
            system=system, 
            llm=llm, 
            max_tokens=max_tokens, 
            temperature=temperature
        )
    else:
        raise ValueError(f"Invalid llm: {llm}")
    logging.info(
        f"========Output for {llm}=======\n{response}\n============================")
    return response

def log_prompt(prompt):
    prompt_display = [prompt] if isinstance(prompt, str) else prompt
    prompt_display = "\n\n".join(prompt_display)
    logging.info(
        f"========Prompt=======\n{prompt_display}\n============================")
    