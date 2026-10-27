# 🧭 Career Compass — Personalized Career Guidance Platform

Career Compass is a career-guidance web application designed to help students explore possible career paths based on their interests, academic background, skills, and goals. It aims to make career exploration easier, particularly for students making important decisions after Class 10 or Class 12.

> **Important:** Career recommendations are intended to support exploration and discussion. They do not guarantee a particular outcome or replace professional career counselling. Always verify course eligibility and admission requirements with official institutions.

## 🎯 Project Objectives

- Help students explore career options that align with their interests and goals.
- Provide personalized career recommendations through an assessment.
- Help students by providing structure roadmap.
- Give users a way to revisit saved career guidance and assessment results.

## ✨ Features

- **Career assessment:** Uses assessment responses to help identify relevant career areas.
- **Career recommendations:** Presents career suggestions based on the application's recommendation logic.
- **Academic guidance:** Supports career exploration for students at different academic stages and relevant roadmap.
- **Accounts and login:** Allows users to register and sign in.
- **Student profile:** Stores relevant profile information.
- **Saved assessment activity:** Uses a local database to retain supported account and assessment information.
- **Web interface:** Provides a browser-based interface served by Flask.

The exact recommendations and available screens depend on the features implemented in the current version of the application.

## 🛠️ Technology Stack

- **Python** — backend programming
- **Flask** — web application framework
- **HTML** — page structure
- **CSS and JavaScript** — interface styling and client-side interactions, where used
- **SQLite** — local data storage
- **Werkzeug Security** — password hashing and verification, where used by the application
- **Visual Studio Code** — development environment

## 📁 Project Files

```text
Career_Compass_VSCode/
├── app.py
├── index.html
├── requirements.txt
├── .gitignore
└── README.md
```

The application may create `career_compass.db` automatically when it runs. Other local or generated files may also appear depending on how you use the project.

- `app.py` — Flask application and backend logic.
- `index.html` — web interface.
- `requirements.txt` — Python package requirements.
- `.gitignore` — specifies files Git should ignore.
- `README.md` — project documentation.

## ⚙️ Setup and Installation (Windows / VS Code)

### Prerequisites

Install Python 3 and Visual Studio Code.

### 1. Open the project

Extract the ZIP file, then open the `Career_Compass_VSCode` folder in VS Code using **File → Open Folder**.

### 2. Open a terminal

In VS Code, select **Terminal → New Terminal**.

### 3. Create a virtual environment

```powershell
py -m venv .venv
```

### 4. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 5. Run the application

```powershell
.\.venv\Scripts\python.exe app.py
```

### 6. Open it in your browser

Visit:

http://127.0.0.1:5000

Keep the terminal open while using the application. For full functionality, run the Flask application and open the local address rather than opening `index.html` directly.

## 🔄 Typical User Flow

1. Register for an account or sign in, if account features are enabled.
2. Enter the academic or career information requested by the application.
3. Complete the available career assessment.
4. Review the career guidance and recommendations displayed.
5. Revisit saved information through the application's supported dashboard or account features.

The exact flow depends on the functionality available in the current version.

## 🗄️ Local Database

The application creates `career_compass.db` in the project folder automatically when it first runs, according to the current project setup. Keep this file if you want to retain locally stored accounts and saved activity. Deleting it may remove that local data.

## 🔐 Security and Deployment Notes

This project is documented for local development. Before deploying it publicly, review the application's secret-key configuration, session security, input validation, database access controls, HTTPS setup, and production server configuration. Do not commit passwords, private keys, or other secrets to GitHub.

## 🚧 Possible Future Improvements

Potential future additions could include:

- More detailed career and qualification profiles.
- Future trend analysis.
- Progress tracking.
- Accessibility Features: Implement text-to-speech and speech-to-text functionality to make Career Compass more accessible for specially-abled students.
.

## 🎓 Intended Audience

Career Compass is intended primarily for students who want to explore career choices and educational pathways, including those making decisions after Class 10 or Class 12. It may also be useful as a starting point for discussions with parents, teachers, and career counsellors.

## 📌 Project Information

- **Project:** Career Compass
- **Type:** Career guidance web application
- **Backend:** Python / Flask
- **Database:** SQLite
- **Development environment:** Visual Studio Code

## License

No license specified.

---

*Career Compass — Explore your interests. Discover your options. Plan your future.*
