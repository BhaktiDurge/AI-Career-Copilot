from flask import Flask, render_template, request, redirect, session
from db import Base, engine, SessionLocal
import models
import PyPDF2
import docx
import json
from ai import analyze_resume
import random
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from flask import flash

#used for FORGOT PASSWORD
load_dotenv()

app = Flask(__name__)
app.secret_key = "Secret123"

Base.metadata.create_all(bind=engine)

#HOME
@app.route("/")
def home():
   if "user" in session:
      return redirect("/dashboard")
   return redirect("/login")

#SINGUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
   db = SessionLocal()

   if request.method == "POST":
      email = request.form.get("email")
      password = request.form.get("password")

      existing_user = db.query(models.User).filter_by(email=email).first()
      
      if existing_user:
         return "User already exists"
      
      user = models.User(email=email, password=password)
      db.add(user)
      db.commit()
      return redirect("/login")
   
   return render_template("signup.html")

#LOGIN
@app.route("/login", methods=["POST", "GET"])
def login():
   db = SessionLocal()

   if request.method == "POST":
      email = request.form.get("email")
      password = request.form.get("password")

      user = db.query(models.User).filter_by(email=email, password=password).first()

      if user:
         session["user"] = user.email
         return redirect("/dashboard")
      else:
         return "Invalid credentials"
      
   return render_template("login.html")
      

#DASHBOARD
@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    
   if "user" not in session:
        flash("Login to see the Dashboard", "error")
        return redirect("/login")

   db = SessionLocal()
   result = {} 
   user_goal = request.form.get("role")
   resume_text = request.form.get("resume")

   file = request.files.get("file")

   #file handeling
   if file and file.name != "":
      if file.filename.endswith(".pdf"):
         try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
               text += page.extract_text() or ""
            resume_text = text
         except Exception as e:
            result = {"error": f"PDF error: {str(e)}"}

      elif file.filename.endswith(".docx"):
         try:
            doc = docx.Document(file)
            text = ""
            for para in doc.paragraphs:
               text += para.text + "\n"
            resume_text = text
         except Exception as e:
            result = {"error": f"Docx error:{str(e)}"}


   if resume_text and user_goal:
      try:
         result = analyze_resume(resume_text, user_goal)

         #save to db
         user = db.query(models.User).filter_by(email=session["user"]).first()

         report = models.Report(
            user_id = user.id,
            resume_text = resume_text,
            result = json.dumps(result)
         )

         db.add(report)
         db.commit()


      except Exception as e:
         result = {"error": f"AI error:{str(e)}"}

   
   return render_template(
      "dashboard.html",
      user=session["user"],
      result = result
   )


#HISTORY
@app.route("/history")
def history():
   if "user" not in session:
      flash("Login to see the History", "error")
      return redirect("/login")
   
   db = SessionLocal()
   user = db.query(models.User).filter_by(email=session["user"]).first()

   reports = db.query(models.Report).filter_by(user_id = user.id).all()

   #convert  JSON string > dict
   pasred_reports = []
   for r in reports:
      try:
         pasred_result = json.loads(r.result)
      except:
         pasred_result = []

      pasred_reports.append({
         "resume":r.resume_text,
         "result":pasred_result
      })

   return render_template("history.html", reports=pasred_reports)


#LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# FORGOT PASSWORD
@app.route("/forgot-password", methods = ["POST", "GET"])
def forgot_password():
   db = SessionLocal()

   if request.method == "POST":
      email = request.form.get("email")
      user = db.query(models.User).filter_by(email=email).first()

      if user:
         otp = random.randint(100000, 999999)

         session["otp"] = str(otp)
         session["reset_email"] = email

         try:
            sender_email = os.getenv("EMAIL")
            sender_password = os.getenv("EMAIL_PASSWORD")

            msg = MIMEText(f"""
            Hello,

            You requested a password reset for your AI Career Copilot account.

            Your One-Time Password (OTP) is: {otp}

            Please enter this OTP on the verification page to reset your password.

            This OTP is valid for a limited time. Do not share it with anyone.

            If you did not request a password reset, please ignore this email.

            Regards,
            AI Career Copilot Team
            """)

            msg["Subject"] = "Password Reset OTP"
            msg["From"] = sender_email
            msg["To"] = email

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()

            server.login(sender_email, sender_password)

            server.sendmail(
               sender_email,
               email,
               msg.as_string()
            )
            server.quit()

         except Exception as e:
            return f"Email error: {str(e)}"
         
         flash("OTP has been sent to your email.", "success")
         return redirect("/OTP-verification")
      
      else:
         return "Invalid email"

   return render_template("forgot_password.html")



# OTP Verification
@app.route("/OTP-verification", methods = ["POST", "GET"])
def OTP_verification():
   db = SessionLocal()

   if request.method == "POST":
      entered_otp = request.form.get("otp")

      if session["otp"] == entered_otp:
         flash("OTP verified successfully!", "success")
         return redirect("/reset-password")
      else:
         flash("Invalid OTP. Please try again.", "error")
         return redirect("/OTP-verificaton")
   
   return render_template("OTP_verification.html")


# RESET PASSWORD
@app.route("/reset-password", methods = ["POST", "GET"])
def reset_password():
   db = SessionLocal()

   if request.method == "POST":
      new_password = request.form.get("new_password")
      confirm_password = request.form.get("confirm_password")

      if new_password != confirm_password:
         return "Passwords do not match"
      
      else:
         user = db.query(models.User).filter_by(email=session["reset_email"]).first()
         user.password = new_password

         db.commit()

         session.pop("otp", None)
         session.pop("reset_email", None)

         flash("Password changed successfully. Please login.", "success")
         return redirect("/login")
   
   return render_template("reset_password.html")
      

if __name__ == "__main__":
   app.run(debug=True)




           


            


      
   

