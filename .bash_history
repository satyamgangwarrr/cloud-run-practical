ls
nano sys_check.sh
ls
chmod +x sys_check.sh 
ls -l
ls
./sys_check.sh 
ls
cat deploy_app/log.txt 
cd deploy_app/
nano main.py
nano requirements.txt
nano Dockerfile
gcloud config set project cloud-first-assignment-486217
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
gcloud config get-value project
ls
gcloud config set project cloud-run-assignment-486813
cd deploy_app/
ls
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
gcloud builds submit --tag gcr.io/cloud-run-assignment-486813/hello-cloud-run
gcloud run deploy hello-cloud-run --image gcr.io/cloud-run-assignment-486813/hello-cloud-run --platform managed --region us-central1 --allow-unauthenticated
cd
cd .
ls
git init
nano .gitignore
git add .
ls
git status
girgi
vvv
git commit -m "Initial Cloud Run practical assignment"
git remote add origin https://github.com/satyamgangwarrr/cloud-run-practical.git
git remote -v
git branch -M main
git push -u origin main
git add .
git commit -m "Initial Cloud Run practical assignment"
git branch -M main
git push -u origin main
git config --global user.name "Satyam Gangwar"
git config --global user.email "satyam.gangwar@highspring.in"
