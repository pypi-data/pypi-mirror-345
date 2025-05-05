import yaml
import random
from typing import Tuple, List, Dict, Any

import yaml
import random
from typing import Tuple, List, Dict

def read_experiment_config(yaml_path: str) -> Tuple[List[Dict], List[str]]:
    """
    Loads an experiment configuration from a YAML file and processes it according to specified rules.
    
    Args:
        yaml_path (str): Path to the YAML configuration file.
        
    Returns:
        Tuple[List[Dict], List[str]]: A tuple containing:
            - The processed experiment configuration
            - The order of selected SetCodes from shuffled blocks
            
    Raises:
        ValueError: If the YAML structure is invalid or missing required components.
    """
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    
    experiment_content = data.get('experiment_content', [])
    
    if len(experiment_content) < 2:
        raise ValueError("Experiment content must contain at least begin and end blocks")
    
    # Extract blocks
    begin_block = experiment_content[0]
    end_block = experiment_content[1]
    middle_blocks = experiment_content[2:]
    
    # Process begin block (skip "Begin" type entry)
    if begin_block[0].get('type') != 'Begin':
        raise ValueError("First block must start with type: 'Begin'")
    config_start = begin_block[1:]
    
    # Process middle blocks
    processed_middles = []
    setcodes = []
    for block in middle_blocks:
        if not block or 'SetCode' not in block[0]:
            raise ValueError("Middle blocks must start with SetCode")
        setcode = block[0]['SetCode']
        steps = block[1:]
        processed_middles.append((setcode, steps))
        setcodes.append(setcode)
    
    # Shuffle middle blocks but preserve internal order
    random.shuffle(processed_middles)
    selected_order = [sc for sc, _ in processed_middles]
    config_middle = [step for _, steps in processed_middles for step in steps]
    
    # Process end block (merge all entries into single dict)
    if end_block[0].get('type') != 'end':
        raise ValueError("End block must start with type: 'end'")
    end_config = {}
    for entry in end_block:
        end_config.update(entry)
    
    # Combine all parts
    final_config = []
    final_config.extend(config_start)
    final_config.extend(config_middle)
    final_config.append(end_config)
    
    # Ensure checkbox_text is always a list
    for step in final_config:
        if step.get('type') == 'consent' and 'checkbox_text' in step:
            cb_text = step['checkbox_text']
            if isinstance(cb_text, str):
                step['checkbox_text'] = [cb_text]
    
    return final_config, selected_order

# Example usage:
# config, order = load_experiment_config("experiment.yml")
# print("Generated Config:", config)
# print("Block Order:", order)