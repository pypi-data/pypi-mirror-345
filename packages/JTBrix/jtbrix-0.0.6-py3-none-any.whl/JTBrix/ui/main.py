from flask import Blueprint, request, render_template_string
import json
from JTBrix.utils.results import get_combined_results




ui = Blueprint("ui", __name__)
submitted_results = []

@ui.route("/experiment")
def experiment():
    from JTBrix.screen_config import flow_config
    flow_json = json.dumps(flow_config)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Experiment</title>
        <meta charset="UTF-8">
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                font-family: Arial, sans-serif;
                background-color: black;
            }
            #content {
                width: 100%;
                height: 100%;
                overflow: hidden;
            }
            iframe {
                border: none;
            }
        </style>
    </head>
    <body>
        <div id="content"></div>

        <script>
            const flow = {{ flow_json | safe }};
            let stepIndex = -1;
            const results = {
                questions_answers: [],
                questions_times: [],
                popup_results: [],
                text_input_results: [],
                dob_results: [],
                dropdown_results: [],
                finished: false
            };
            let popupSubmitted = false;

            // --- listen for nextStep requests coming from child iframes ---
            window.addEventListener("message", (event) => {
                if (event.data && event.data.type === "nextStep") {
                    nextStep(event.data.answer ?? null, event.data.time ?? null);
                }
            });
            // ----------------------------------------------------------------

            function loadScreen(screenUrl) {
                const contentDiv = document.getElementById('content');
                contentDiv.innerHTML = '';
                const iframe = document.createElement('iframe');
                iframe.style.width = '100%';
                iframe.style.height = '100%';
                iframe.src = screenUrl;
                contentDiv.appendChild(iframe);
            }

            function nextStep(answer = null, time = null) {
                popupSubmitted = false;
                // Save previous step's results — but skip automatic handling for pop‑ups
                if (stepIndex >= 0) {
                    const currentStep = flow[stepIndex];

                    if (currentStep.type !== 'popup') { // popup already handled in submitPopup()
                        switch (currentStep.type) {
                            case 'question':
                                results.questions_answers.push(answer);
                                results.questions_times.push(time);
                                break;
                            case 'dropdown':
                                results.dropdown_results.push(answer);
                                break;
                            case 'dob':
                                results.dob_results.push(answer);
                                break;
                            case 'text_input':
                                results.text_input_results.push(answer);
                                break;
                        }
                    }
                }

                stepIndex++;

                // Check if experiment is complete
                if (stepIndex >= flow.length) {
                    const endHTML = `
                        <div style="display: flex; justify-content: center; align-items: center; 
                                    height: 100vh; background: white; color: #333; font-family: Arial;">
                            <h1>Thank you for participating!</h1>
                        </div>`;
                    document.getElementById('content').innerHTML = endHTML;
                    document.exitFullscreen();
                    
                    // Submit final results
                    results.finished = true;
                    const fullResults = {
                        questions_answers: results.questions_answers,
                        questions_times: results.questions_times,
                        popup_results: results.popup_results,
                        text_input_results: results.text_input_results,
                        dob_results: results.dob_results,
                        dropdown_results: results.dropdown_results,
                        finished: results.finished
                    };
                    fetch("/submit_results", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(fullResults)
                    });
                    
                    return;
                }

                // Load next step
                const step = flow[stepIndex];
                switch(step.type) {
                    case "consent":
                        loadScreen("/screen/consent");
                        break;
                    case "dob" :
                        loadScreen(`/screen/dob/${stepIndex}`);
                        break;  
                    case "dropdown":
                        loadScreen(`/screen/dropdown/${stepIndex}`);
                        break;
                    case "video":
                        loadScreen(`/screen/video?filename=${encodeURIComponent(step.video_filename)}`);
                        break;
                    case "question":
                        loadScreen(`/screen/question/${stepIndex}`);
                        break;
                    case "popup":
                        loadScreen(`/screen/popup/${stepIndex}`);
                        break;
                    case "text_input":
                        loadScreen(`/screen/text_input/${stepIndex}`);
                        break;
                    case "end":
                        results.finished = true;
                        const fullResults = {
                            questions_answers: results.questions_answers,
                            questions_times: results.questions_times,
                            popup_results: results.popup_results,
                            text_input_results: results.text_input_results,
                            dob_results: results.dob_results,
                            dropdown_results: results.dropdown_results,
                            finished: results.finished
                        };
                        const endHTML = `
                            <div style="display: flex; justify-content: center; align-items: center; 
                                        height: 100vh; background: ${step.background || "#f0f0f0"}; 
                                        color: ${step.text_color || "#333"}; font-family: Arial;">
                                <h1>${step.message || "Thank you for your participation!"}</h1>
                            </div>`;
                        document.getElementById('content').innerHTML = endHTML;
                        document.exitFullscreen();

                        // ✅ Submit results
                        fetch("/submit_results", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(fullResults)
                        });

                        break;
                    default:
                        console.error("Unknown step type:", step.type);
                }
            }

            function submitPopup(answer, time) {
                if (popupSubmitted) {
                    console.warn("🚫 Popup already submitted — skipping");
                    return;
                }

                if (answer == null) {
                    console.warn("🚫 Null/undefined popup answer — skipping");
                    return;
                }

                popupSubmitted = true;

                results.popup_results.push(answer);

                if (flow[stepIndex + 1] && flow[stepIndex + 1].type === "end") {
                    results.finished = true;
                }

                const fullResults = {
                    questions_answers: results.questions_answers,
                    questions_times: results.questions_times,
                    popup_results: results.popup_results,
                    text_input_results: results.text_input_results,
                    dob_results: results.dob_results,
                    dropdown_results: results.dropdown_results,
                    finished: results.finished
                };

                fetch("/submit_results", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(fullResults)
                }).then(() => {
                    const step = flow[stepIndex + 1];  // peek ahead
                    if (step && step.type === "end") {
                        stepIndex++;  // advance manually
                        const endHTML = `
                            <div style="display: flex; justify-content: center; align-items: center; 
                                        height: 100vh; background: ${step.background || "#f0f0f0"}; 
                                        color: ${step.text_color || "#333"}; font-family: Arial;">
                                <h1>${step.message || "Thank you for your participation!"}</h1>
                            </div>`;
                        document.getElementById('content').innerHTML = endHTML;
                        document.exitFullscreen();
                    } else {
                        nextStep();  // fallback
                    }
                });
            }

            // Start experiment
            document.documentElement.requestFullscreen().catch(e => {});
            window.addEventListener("nextScreen", () => nextStep());
            nextStep();
        </script>
    </body>
    </html>
    """, flow_json=flow_json)

aggregated_results = {
    "questions_answers": [],
    "questions_times": [],
    "popup_results": [],
    "text_input_results": [],
    "dob_results": [],
    "dropdown_results": [],
    "finished_flags": []
}

@ui.route("/submit_results", methods=["POST"])
def submit_results():
    data = request.get_json()
    submitted_results.append(data)

    # Update the live aggregated state
    for key in ["questions_answers", "questions_times", "popup_results",
                "text_input_results", "dob_results", "dropdown_results"]:
        if key in data:
            aggregated_results[key].extend(data[key])

    # Handle finished flag separately
    aggregated_results["finished_flags"].append(data.get("finished", False))

    print("✅ Results submitted:", json.dumps(data, indent=2))
    return "", 204

@ui.route("/view_results")
def view_results():
    return "<pre>" + json.dumps(submitted_results, indent=2) + "</pre>"


@ui.route("/view_aggregated_results")
def view_aggregated_results():
    return "<pre>" + json.dumps(aggregated_results, indent=2) + "</pre>"





@ui.route("/get_combined_dict")
def get_combined_dict():
    combined = get_combined_results(submitted_results)
    return "<pre>" + json.dumps(combined, indent=2) + "</pre>"