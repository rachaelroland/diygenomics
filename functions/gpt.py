import importlib.resources as resources
import json
import os
import openai
import time

from retry import retry
from retry.api import retry_call

log_file = os.path.join('logs', 'chat_completion.log')

if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write('')
        
def load_pricing():
    with resources.open_text('logs', 'pricing.json') as f:
        return json.load(f)

PRICING = load_pricing()

def parse_response(completion):
    output_dict = {}
 
    content = completion.choices[0].message['content']
    start_index = content.find("{")
    output_str = content[start_index:]

    try:
        if "\'" in output_str:
            output_str = json.dumps(eval(output_str))
        else:
            output_str = output_str.replace("'", "\"")
        output_dict = json.loads(output_str)
    except json.JSONDecodeError as je:
        output_dict = {'json_error': f'Error: {je} {completion}'}
    except Exception as e:
        output_dict = {'general_error': f'Error: {e} {completion}'}

    return output_dict

def chat_create(system_prompt, user_text, model, output_json=True, temperature=0):
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_text}
      ]

    completion = retry_call(
        openai.ChatCompletion.create,
        fkwargs={
            "model": model,
            "messages": messages,
            "temperature": temperature,
        },
        backoff=2,
        max_delay=120,
        tries=3
    )

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cost = get_rate_per_token(model, completion["usage"]["prompt_tokens"], completion["usage"]['completion_tokens'])
    cost_float = float(cost)
    cost_str = f"{cost_float:.10f}" 
    cost_formatted = cost_str.rstrip('0').rstrip('.')
    
    with open(log_file, 'r') as f:
        total_cost = 0
        for line in f:
            entry = json.loads(line)
            total_cost += float(entry['cost'])
            
    total_cost += cost_float
    total_cost_str = f"{total_cost:.10f}"
    total_cost_formatted = total_cost_str.rstrip('0').rstrip('.')
    with open(log_file, 'a') as f:
        log_entry = {
            'timestamp': timestamp,
            'model': model,
            'cost': cost_formatted,
            'total_cost': total_cost_formatted,
            'prompt': user_text,
            'response': completion.choices[0].message['content'],
            'temperature': temperature
        }
        f.write(json.dumps(log_entry) + '\n')
    
    return parse_response(completion) if output_json else completion.choices[0].message['content']

def get_rate_per_token(model, prompt_tokens, completion_tokens):
    if model == "gpt-3.5-turbo":
        usage = PRICING[model]["usage"]
        tokens = prompt_tokens + completion_tokens
        cost = (usage / 1000) * tokens
        return cost
    elif model == "gpt-4":
        prompt = PRICING[model]["prompt"]
        cost_prompt = (prompt / 1000) * prompt_tokens
        completion = PRICING[model]["completion"]
        cost_completion = (completion / 1000) * completion_tokens
        cost = cost_prompt + cost_completion
        return cost 
