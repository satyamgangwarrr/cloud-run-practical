# Cloud Run Assignment

## Objective
This project demonstrates basic cloud computing skills including Linux shell scripting, containerization, and deployment of a serverless application on Google Cloud Run.

---

## Project Description
The assignment automates system checks using a shell script, builds a simple Python Flask web application, containerizes it using Docker, and deploys it to Google Cloud Run. The complete source code is maintained using GitHub.

---

## Technologies Used
- Linux (Cloud Shell / VM)
- Bash Scripting
- Python (Flask)
- Docker
- Google Cloud Run
- Git & GitHub

---

## Project Structure
sys_check.sh  
deploy_app/  
  ├── main.py  
  ├── requirements.txt  
  └── Dockerfile  

---

## Task 1: Linux & Shell Scripting
A shell script `sys_check.sh` is created to:
- Print current date and time
- Display disk usage using `df -h`
- Show the current logged-in user
- Save the output to `log.txt`
- Create a directory named `deploy_app` if it does not exist
- Move `log.txt` into the `deploy_app` directory
- The script is made executable using `chmod +x`

---

## Task 2: Python Flask Application
A simple Flask web application is developed inside the `deploy_app` directory.

- The application listens on the root route (`/`)
- It returns the message:

Hello from Cloud Run! System check complete.

- Dependencies are defined in `requirements.txt`:
  - Flask
  - gunicorn

---

## Task 3: Containerization
A Dockerfile is created to:
- Use a lightweight Python base image
- Install dependencies
- Copy application files into the container
- Run the application using Gunicorn on port 8080

---

## Task 4: Deployment to Google Cloud Run
Steps followed:
1. Enabled Cloud Run and Cloud Build services
2. Built the container image using Cloud Build
3. Deployed the container to Google Cloud Run
4. Enabled public (unauthenticated) access

---

## Cloud Run Live URL
The deployed application is accessible at:

[https://satyam-gangwar-370498901616.us-central1.run.app/]

---

## Key Learnings
- Difference between local and cloud environments
- Linux automation using shell scripting
- Container-based application deployment
- Serverless computing using Cloud Run
- Source code management using GitHub

---

## Author
Satyam Gangwar

---

## Notes
- The Cloud Run service remains active even after closing Cloud Shell
- The application automatically scales based on incoming requests
- No server management is required

---

This project is submitted as part of a Cloud assignment.
