from flask import Flask, render_template, request, redirect ,url_for,session
import sklearn.pipeline
import pickle
import fitz  # PyMuPDF
import csv
import re
import io
import base64
import matplotlib.pyplot as plt
import language_tool_python

import numpy as np
from sklearn import pipeline

app = Flask(__name__)
tool = language_tool_python.LanguageTool('en-US')
# Load the trained model
model = pickle.load(open(r'C:\Users\Varshini\PycharmProjects\untitled\latest.pkl', 'rb'))

sections = {
  "Personal Information": 5,
  "Objective": 13,
  "Education": 10,
  "Work and Related Experience": 15,
  "Awards and Honors": 5,
  "Activities/Hobbies": 5,
  "Skills": 40,
  "References": 5,
}

# Define suggestions for improvement for each section
suggestions = {
  "Personal Information": "Consider adding your address, phone number, and email for better contact information.",
  "Objective": "Craft a more specific objective statement that directly relates to the job you're applying for.",
  "Education": "Include more details about your education, such as GPA or relevant coursework.",
  "Work and Related Experience": "Provide detailed job descriptions and highlight relevant skills and accomplishments.",
  "Awards and Honors": "Expand on your awards and honors, including why you received them and their significance.",
  "Activities/Hobbies": "Elaborate on your extracurricular activities and hobbies to showcase your interests and skills.",
  "Skills": "Be more specific about your skills, including software proficiency, languages, and certifications.",
  "References": "Consider providing contact information for your references."
}


def calculate_score(resume_text):
  resume_lower = resume_text.lower()
  total_score = 0
  suggestions_list = []

  for section, score in sections.items():
    if section.lower() in resume_lower:
      total_score += score
    else:
      suggestions_list.append(suggestions[section])

  return total_score, suggestions_list


def create_score_chart(score):
  labels = ["Low", "Moderate", "High"]
  values = [20, 60, 100]  # Adjust these values as needed for your chart

  plt.figure(figsize=(8, 4))
  plt.bar(labels, values, color=['red', 'yellow', 'green'])
  plt.xlabel("Resume Score")
  plt.ylabel("Score Range")
  plt.title(f"Resume Score: {score}")

  # Save the chart as an image
  img = io.BytesIO()
  plt.savefig(img, format='png')
  img.seek(0)

  # Encode the image data as base64
  img_base64 = base64.b64encode(img.read()).decode()

  return img_base64


@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files["resume"]

        if uploaded_file.filename != "":
            try:
                # Read the uploaded PDF file
                pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text = ""

                for page_num in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()

                # Evaluate key points and grammar
                # education_score = calculate_score(text, education_keywords)
                # experience_score = calculate_score(text, experience_keywords)
                # internship_score = calculate_score(text, internship_keywords)
                # interests_score = calculate_score(text, interests_keywords)
                # grammar_errors = len(tool.check(text))

                score, suggestions_list = calculate_score(text)

                if score >= 40:
                  resume_score = "High"
                elif score >= 20:
                  resume_score = "Moderate"
                else:
                  resume_score = "Low"

                # Create the score visualization as base64-encoded image data
                chart_image = create_score_chart(score)

                return render_template("res.html", resume_score=resume_score, suggestions=suggestions_list,
                                       chart_image=chart_image)

                # Calculate an overall score
                # overall_score = (education_score + experience_score + internship_score + interests_score) / 4

                # You can now work with the scores and grammar_errors
                # return render_template(
                #     "result.html",
                #     education_score=education_score,
                #     experience_score=experience_score,
                #     internship_score=internship_score,
                #     interests_score=interests_score,
                #     grammar_errors=grammar_errors,
                #     overall_score=overall_score,
                # )

            except Exception as e:
                return f"An error occurred: {str(e)}"

    return render_template("ind.html")


@app.route('/')
def home():
  return render_template('home.html')

@app.route('/course')
def course():
  return render_template('course.html')

@app.route('/ca')
def ca():
  return render_template('ca.html')

@app.route('/ip')
def ip():
  return render_template('ip.html')

@app.route('/check')
def check():
  return render_template('new.html')

@app.route('/new', methods=['GET','POST'])
def new():
    x=[x for x in request.form.values()]
    ssc_p = x[1]
    if x[2] == 'central':
      ssc_b = 0
    else:
      ssc_b = 1

    hsc_p = x[3]

    if x[4] == 'central':
      hsc_b=0
    else:
      hsc_b=1

    if x[5] == 'Commerce':
      hsc_s=1
    elif x[5] == 'Science':
      hsc_s=2
    else:
      hsc_s = 0

    degree_p = x[6]

    if x[7] == 'Sci&Tech':
      degree_t=2
    elif x[7] == 'Comm&Mgmt':
      degree_t = 0
    else:
      degree_t=1

    if x[8] == 'yes':
      workex=1
    else:
      workex=0

    etest_p = x[9]
    if x[10] == 'Mkt&HR':
      specialization=1
    else:
      specialization=0

    mba_p = x[11]
    Internships = x[12]
    if x[13] == 'male':
      gen=1
    else:
      gen = 0

    salary=x[14]
    arr = np.array([[gen,ssc_p,ssc_b,hsc_p,hsc_b,hsc_s,degree_p,degree_t,workex,etest_p,specialization,mba_p,Internships,salary]])
    pred = model.predict(arr)
    return render_template("predict.html",predi=pred)
#     return redirect(url_for('predict',pr=pred))
#
# @app.route('/predict')
# def predict():
#   return render_template("predict.html",=predi)
@app.route('/clgcheck')
def clgcheck():
  return render_template('clgind.html')


@app.route('/clgnew', methods=['GET','POST'])
def clgnew():
  if 'clgdata' not in request.files:
    return "No file part"


  file = request.files['clgdata']

  if file.filename == '':
    return "No selected file"

  if file:
    # Read the CSV file and convert it to a 2D array
    csv_data = []
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.reader(stream)
    next(csv_reader, None)
    for row in csv_reader:
      csv_data.append(row)
    res=np.array(model.predict(csv_data))
    print(res)
    pla = np.count_nonzero(res == 1)
    npla = np.count_nonzero(res == 0)
    return render_template('college.html',pla=pla,npla=npla)



if __name__ == '__main__':
       app.run()

# ssc_p = request.form['ssc_p']
#     ssc_b = request.form['ssc_b']
#     hsc_p = request.form['hsc_p']
#     hsc_b = request.form['hsc_b']
#     hsc_s = request.form['hsc_m']
#     degree_p = request.form['d_p']
#     degree_t = request.form['d_b']
#     workex = request.form['w_e']
#     etest_p = request.form['e_p']
#     specialisation = request.form['Spec']
#     mba_p = request.form['spec_p']
#     Internships = request.form['in']
#     arr = np.array([[ssc_p,ssc_b,hsc_p,hsc_b,hsc_s,degree_p,degree_t,workex,etest_p,specialisation,mba_p,Internships]])
#     pred = model.predict(arr)
