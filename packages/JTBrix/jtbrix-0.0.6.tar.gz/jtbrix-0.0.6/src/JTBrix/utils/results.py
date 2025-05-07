
from JTBrix.utils.config import load_experiment_content_by_block

def get_combined_results(submitted_results):
    # Get the last complete (finished) submission
    for entry in reversed(submitted_results):
        if entry.get("finished"):
            return entry.copy()

    # Fallback if none finished
    return {}



def build_structured_blocks(raw_result: dict, setcode_blocks: dict, execution_order: list) -> list:
    """
    Reconstructs and reorders block-level results from the raw result using the setcode block definitions
    and the execution order.

    Args:
        raw_result: dict containing flat fields like 'questions_answers', 'questions_times', etc.
        setcode_blocks: dict mapping SetCode to its list of content items
        execution_order: list of SetCodes indicating the order of execution

    Returns:
        A list of block-level structured results with answers, times, and popup, sorted by SetCode.
    """

    # Prepare iterators over flat result lists
    answer_iter = iter(raw_result.get("questions_answers", []))
    time_iter = iter(raw_result.get("questions_times", []))
    popup_iter = iter(raw_result.get("popup_results", []))

    structured_blocks = []

    for setcode in execution_order:
        block_config = setcode_blocks.get(setcode, [])
        num_questions = sum(1 for item in block_config if item.get("type") == "question")
        has_popup = any(item.get("type") == "popup" for item in block_config)

        answers = [next(answer_iter) for _ in range(num_questions)]
        times = [next(time_iter) for _ in range(num_questions)]
        popup = next(popup_iter) if has_popup else None

        structured_blocks.append({
            "SetCode": setcode,
            "answers": answers,
            "times": times,
            "popup": popup
        })

    # Sort the result blocks by SetCode (numerically if possible)
    structured_blocks.sort(key=lambda b: int(b["SetCode"]) if b["SetCode"].isdigit() else b["SetCode"])
    return structured_blocks

def build_full_structured_result(raw_result: dict, config_path: str, execution_order: list) -> dict:
    """
    Builds a fully structured result from raw submission and config,
    including participant info, metadata, and block-wise results.

    Args:
        raw_result: Flat submitted results from frontend
        config: Full experiment config parsed using load_experiment_content_by_block
        execution_order: List of executed SetCodes (e.g. ['2', '4', '3', '1'])

    Returns:
        A complete structured result dictionary.
    """
    if not execution_order:
        raise ValueError("Execution order must be provided.")
    
    config = load_experiment_content_by_block(config_path)
    begin = config.get("begin", [])
    text_inputs = raw_result.get("text_input_results", [])
    dob_results = raw_result.get("dob_results", [])
    dropdown_results = raw_result.get("dropdown_results", [])

    structured = {}

    # Extract fields from 'begin' block
    text_index = 0
    for item in begin:
        if item.get("type") == "text_input":
            field_id = item.get("id", f"text_input_{text_index}")
            structured[field_id] = text_inputs[text_index] if text_index < len(text_inputs) else None
            text_index += 1

    if any(item.get("type") == "dob" for item in begin):
        structured["age"] = dob_results[0] if dob_results else None

    dropdown_index = 0
    for item in begin:
        if item.get("type") == "dropdown":
            label_key = "country" if dropdown_index == 0 else "native_language"
            structured[label_key] = dropdown_results[dropdown_index] if dropdown_index < len(dropdown_results) else None
            dropdown_index += 1

    # Metadata
    structured["experiment_start"] = raw_result.get("experiment_start")
    structured["experiment_duration_sec"] = raw_result.get("experiment_duration_sec")
    structured["completed"] = raw_result.get("finished", False)
    structured["execution_order"] = execution_order

    # Add structured blocks based on SetCode
    structured["blocks"] = build_structured_blocks(
        raw_result=raw_result,
        setcode_blocks=config.get("setcodes", {}),
        execution_order=execution_order
    )

    return structured



