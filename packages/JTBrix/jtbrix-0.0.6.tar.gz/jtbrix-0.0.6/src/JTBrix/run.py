from JTBrix.app import app
from flask import request, jsonify
from JTBrix import run_test
from JTBrix.utils.results import build_full_structured_result
from JTBrix.io.saving import save_structured_output

@app.route("/run_experiment")
def run_experiment_from_web():
    results, order = run_test("data/config.yml", "data/static/", timeout=300)
    structured_output = build_full_structured_result(results, "data/config.yml", execution_order=order)
    save_structured_output(structured_output, save_path="data/results/", name="Test_data")
    return jsonify({"status": "success", "order": order, "summary": structured_output})