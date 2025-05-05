from flask import Blueprint, render_template_string
import os
from flask import Blueprint, request, render_template


screens = Blueprint("screens", __name__)
from flask import render_template, abort
from JTBrix import screen_config

@screens.route("/screen/question/<int:index>")
def show_question(index):
    try:
        step = screen_config.flow_config[index]
    except IndexError:
        return abort(404, description="Invalid step index")

    if step.get("type") != "question":
        return abort(400, description="Expected a question step")

    prompt = step.get("prompt", "")
    options = step.get("options", [])
    colors = step.get("colors", [])
    image = step.get("image", "")

    if len(options) != 2 or len(colors) != 2:
        return abort(400, description="Questions must have 2 options and 2 colors")

    return render_template("question_screen.html",
        index=index,
        question=prompt,
        option1=options[0],
        option2=options[1],
        color1=colors[0],
        color2=colors[1],
        image=image
    )

@screens.route("/screen/video")
def show_video():
    filename = request.args.get("filename")
    if not filename:
        return "Missing video filename", 400

    return render_template("video_screen.html", filename=filename)



@screens.route("/screen/dob/<int:index>")
def screen_dob(index):
    try:
        step = screen_config.flow_config[index]
    except IndexError:
        return abort(404, description="Invalid step index")

    if step.get("type") != "dob":
        return abort(400, description="Expected a dob step")

    prompt = step.get("prompt", "Please enter your date of birth")

    html = f"""
    <div style="padding: 40px; color: black; background: white; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <p style="font-size: 18px;">{prompt}</p>
        <input type="date" id="dobInput" style="font-size: 16px; padding: 10px; margin: 20px 0;">
        <button id="nextBtn" disabled style="padding: 10px 20px; font-size: 16px; background: #007BFF; color: white; border: none; border-radius: 6px;">Next</button>
    </div>
    <script>
        const btn = document.getElementById('nextBtn');
        const dob = document.getElementById('dobInput');
        const start = Date.now();

        dob.addEventListener('change', function() {{
            btn.disabled = !dob.value;
        }});

        btn.addEventListener('click', function() {{
            const birthDate = new Date(dob.value);
            const today = new Date();
            const age = today.getFullYear() - birthDate.getFullYear();
            const duration = Date.now() - start;
            console.log("DOB submitted:", dob.value, " → Age:", age);
            window.parent.nextStep(age, duration);
        }});
    </script>
    """
    return render_template_string(html)

@screens.route("/screen/consent")
def screen_consent():
    config = screen_config.flow_config[0]  # assuming consent is at index 0
    main_text = config.get("main_text", "Please read the following.")
    checkbox_texts = config.get("checkbox_text", ["I agree to participate."])
    button_text = config.get("button_text", "Begin")
    button_color = config.get("button_color", "#007BFF")

    checkbox_html = ""
    for i, text in enumerate(checkbox_texts):
        checkbox_html += f"""
            <label>
                <input type="checkbox" class="consent-checkbox" id="checkbox_{i}"> {text}
            </label><br>
        """

    html = f"""
    <div style="padding: 40px; color: black; background: white; height: 100%;">
        <p style="font-size: 18px;">{main_text}</p>
        {checkbox_html}
        <br>
        <button id="startBtn" disabled style="padding: 10px 20px; font-size: 16px; background: {button_color}; color: white; border: none; border-radius: 6px;">{button_text}</button>
    </div>
    <script>
        function toggleButton() {{
            const btn = document.getElementById('startBtn');
            const boxes = document.querySelectorAll('.consent-checkbox');
            btn.disabled = ![...boxes].every(b => b.checked);
        }}

        document.addEventListener("DOMContentLoaded", function () {{
            document.querySelectorAll(".consent-checkbox").forEach(cb => cb.addEventListener("change", toggleButton));
            document.getElementById("startBtn").addEventListener("click", function () {{
                window.parent.nextStep();
            }});
        }});
    </script>
    """
    return render_template_string(html)

@screens.route("/screen/popup/<int:index>")
def screen_popup(index):
    try:
        step = screen_config.flow_config[index]
    except IndexError:
        return abort(404, description="Invalid step index")

    if step.get("type") != "popup":
        return abort(400, description="Expected a popup step")

    question = step.get("question", "")
    options = step.get("options", [])
    colors = step.get("colors", [])

    if len(options) != 3 or len(colors) != 3:
        return abort(400, description="Popup must have 3 options and 3 colors")

    html = f"""
    <div style="height:100%; display: flex; align-items: center; justify-content: center;">
        <div id="popup" style="width: 33vw; height: 33vh; background: white; border-radius: 12px; padding: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.3); display: flex; flex-direction: column; justify-content: space-around; align-items: center;">
            <h2>{question}</h2>
            <div>
                <button style="background:{colors[0]}; padding:10px; margin:5px; color:white;" onclick="submitPopup('{options[0]}')">{options[0]}</button>
                <button style="background:{colors[1]}; padding:10px; margin:5px; color:white;" onclick="submitPopup('{options[1]}')">{options[1]}</button>
                <button style="background:{colors[2]}; padding:10px; margin:5px; color:white;" onclick="submitPopup('{options[2]}')">{options[2]}</button>
            </div>
        </div>
    </div>
    <script>
        const startTime = Date.now();
        function submitPopup(answer) {{
            const time = (Date.now() - startTime) / 1000;
            window.parent.submitPopup(answer, time);
        }}
    </script>
    """
    return render_template_string(html)


@screens.route("/screen/dropdown/<int:index>")
def screen_dropdown(index):
    try:
        step = screen_config.flow_config[index]
    except IndexError:
        return abort(404, description="Invalid step index")

    if step.get("type") != "dropdown":
        return abort(400, description="Expected a dropdown step")

    prompt = step.get("prompt", "Please select an option")
    options = step.get("options", [])

    dropdown_html = ''.join(
        f'<option value="{opt}">{opt}</option>' for opt in options
    )

    html = f"""
    <div style="padding: 40px; color: black; background: white; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <p style="font-size: 18px;">{prompt}</p>
        <select id="dropdown" style="font-size: 16px; padding: 10px; margin: 20px 0;">
            <option value="" disabled selected>Select...</option>
            {dropdown_html}
        </select>
        <button id="nextBtn" disabled style="padding: 10px 20px; font-size: 16px; background: #007BFF; color: white; border: none; border-radius: 6px;">Next</button>
    </div>
    <script>
        const dropdown = document.getElementById("dropdown");
        const btn = document.getElementById("nextBtn");
        const start = Date.now();

        dropdown.addEventListener("change", function() {{
            btn.disabled = !dropdown.value;
        }});

        btn.addEventListener("click", function() {{
            const selected = dropdown.value;
            const duration = Date.now() - start;
            console.log("Dropdown selected:", selected);
            window.parent.nextStep(selected, duration);
        }});
    </script>
    """
    return render_template_string(html)