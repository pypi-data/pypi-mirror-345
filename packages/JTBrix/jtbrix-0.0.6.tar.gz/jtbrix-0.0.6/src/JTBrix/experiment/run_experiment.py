from typing import Tuple
from JTBrix.screen_config import flow_config
from JTBrix.experiment.run_session import run_entire_test_config
from JTBrix.utils.config import read_experiment_config

def run_test(config_path: str, static_folder: str, timeout: int = 600) -> Tuple[dict, list]:
    """
    Run an experiment from a YAML configuration file
    
    Args:
        config_path (str): Path to experiment YAML config file
        static_folder (str): Path to static assets directory
        
    Returns:
        Tuple[list, list]: 
            - Experiment results list
            - Block execution order list
    """
    # Load and validate config
    config, order = read_experiment_config(config_path)
    
    print("CONFIG:")
    print(config)
    print("\nSELECTED ORDER:", order)

    # Update global flow config
    flow_config.clear()
    flow_config.extend(config)
    
    # Run experiment and return results
    results = run_entire_test_config(config, static_folder=static_folder, timeout=timeout)
    return results, order

