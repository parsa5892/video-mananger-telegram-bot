import sys
sys.path.insert(1,'../')
import telebot
telebot.apihelper.ENABLE_MIDDLEWARE=True
import pickle
import cv2
from watermark.watemark import marking
from orm.ormvideo import session , User
import numpy as np
import os
from sqlalchemy.exc import IntegrityError



api='Your Api here'





#relation wit database

def newproduct(name):
    new_user = User(pname=name)
    session.add(new_user)
    session.commit()

def searchp(name):
    try:    
        query = session.query(User)
        query = query.filter(User.pname.contains(name))
        results = query.all()
        if results!=[]:
            return(results)
        else:
            return(False)
    except :
        return(False)
def howmedia(name,t):
        query = session.query(User)
        query = query.filter_by(pname=name).first()
        if t=='i':
            try:    
                lp=query.image
                return(len(lp.split(',')))
            except:
                return("0")
        elif t=='v':
            try:
                lp=query.video   
                return(len(lp.split(',')))
            except:
                return("0")
def updatep(name,t,*image):
        query = session.query(User)
        query = query.filter_by(pname=name).first()
        image=image[0]
        if t=='i':
            lp=query.image
            newimage=image['image']
            if lp==None:
                image=newimage
            else:
                image=lp+','+newimage
            query.image=image
        elif t=='v':
            lp=query.video
            newvideo=image['video']
            if lp==None:
                video=newvideo
            else:     
                video=lp+','+newvideo
            query.video=(video)
        session.commit()

def pnomedia():
        query = session.query(User)
        query = query.filter_by(image=None)
        results = query.all()
        return(results)

def pwithmedia():
     query=session.query(User)
     result=query.all()
     nomedia=pnomedia()
     result= set(result) - set(nomedia)
     return(result)

def productimage(name):
    try:    
        query = session.query(User)
        query = query.filter_by(pname=name).first()
        results = query.image
        results=results.split(',')
        
        return(results)
    except:
        return('هیچ عکسی برای این محصول ثبت نشده است')
def productvideo(name):
    try:
            query = session.query(User)
            query = query.filter_by(pname=name).first()
            results = query.video
            results=results.split(',')
            
            return(results)
    except:
            return('هیچ ویدیویی برای این محصول ثبت نشده است')
def searchbyid(idg):
    try:
            query = session.query(User)
            query = query.filter_by(id=idg).first()
            results = query.pname
            return(results)
    except:
            return(False)
     


onoroff='off'



#bot code from here






bot=telebot.TeleBot(api,parse_mode=None)



@bot.message_handler(commands=['setnewmedia'])
def newmedia(message):
    sent = bot.send_message(message.chat.id, 'لطفا اسم محصول مورد نظر را بفرستید ')
    bot.register_next_step_handler(sent,getname)


def getname(message):
    global name1
    name1=message.text
    a=searchp(message.text)
    if a==False:
        ae=bot.send_message(message.chat.id,'محصول مورد نظر وجود ندارد ایا میخواهید اضافه شود؟')
        bot.register_next_step_handler(ae, creatorno)
    else :
        namelist=[]
        ae=bot.send_message(message.chat.id,'لطفا از لیست زیر محصول را انتخاب کنید:\n')
        mess=''
        for i in a:
            namelist.append(i)
        for i in range(0,len(namelist),50):
            sub = namelist[i:i+50]
            for s in sub:
                simgn=(productimage(s.pname))
                svidn=(productvideo(s.pname))
                if type(simgn)==type([]):
                     simgn=len(simgn)
                else:
                     simgn=0

                if type(svidn)==type([]):
                     svidn=len(svidn)
                else:
                     svidn=0
                mess+=f'\n{s.pname} : /{s.id}   تعداد عکس ها:{simgn}    تعداد ویدیو ها:{svidn}'
            ae=bot.send_message(message.chat.id,str(mess))
            sub=[]
            mess=''
        bot.register_next_step_handler(ae, getitemname)

def getitemname(message):
        global name1
        a=message.text
        a=int(a[1:])
        name1=searchbyid(a)
        a=searchp(name1)
        if a==False:
            ae=bot.send_message(message.chat.id,'محصول مورد نظر وجود ندارد ایا میخواهید اضافه شود؟')
            bot.register_next_step_handler(ae, creatorno)
        else :
            ae=bot.send_message(message.chat.id,'لطفا فایل مورد نظر را ارسال کنید')
            bot.register_next_step_handler(ae, photo)
        

def creatorno(message):
        if message.text=="بله":
            newproduct(name1)
            bot.send_message(message.chat.id,'محصول اضافه شد')
        elif message.text=='نه':
            bot.send_message(message.chat.id,'محصول اضافه نشد')
        else:
            bot.send_message(message.chat.id,'  لطفا فرمان تعریف شده وارد کنید  (دوباره امتحان کنید) ')
        
    

def photo(message):
        i=0
        try:
            fileID = message.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)
            a=howmedia(name1,'i')
            path=f"../media/img/{name1+str(a)}.jpg"
            with open(path, 'wb') as new_file:
                new_file.write(downloaded_file)
            if onoroff=='on':
                marking(input_image_path=path)
            updatep(name1,'i',{'image':path})
            bot.send_photo(message.chat.id,photo=open(path, 'rb'),timeout=10000)
            bot.send_message(message.chat.id,'عکس با موفقیت ثبت شد')
        except:
            pass
        try:
            fileID = message.video.file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)
            a=howmedia(name1,'v')
            path=f"../media/video/{name1+str(a)}.mp4"
            with open(path, 'wb') as new_file:
                new_file.write(downloaded_file)
            updatep(name1,'v',{'video':path})
            bot.send_message(message.chat.id,'ویدیو با موفقیت ثبت شد')
        except:
            pass
        i+=1


@bot.message_handler(commands=['pwithmedia'])
def rpwithimage(message):
    namelist=[]
    mess=''
    a=pwithmedia()
    for i in a:
        namelist.append(i.pname)
    for i in range(0,len(namelist),40):
        sub = namelist[i:i+40]
        for s in sub:
             mess+=f'\n{s}'
             
        bot.send_message(message.chat.id,((mess)))
        mess=''


@bot.message_handler(commands=['pwithnomedia'])
def rpwithimage(message):
    namelist=[]
    mess=''
    a=pnomedia()
    for i in a:
        namelist.append(i.pname)
    for i in range(0,len(namelist),40):
        sub = namelist[i:i+40]
        for s in sub:
             mess+=f'\n{s}'
             
        bot.send_message(message.chat.id,((mess)))
        mess=''



@bot.message_handler(commands=['changefooter'])
def changefooter(message):
    sent = bot.send_message(message.chat.id, 'لطفا فوتر مورد نظر را بفرستید ')
    bot.register_next_step_handler(sent,getfooter)


def getfooter(message):
            fileID = message.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)

            with open('../watermark/img/footer.png', 'wb') as new_file:
                new_file.write(downloaded_file)


@bot.message_handler(commands=['changeheader'])
def changefooter(message):
    sent = bot.send_message(message.chat.id, 'لطفا هدر  مورد نظر را بفرستید ')
    bot.register_next_step_handler(sent,getheader)


def getheader(message):
            fileID = message.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)

            with open('../watermark/img/header.png', 'wb') as new_file:
                new_file.write(downloaded_file)


@bot.message_handler(commands=['changewater'])
def changewater(message):
    sent = bot.send_message(message.chat.id, 'لطفا واترمارک مورد نظر را بفرستید ')
    bot.register_next_step_handler(sent,getwater)


def getwater(message):
            fileID = message.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)

            with open('../watermark/img/mark.png', 'wb') as new_file:
                new_file.write(downloaded_file)


@bot.message_handler(commands=['getproductmedia'])
def getproductmedia(message):
    sent = bot.send_message(message.chat.id, 'لطفا اسم محصول مورد نظر را بفرستید ')
    bot.register_next_step_handler(sent,getname2)

def getname2(message):
    chatid=message.chat.id
    a=searchp(message.text)
    if a==False:
        ae=bot.send_message(message.chat.id,'محصول مورد نظر وجود ندارد ایا میخواهید اضافه شود؟')
        bot.register_next_step_handler(ae, creatorno)
    else :
        ae=bot.send_message(message.chat.id,'لطفا از لیست زیر محصول را انتخاب کنید:\n')
        
        namelist=[]
        mess=''
        for i in a:
            namelist.append(i)
        for i in range(0,len(namelist),50):
            sub = namelist[i:i+50]
            for s in sub:
                simgn=(productimage(s.pname))
                svidn=(productvideo(s.pname))
                if type(simgn)==type([]):
                     simgn=len(simgn)
                else:
                     simgn=0

                if type(svidn)==type([]):
                     svidn=len(svidn)
                else:
                     svidn=0
                mess+=f'\n{s.pname} : /{s.id}   تعداد عکس ها:{simgn}    تعداد ویدیو ها:{svidn}'
            
            ae=bot.send_message(chatid,str(mess))
            sub=[]
            mess=''
        bot.register_next_step_handler(ae, getitemname2)
def getitemname2(message):
        global name2
        a=message.text
        a=int(a[1:])
        name2=searchbyid(a)
        a=searchp(name2)
        if a==False:
            ae=bot.send_message(message.chat.id,'محصول در دیتابیس وجود ندارد')
        else :
            ae=bot.send_message(message.chat.id,'در حال لود کردن رسانه \n لطفا منتظر بمانید')
            sendmedia(message)

def sendmedia(message):
    try:
        a=productimage(name2)
        bot.send_message(message.chat.id,'عکس ها:')
        for i in a:
            bot.send_message(message.chat.id,'...درحال اپلود عکس')
            bot.send_photo(message.chat.id,photo=open(i, 'rb'),timeout=10000)
    except:
        bot.send_message(message.chat.id,'هیچ عکسی ثبت نشده')
    try:
        a=productvideo(name2)
        bot.send_message(message.chat.id,'ویدیو ها:')
        for i in a:
            bot.send_message(message.chat.id,'...درحال اپلود ویدیو')
            bot.send_video(message.chat.id,video=open(i, 'rb'),supports_streaming=True,timeout=100000)
            
    except:
        bot.send_message(message.chat.id,'هیچ ویدیویی ثبت نشده')


@bot.message_handler(commands=['off'])
def geton(message):
    global onoroff
    onorof='off'  
@bot.message_handler(commands=['on'])
def geton(message):
    global onoroff
    onorof='on'           
if __name__ == '__main__':
    while True:
        bot.infinity_polling()