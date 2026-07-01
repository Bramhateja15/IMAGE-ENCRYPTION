from django.shortcuts import render, redirect
from . models import *
# Create your views here.
from django.contrib import messages
# from tensorflow.keras.models import load_model
import imutils, pickle
import numpy as np
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
# from tensorflow.keras.preprocessing.image import img_to_array
from sklearn.preprocessing import LabelEncoder
from django.db.models import Q
import cv2
import os
import uuid
from PIL import Image
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')


def register(request):
    # UserModel.objects.all().delete()
    # UploadFileModel.objects.all().delete()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            if UserModel.objects.filter(Q(email=email) | Q(username=username)).exists():
                messages.error(request, 'Email or User Name already exists')
                return redirect('register')
            
            # Capture live images from webcam
            cam = cv2.VideoCapture(0)
            harcascadePath = "Haarcascade/haarcascade_frontalface_default.xml"
            detector = cv2.CascadeClassifier(harcascadePath)
            sampleNum = 0
            # folder_path = os.path.join('IndentorImages', email)
            # os.makedirs(folder_path, exist_ok=True)

            while True:
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    sampleNum += 1
                    # Save captured face images
                    cv2.imwrite("UserImages/ " +username + '.' +str(sampleNum) + ".jpg",
                            gray[y:y + h, x:x + w])

                cv2.imshow('frame', img)

                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                elif sampleNum >= 350:  # Stop after capturing 50 images
                    break

            cam.release()
            cv2.destroyAllWindows()
            user = UserModel.objects.create(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'User created successfully')
            return redirect('training')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')    
    return render(request, 'register.html')



def training(request):
    le = LabelEncoder()
    faces, Id = getImagesAndLabels("UserImages")
    Id=le.fit_transform(Id)
    output = open('model/encoder.pkl', 'wb')
    pickle.dump(le, output)
    output.close()
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(Id))
    recognizer.save(r"model\Trainner.yml")
    messages.success(request, 'Your model has been trained successfully!!')
    return redirect('login')

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        Id = str(os.path.split(imagePath)[-1].split(".")[0])
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids


# def detect_and_predict_person(img, faceNet, model):
# 	(h, w) = img.shape[:2]
# 	blob = cv2.dnn.blobFromImage(img, 1.0, (224, 224),(104.0, 177.0, 123.0))
# 	faceNet.setInput(blob)
# 	detections = faceNet.forward()
# 	print(detections.shape)
# 	faces = []
# 	locs = []
# 	preds = []
# 	for i in range(0, detections.shape[2]):
# 		confidence = detections[0, 0, i, 2]
# 		if confidence > 0.5:
# 			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
# 			(startX, startY, endX, endY) = box.astype("int")
# 			(startX, startY) = (max(0, startX), max(0, startY))
# 			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))
# 			face = img[startY:endY, startX:endX]
# 			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
# 			face = cv2.resize(face, (32, 32))
# 			face = img_to_array(face)
# 			face = preprocess_input(face)
# 			faces.append(face)
# 			locs.append((startX, startY, endX, endY))

# 	if len(faces) > 0:
# 		faces = np.array(faces, dtype="float32")
# 		preds = model.predict(faces, batch_size=32)
# 	return (locs, preds)

import cv2
import pickle
import imutils
from django.shortcuts import render, redirect
from django.contrib import messages

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        meth = request.POST['auth_method']
        if meth == 'password':
            password = request.POST['password']

        # Check if user credentials are valid
            if UserModel.objects.filter(email=email, password=password).exists():
                request.session['email'] = email
                return redirect('home')

            else:
                messages.error(request, 'Invalid Email or Password!')
                return redirect('login')
        else:
            if UserModel.objects.filter(email=email).exists():
                
                face_model = "model/Trainner.yml"
                cam = cv2.VideoCapture(0)
                
                # Check if the camera is available
                if not cam.isOpened():
                    messages.error(request, "Error: Could not access the camera.")
                    return render(request, 'login.html')

                harcascadePath = "Haarcascade/haarcascade_frontalface_default.xml"
                detector = cv2.CascadeClassifier(harcascadePath)
                font = cv2.FONT_HERSHEY_SIMPLEX 

                # Load the encoder file
                pkl_file = open('model/encoder.pkl', 'rb')
                le = pickle.load(pkl_file)
                pkl_file.close()

                det = 0  # Count the number of detected faces
                face_not_matched = False  # Flag to check if face is not matched
                while True:
                    ret, img = cam.read()
                    if not ret:
                        print("Failed to capture image")
                        break

                    img = imutils.resize(img, width=1000)  # Resize image for better processing
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale for face detection
                    faces = detector.detectMultiScale(gray, 1.2, 5)  # Detect faces

                    # Loop through detected faces
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (225, 0, 0), 2)  # Draw rectangle around face
                        
                        # Create the LBPH recognizer and load the trained model
                        recognizer = cv2.face.LBPHFaceRecognizer_create()
                        recognizer.read(face_model)
                        
                        Id, conf = recognizer.predict(gray[y:y + h, x:x + w])  # Predict the ID of the face
                        print(conf)  # Output the confidence

                        # Check if the confidence is above a threshold
                        if conf > 30 and conf < 45:
                            tt = le.inverse_transform([Id])
                            tt = tt[0]
                            det += 1
                            if det == 3:  # If face is detected 3 times, log in the user
                                request.session['email'] = email
                                cam.release()
                                cv2.destroyAllWindows()
                                return redirect('home')  # Redirect to home page after successful login
                        else:
                            tt = "Face Not Matched"
                            face_not_matched = True  # Set flag if face is not matched
                            
                        cv2.putText(img, str(tt), (x, y + h), font, 1, (255, 255, 255), 2)  # Display recognized name

                    # Show the image with the face and name
                    cv2.imshow("Frame", img)

                    # Break the loop if 'q' is pressed
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                cam.release()  # Release the camera
                cv2.destroyAllWindows()  # Close the OpenCV window

                # If face was not matched, show a message to the user
                if face_not_matched:
                    messages.error(request, "Face not matched. Please try again.")
                    return redirect('login')  # Redirect to login page

            # Redirect back to the login page if credentials are incorrect

    return render(request, 'login.html')

import random
from django.core.mail import send_mail
def forgotpass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if UserModel.objects.filter(email=email).exists():
            user = UserModel.objects.get(email=email)
            
            otp = random.randint(10000,99999)
            user.otp = otp
            user.save()
            email_subject = 'Reset Passward Details'
            email_message = f'Hello {email},\n\nWelcome To Our Website!\n\nHere are your OTP details:\nEmail: {email}\OTP: {otp}\n\nPlease keep this information safe.\n\nBest regards,\nYour Website Team'
            from_email = 'cse.takeoff@gmail.com'
            send_mail(email_subject, email_message, from_email, [email])
            messages.success(request, 'OTP sent successfully')
            return redirect('resetpassword')
        else:
            messages.error(request, 'Invalid email!')
            return redirect('forgotpass')


    return render(request, 'forgotpass.html')


def resetpassword(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        if UserModel.objects.filter(otp=otp, email=email).exists():
            user = UserModel.objects.get(email=email)
            if password == confirm_password:
                user.password = password
                user.save()
                messages.success(request, 'Password reset successfully')
                return redirect('login')
            else:
                messages.error(request, 'Password and confirm password does not match!')
                return redirect('resetpassword')
        else:
            messages.error(request, 'Invalid OTP!')
            return redirect('resetpassword')
    return render(request, 'resetpassword.html')



def home(request):
     email =request.session['email']
    #  print(email)
     return render(request, 'home.html',{'email':email})



import os
import uuid
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import  UserModel  # Import your models


import hashlib

def hash_string(content):
    """Generate a hash for the file content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
import os
import uuid
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from .models import EncryptedImage, UserModel
from .crypto_utils import *
import secrets
from io import BytesIO

def uploadfiles(request):
    # EncryptedImage.objects.all().delete()
    # RequestFileModel.objects.all().delete()

    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        original_filename = uploaded_file.name
        extension = os.path.splitext(original_filename)[1].lower()

        if extension not in ['.jpg', '.jpeg', '.png']:
            messages.error(request, "Only .jpg, .jpeg, or .png files are allowed.")
            return redirect('uploadfiles')

        unique_filename = f"{os.path.splitext(original_filename)[0]}_" \
                          f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{extension}"

        file_path = os.path.join(settings.BASE_DIR, 'static/assets/Files', unique_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb+') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        privKey = secrets.randbelow(curve.field.n)
        pubKey = privKey * curve.g

        encrypted_data, iv, encrypted_key, c1, img_size = encrypt_image(file_path, pubKey)
        with open(file_path, 'wb+') as f:
            f.write(encrypted_data)
        try:
            user = UserModel.objects.get(email=request.session['email'])
        except UserModel.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('uploadfiles')

        encrypted_img = EncryptedImage(
            user=user,
            name=unique_filename,
            encrypted_data=encrypted_data,
            iv=iv,
            c1=c1,
            encrypted_key=encrypted_key,
            width=img_size[0],
            height=img_size[1],
        )
        encrypted_img.save()

        # Save private key in session (not DB)
        request.session[f'priv_{encrypted_img.id}'] = str(privKey)

        messages.success(request, f"File '{original_filename}' uploaded and encrypted successfully.")
        return redirect('uploadfiles')

    return render(request, 'uploadfiles.html')


def decrypt(request, id):
    file = EncryptedImage.objects.get(id=id)
    privKey_str = request.session.get(f'priv_{file.id}', None)

    if not privKey_str:
        return HttpResponse("Private key not found in session. Cannot decrypt.", status=403)

    privKey = int(privKey_str)

    try:
        image = decrypt_image(
            file.encrypted_data,
            file.iv,
            file.encrypted_key,
            file.c1,
            (file.width, file.height),
            privKey
        )

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="decrypted_{file.name}"'
        return response

    except ValueError as e:
        return HttpResponse(f"Decryption failed: {str(e)}", status=400)



def viewfiles(request):
    # UploadFileModel.objects.all().delete()
    email = request.session['email']
    files = EncryptedImage.objects.all()
    paginator = Paginator(files, 4)  
    page_number = request.GET.get('page')
    page_data = paginator.get_page(page_number)
    return render(request, 'viewfiles.html', {'data':page_data, 'email':email})





# def decrypt(request, id):

#     file = EncryptedImage.objects.get(id=id)
#     # Decrypt the image data
#     data = decrypt_image(file.encrypted_data, file.iv, file.encrypted_key, file.c1,(file.height,file.width), int(file.priv) )
#     print(data)

        
    



def logout(request):
    del request.session['email']
    return redirect('index')


def profile(request):
    # UserProfile.objects.all().delete()
    email =  request.session['email']
    user = UserModel.objects.get(email=email)
    data = UserProfile.objects.filter(user_id=user.id).exists()
    if data:
        profile = UserProfile.objects.filter(user_id=user.id)

        user = UserModel.objects.filter(email=email)
        return render(request, 'profile.html', {'profile': profile,'user': user})
    else:
        userdata = UserModel.objects.filter(email=email)

        return render(request, 'updateprofile.html',{'user':userdata})
    
    # return render(request, 'profile.html')

def updateprofile(request):
    email =  request.session['email']
    user = UserModel.objects.get(email=email)
    if request.method == 'POST':
        # name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('location')
        bio = request.POST['bio']
        image = request.FILES['image']
        data = UserProfile.objects.create(
            user_id=user.id,
           
            phone=phone,
            address=address,
            bio=bio,
            image=image 
        
        )
        data.save()
        return redirect('profile')

def editprofile(request):
    # UserProfile.objects.filter(id=4).delete()
    email =  request.session['email']
    user = UserModel.objects.get(email=email)
    profile = UserModel.objects.filter(email=email)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        address = request.POST.get('location')
        bio = request.POST['bio']
        image = request.FILES['image']
        data = UserProfile.objects.get(user_id=user.id)
        if phone:
            data.phone = phone
        if address :
            data.address = address
        data.bio = bio
        if image:
            data.image = image
        data.save()
        messages.success(request, 'Profile Updated Successfully!')
        return redirect('profile')
    return render(request, 'editprofile.html',{'user':profile})


def sendrequest(request, id):
    requester = request.session['email']
    data = EncryptedImage.objects.get(id=id)
    if RequestFileModel.objects.filter(requester=requester, file_id=data).exists():
        messages.success(request, 'You already requested this file')
        return redirect('viewfiles')
    else:
        req = RequestFileModel.objects.create(
            file_id = data,
            requester = requester
        )
        req.save()
        messages.success(request, 'Request Sent Successfully!')
        return redirect('viewfiles')

        

def viewrequests(request):
    email =  request.session['email']
    # user = UserModel.objects.get(email=email)
    requests = RequestFileModel.objects.filter(file_id__user__email=email, status='Pending')
    paginator = Paginator(requests, 4)  
    page_number = request.GET.get('page')
    page_data = paginator.get_page(page_number)
    return render(request, 'viewrequests.html', {'data':page_data, 'email':email})


import random
def acceptrequest(request, id):
    email = request.session['email']
    req = RequestFileModel.objects.get(id=id)
    req.status = 'Accepted'
   
    req.save()
    email_subject = 'File Request Details'
    email_message = f'Hello {req.requester},\n\nWelcome To Our Website!\n\nHere are your File Request details:\nEmail: {req.requester}\nStatus: Accepted\n\nPlease keep this information safe.\n\nBest regards,\nYour Website Team'
    send_mail(email_subject, email_message, 'cse.takeoff@gmail.com', [req.requester])
    messages.success(request, 'Request Accepted Successfully!')
    return redirect('viewrequests')

def rejectrequest(request, id):
    email = request.session['email']
    req = RequestFileModel.objects.get(id=id)
    req.status = 'Rejected'
    req.save()
    email_subject = 'File Request Details'
    email_message = f'Hello {req.requester},\n\nWelcome To Our Website!\n\nHere are your File Request details:\nEmail: {req.requester}\nStatus: Rejected\n\nPlease keep this information safe.\n\nBest regards,\nYour Website Team'
    send_mail(email_subject, email_message, 'cse.takeoff@gmail.com', [req.requester])
    messages.success(request, 'Request Rejected Successfully!')
    return redirect('viewrequests')



def viewresponses(request):
    email =  request.session['email']
    responses = RequestFileModel.objects.filter(requester=email, status='Accepted')
    paginator = Paginator(responses, 4)
    page_number = request.GET.get('page')
    page_data = paginator.get_page(page_number)
    return render(request, 'viewresponses.html',{'data':page_data, 'email':email})


def download(request, id):
    if request.method == 'POST':
        otp1 = request.POST['otp1']
        otp2 = request.POST['otp2']
        otp3 = request.POST['otp3']
        otp4 = request.POST['otp4']
        otp5 = request.POST['otp5']
        otp6 = request.POST['otp6']
        otp = int(otp1+otp2+otp3+otp4+otp5+otp6)
        req = RequestFileModel.objects.get(id=id)
        if req.otp == otp:
            return redirect('decrypt', req.file_id.id)
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('download', id)
    req = RequestFileModel.objects.get(id=id)
    req.status = 'Accepted'
    otp = random.randint(100000, 999999)
    req.otp = otp
    req.save()
    email_subject = 'File Request Details'
    email_message = f'Hello {req.requester},\n\nWelcome To Our Website!\n\nHere are your Key details:\nEmail: {req.requester}\nKey: {otp}\n\nPlease keep this information safe.\n\nBest regards,\nYour Website Team'
    send_mail(email_subject, email_message, 'cse.takeoff@gmail.com', [req.requester])
    messages.success(request, 'Otp Sent Successfully!')
    
    return render(request, 'download.html',{ 'id':id})


def delete(request, id):
    req = EncryptedImage.objects.get(id=id)
    req.delete()
    messages.success(request, 'File Deleted Successfully!')
    return redirect('viewfiles')



