from flask import Flask, render_template, url_for, session, redirect, request, Response, flash
from flask_pymongo import PyMongo, ObjectId

import gridfs
import bcrypt
import ssl
import os
import math

app = Flask(__name__)

uploads_dir = os.getcwd()+'/static/img'

app.config["IMAGE_UPLOADS"] = uploads_dir
app.config['MONGO_DBNAME'] = 'cookmeasure'
app.config['SECRET_KEY'] = 'cookrecetas'
app.config['MONGO_URI'] = 'mongodb+srv://admin:utp123@cluster0-tjpda.mongodb.net/cookmeasure?retryWrites=true&w=majority'

mongo = PyMongo(app)
fs = gridfs.GridFS(mongo.db)

@app.route('/pwabuilder-sw.js', methods=['GET'])
def sw():
    return send_from_directory('static/js','pwabuilder-sw.js')

@app.route('/',methods=['POST','GET'])
def index():
    #if 'email' in session:
     #   return render_template('home.html')    
    return render_template('index.html')

@app.route('/home',methods=['POST','GET'])
def home():
    users = mongo.db.users
    recetas = mongo.db.recetas
    #if 'email' in session:
    #    user = users.find_one({'email':session['email']})
    #    return render_template('home.html',user=user)    
    return render_template('index.html')

@app.route('/admin',methods=['GET','POST'])
def admin():
    recetas = mongo.db.recetas
    if request.method == 'POST':
        imgs = {}
        c = 0
        for i in request.files.getlist('images'):
            a = fs.put(i, content_type = i.content_type, filename = i.filename)
            imgs[str(c)]=i.filename
            c += 1
            print('* ',i)
        new_receta = {'usuario':request.form['usuario'],
                    'title':request.form['title'],
                    'tiempo':request.form['tiempo'],
                    'description':request.form['description'],
                    #'ingredientes':request.form['ingredientes'],
                    'preparacion':request.form['preparacion'],
                    'link':request.form['link'],'images':imgs}
        _id = recetas.insert_one(new_receta)
        return redirect('recetas')
    else:
        return render_template('admin.html',recetas=mongo.db.recetas.find())

@app.route('/images/<filename>')
def image(filename):
    gridout = fs.find_one({'filename':filename})
    Response.content_type = 'image/jpeg'
    g = gridout.read()
    return g

@app.route('/delete/<item>')
def delete(item):
    recetas = mongo.db.recetas
    user = mongo.db.users
    fsf = mongo.db.fs.files
    fsc = mongo.db.fs.chunks
    target = recetas.find_one({'_id':ObjectId(item)})
    for i in target['images']:
        obj = fsf.find_one({'filename':target['images'][i]})
        fsf.find_one_and_delete({'filename':target['images'][i]})
        fsc.delete_many({'files_id':obj['_id']})
    target = recetas.find_one_and_delete({'_id':ObjectId(item)})
    if user.email == 'administrador@cookmeasure.com':
        return redirect(url_for('recetas'))
    else:
        return redirect(url_for('misrecetas'))

@app.route('/recetas')
def recetas():
    recetas = mongo.db.recetas
    return render_template('receta.html',recetas=recetas.find())

@app.route('/recetas/<receta>')
def receta1(receta):
    recetas = mongo.db.recetas
    target = recetas.find_one({'_id':ObjectId(receta)})
    return render_template('recetas.html',receta=target)

@app.route('/misrecetas')
def misrecetas():
    recetas = mongo.db.recetas
    return render_template('misrecetas.html', recetas=recetas.find())

@app.route('/modificar/<receta>', methods=['GET','POST'])
def modificar(receta):
    recetas = mongo.db.recetas
    user = mongo.db.users
    fsf = mongo.db.fs.files
    fsc = mongo.db.fs.chunks
    target = recetas.find_one({'_id':ObjectId(receta)})
    if request.method == 'POST':
        target = recetas.find_one({'_id':ObjectId(receta)})
        imgs = {}
        c = 0
        for i in request.files.getlist('images'):
            a = fs.put(i, content_type = i.content_type, filename = i.filename)
            imgs[str(c)]=i.filename
            c += 1
            print('* ',i)
        update_receta = recetas.update_one(target,
            {
                '$set':{'usuario':request.form['usuario'],
                    'title':request.form['title'],
                    'tiempo':request.form['tiempo'],
                    'description':request.form['description'],
                    #'ingredientes':request.form['ingredientes'],
                    'preparacion':request.form['preparacion'],
                    'link':request.form['link'],'images':imgs}
            }
        )
        return redirect(url_for('misrecetas'))
    else:
        return render_template('modificar.html', receta=target)

@app.route('/signup',methods=['POST'])
def signup():
    users = mongo.db.users
    used = users.find_one({'email':request.form['remail']})
    if used:
        flash(u'El correo ingresado ya se encuentra en uso')
        return redirect(url_for('index'))
    if request.form['rpass'] != request.form['rpass2']:
        flash(u'Las contraseñas no coinciden.')
        return redirect(url_for('index'))
    password = request.form['rpass']
    password2 = request.form['rpass2']
    hashpass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    new_user = { 'nickname':request.form['nickname'], 'email':request.form['remail'],'name':request.form['rname'], 'password':hashpass }
    users.insert_one(new_user)
    session['email'] = request.form['remail']
    session['nickname'] = request.form['nickname']
    print('Usuario creado')
    return redirect(url_for('home'))

@app.route('/login',methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email': request.form['email']})
    if login_user is not None:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['email'] = request.form['email']
            return redirect(url_for('home'))
        else:
            flash('Datos incorrectos')
            return redirect(url_for('logint'))
    else:
        flash('El correo no existe en CookMeasure')
        return redirect(url_for('logint'))

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect(url_for('index'))

@app.route('/logint')
def logint():
    return render_template('login.html')


if __name__ == '__main__':
    app.secret_key = 'mykey'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)