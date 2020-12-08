from flask import Flask, render_template, url_for, session, redirect, request, Response, flash
from flask_pymongo import PyMongo, ObjectId

import gridfs
import bcrypt
import ssl
import os
import math
import sys

app = Flask(__name__)

uploads_dir = os.getcwd()+'/static/img'

app.config["IMAGE_UPLOADS"] = uploads_dir
app.config['MONGO_DBNAME'] = 'cookmeasure'
app.config['SECRET_KEY'] = 'cookrecetas'
app.config['MONGO_URI'] = 'mongodb+srv://admin:utp123@cluster0-tjpda.mongodb.net/cookmeasure?retryWrites=true&w=majority'

mongo = PyMongo(app)
fs = gridfs.GridFS(mongo.db)

@staticmethod
def all_paginated(page=1, per_page=8):
    return Post.query.order_by(Post.created.asc()).\
        paginate(page=page, per_page=per_page, error_out=False)

#@app.route('/pwabuilder-sw.js', methods=['GET'])
#def sw():
#    return send_from_directory('static/js','pwabuilder-sw.js')

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
        separar_ing = request.form['ingredientes'].split(', ')
        new_receta = {'usuario':request.form['usuario'],
                    'title':request.form['title'],
                    'tiempo':request.form['tiempo'],
                    'description':request.form['description'],
                    'ingredientes':separar_ing,
                    'preparacion':request.form['preparacion'],
                    'link':request.form['link'],'images':imgs}
        _id = recetas.insert_one(new_receta)
        print (new_receta)
        return redirect('recetas')
    else:
        return render_template('admin.html',recetas=mongo.db.recetas.find())

@app.route('/comentar',methods=['GET','POST'])
def comentar():
    comentarios = mongo.db.comentarios
    recetas = mongo.db.recetas
    id = request.form['receta']
    if request.method == 'POST':
        comentario = {'usuario':request.form['usuario'],
                    'receta':request.form['receta'],
                    'comentario':request.form['comentario']
                    }
        _id = comentarios.insert_one(comentario)
    target = recetas.find_one({'_id':ObjectId(id)})
    return render_template('recetas.html',receta=target, comentarios=mongo.db.comentarios.find() )

@app.route('/input')
def input():
    return render_template('input.html')

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
    comentarios = mongo.db.comentarios
    target = recetas.find_one_and_delete({'_id':ObjectId(item)})
    if user.email == 'administrador@cookmeasure.com':
        return redirect(url_for('recetas'))
    else:
        return redirect(url_for('misrecetas'))


@app.route('/recetas')
def recetas():
    recetas = mongo.db.recetas
    rep = []
    comentarios = mongo.db.comentarios
    return render_template('receta.html',recetas=recetas.find(), ingres=recetas.find(), especifico=recetas.find(), ingro = rep)

@app.route('/recetas/<receta>')
def receta1(receta):
    recetas = mongo.db.recetas
    comentarios = mongo.db.comentarios
    target = recetas.find_one({'_id':ObjectId(receta)})
    coment = comentarios.find({'receta':ObjectId(receta)})
    return render_template('recetas.html',receta=target, comentarios=mongo.db.comentarios.find())

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

@app.route('/busqueda',methods=['POST'])
def busqueda():
    recetas = mongo.db.recetas
    if request.method == 'POST':
        buscar = request.form['busqueda']
        resultado = recetas.find()
    return render_template('busqueda.html',recetas=resultado, busqueda=buscar)

@app.route('/especifico',methods=['POST'])
def especifico():
    recetas = mongo.db.recetas
    if request.method == 'POST':
        ings = request.form.getlist('ingredientes_check')
        rep = []
        resultado = recetas.find()
        tamanio = len(ings)
        repetido = recetas.find({'ingredientes':ings})
        for i in repetido:
            rep.append(i)
    return render_template('especifica.html', recetas=resultado, tamanio = rep, ingredientes_especifico=ings, ingres=recetas.find(), especifico=recetas.find())

@app.route('/filtro', methods=['POST'])
def filtro():
    recetas = mongo.db.recetas
    if request.method == 'POST':
        ings = request.form.getlist('ingredientes_check')
        resultado = recetas.find()
    return render_template('filtro.html', recetas=resultado, ingredientes_especifico=ings, ingres=recetas.find(), especifico=recetas.find())

@app.route('/creadores')
def creadores():
    return render_template('creadores.html')

if __name__ == '__main__':
    app.secret_key = 'mykey'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)