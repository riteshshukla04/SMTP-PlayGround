
from django.http import response
from django.shortcuts import render,HttpResponse,redirect
import email, smtplib, ssl
from django.views.decorators.csrf import csrf_exempt
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import send_mail, EmailMessage
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from django.contrib.auth import authenticate,login,logout
from cryptography.fernet import Fernet
from background_task import background

from stmpplayground.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, SECRET_KEY

l=[]
def generate_key():
 
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
  
    return "iL_ogqlZVQEM4F4-v_hgcFJyFHjR_I6iVc4jg11Tqhs="

def encrypt_message(message):
 
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return (encrypted_message)


def decrypt_message(encrypted_message):
    
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return (decrypted_message.decode())




def index(request):                    
    
    if request.method == 'POST':
        email=request.POST.get("email")
        subject=request.POST.get("subject")
        text=request.POST.get("content")
        encMessage =encrypt_message(text)
        print(encMessage)
        try:
            file=request.FILES['files']
            if file!=None:

                print(email,subject,text,file)
                
                print(encMessage)
                mail = EmailMessage(subject, (encMessage.decode('utf8')), 'testforritesh@gmail.com', [email])
                mail.attach(file.name, file.read(), file.content_type)
                mail.send()
            else:
                mail = EmailMessage(subject, encMessage.decode('utf8'), 'testforritesh@gmail.com', [email])
                mail.send()
        except:
            mail = EmailMessage(subject, encMessage.decode('utf8'), 'testforritesh@gmail.com', [email])
            
            mail.send()
    
                
   
    return render(request,"index.html")


@api_view(["POST"])
def indexapi(request):
    
    json_data = json.loads(str(request.body, encoding='utf-8'))
    email=json_data["email"]
    subject=json_data["subject"]
    text=json_data["content"]
    encMessage =encrypt_message(text)
    mail = EmailMessage(subject, encMessage.decode('utf8'), 'testforritesh@gmail.com', [email])
  
    mail.send() 
    
    
                
   
    return Response("DONE")


def inbox(request):
    import imaplib
    import email
    
    username =EMAIL_HOST_USER

    app_password= EMAIL_HOST_PASSWORD
    gmail_host= 'imap.gmail.com'
    mail = imaplib.IMAP4_SSL(gmail_host)
    mail.login(username, app_password)
    mail.select("INBOX")
    _, selected_mails = mail.search(None, 'ALL')
    i=0
    l=[]
    
    for num in selected_mails[0].split():
        _, data = mail.fetch(num , '(RFC822)')
        _, bytes_data = data[0]

        #convert the byte data to message
        email_message = email.message_from_bytes(bytes_data)
        #print("\n===========================================")

        #access data
        #print("Subject: ",email_message["subject"])
        #print("To:", email_message["to"])
        #print("From: ",email_message["from"])
        #print("Date: ",email_message["date"])
        m={"subject":email_message["subject"],"from":email_message["from"],"date":email_message["date"]}
        for part in email_message.walk():
            if part.get_content_type()=="text/plain" or part.get_content_type()=="text/html":
                message = part.get_payload(decode=True)
                #print("Message: \n", message.decode())
                #print("==========================================\n")
                s=message.decode()
                
                res = bytes(s, 'utf-8')
                try:
                    m["message"]=(decrypt_message(res))
                    l+=[m]
                except:
                    pass
                break
                
        
        
        i+=1
    return render(request,"inbox.html",{"l":l})
    

def excelMails(request):
    if request.method=="POST":
        try:
            import smtplib
            import pandas
            username =EMAIL_HOST_USER

            app_password= EMAIL_HOST_PASSWORD
            file=request.FILES['files']
            print(file)
            dataframe=pandas.read_csv(file)
            s = smtplib.SMTP('smtp.gmail.com', 587)
            text=request.POST.get("content")
            s.starttls()
            s.login(username,app_password)
            
            for i in range(len(dataframe)):


                message=f"Subject: DCN Recruitment\nHello {dataframe['NAME'][i]},\n\n{str(text)}."
                s.sendmail("#email",dataframe['EMAIL'][i], message.encode('utf-8'))
                
            s.quit()
        except:
            return HttpResponse("Something went Wrong")
    return render(request,"schedulemails.html")

@background(schedule=10)
def sendmail(email,subject,text,time):
    time==""
    mail = EmailMessage(subject, text, 'testforritesh@gmail.com', [email])
    mail.send()



def ScheduleMails(request):
    if request.method == 'POST':
        email=request.POST.get("email")
        subject=request.POST.get("subject")
        text=request.POST.get("content")
        time=request.POST['birthdaytime']
        
       
    
                
   
    
    return render(request,"Schedule Mails.html")

@api_view(["POST"])
def inboxapi(request):
    import imaplib
    import email
    username =EMAIL_HOST_USER
    app_password= EMAIL_HOST_PASSWORD
    gmail_host= 'imap.gmail.com'
    mail = imaplib.IMAP4_SSL(gmail_host)
    mail.login(username, app_password)
    mail.select("INBOX")
    _, selected_mails = mail.search(None, 'ALL')
    i=0
    l=[]
    
    for num in selected_mails[0].split():
        _, data = mail.fetch(num , '(RFC822)')
        _, bytes_data = data[0]

        email_message = email.message_from_bytes(bytes_data)

        m={"subject":email_message["subject"],"from":email_message["from"],"date":email_message["date"]}
        for part in email_message.walk():
            if part.get_content_type()=="text/plain" or part.get_content_type()=="text/html":
                message = part.get_payload(decode=True)
                s=message.decode()
                
                res = bytes(s, 'utf-8')
                m["message"]=(decrypt_message(res))
                l+=[m]
                
                break
                
        
        
        i+=1
    return Response((l))

from django.contrib import messages
@csrf_exempt
def Login(request):
    context={}
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        user=authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            return redirect("/")
        else:
           messages.info(request,"Username or password incorrect")             
     
    return render(request,'login2.html',context)