from flask import Flask, render_template, request, Response, redirect
import cv2
import easyocr
from googletrans import Translator

app = Flask(__name__)
global switch, capture, new, acc, lang
lang='en'
new=''
switch = 0
capture = 0
acc=0
camera = None

def convert(img1, lang):
    global new, acc
    new=''
    reader = easyocr.Reader([lang])
    result = reader.readtext(img1)

    for i in range(len(result)):
        new+=str(result[i][1]) + ' '

    acc = 0
    for i in range(len(result)):
        acc+=result[i][2]
    acc = round(100*acc/len(result),2)

    return new, acc

def generate():
    global camera, capture, new, acc, lang
    # lang = 'en'
    # new = ''
    # acc = 0
    while True:
        ret, frame = camera.read()

        if ret:
            (flag, encodedImage) = cv2.imencode('.jpg', cv2.flip(frame,1))
            if not flag:
                break
            if(capture):
                capture=0
                cv2.imwrite('static/file2.jpg',frame)

                img1 = cv2.imread('static/file2.jpg')
                
                new, acc = convert(img1, lang)
            
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                bytearray(encodedImage) + b'\r\n')
        else:
            break

@app.route('/', methods=['GET', 'POST'])
def index():
    global acc, new, switch, camera, capture
    new=''
    switch = 0
    capture = 0
    acc=0
    if request.method == 'GET':
        return render_template('index.html', data=new, acc=acc, text=new)
    if request.method == 'POST':
        if request.files:
            img = request.files['file1']
            lang = request.form['cars']
            
            img.save('static/file.jpg')
            img1 = cv2.imread('static/file.jpg')
            
            new, acc = convert(img1,lang)

            if acc > 50:
                    return render_template('index.html',text=new, data=new, acc=acc)
            else:
                return render_template('index.html', data='', acc="select the correct language")
        # elif request.form.get('stop') == 'Stop/Start':
                
        #     if(switch==1):
        #         switch=0
        #         camera.release()
        #         cv2.destroyAllWindows()
        #         return redirect('/')
                
        #     else:
        #         camera = cv2.VideoCapture(0)
        #         switch=1
        #         return redirect('/')

        # elif request.form.get('click') == 'Capture':
        #     lang = request.form['language']
        #     capture=1
        #     return render_template('index.html', data=new, acc=acc, text=new)
        elif request.form.get('Clear') == 'Clear':
            return redirect('/')
        else:
            tran = request.form ['text']
            lang = request.form ['trans']
            translater = Translator()
            translated = translater.translate(tran,dest=lang)
            return render_template('index.html', translated=translated.text, data=tran) 

@app.route('/request',methods=['POST','GET'])
def tasks():
    global switch, camera
    if request.method == 'GET':
        return render_template('image.html')
    elif request.method == 'POST':
        if request.form.get('stop') == 'Stop/Start':
                
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                return redirect('/')
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1
                return redirect('/request')

        if request.form.get('click') == 'Capture':
            global capture, lang
            lang = request.form['language']
            capture=1
            return redirect('/request')

@app.route('/video')
def video():
    return Response(generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run()