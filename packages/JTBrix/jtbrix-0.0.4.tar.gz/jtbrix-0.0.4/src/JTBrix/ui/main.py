from flask import Blueprint, request, render_template_string
import json

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
            const results = { answers: [], times: [] };
            const popupResult = [];

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
                // Save previous step's results
                if (stepIndex >= 0) {
                    const currentStep = flow[stepIndex];
                    if (['question', 'dropdown'].includes(currentStep.type)) {
                        results.answers.push(answer);
                        results.times.push(time);
                    }
                    else if (currentStep.type === 'dob') {
                        results.answers.push(answer);
                    }
                    if (currentStep.type === 'popup') {
                        popupResult.push({ answer, time });
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
                    const fullResults = {
                        answers: results.answers,
                        times: results.times,
                        popup_results: popupResult
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
                    case "end":
                        const fullResults = {
                            answers: results.answers,
                            times: results.times,
                            popup_results: popupResult
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
                popupResult.push({ answer, time });  // ✅ push to the array

                const fullResults = {
                    answers: results.answers,
                    times: results.times,
                    popup_results: popupResult  // ✅ now this is a list of all popups
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
            nextStep();
        </script>
    </body>
    </html>
    """, flow_json=flow_json)

@ui.route("/submit_results", methods=["POST"])
def submit_results():
    data = request.get_json()
    submitted_results.append(data)
    print("✅ Results submitted:", json.dumps(data, indent=2))
    return "", 204

@ui.route("/view_results")
def view_results():
    return "<pre>" + json.dumps(submitted_results, indent=2) + "</pre>"