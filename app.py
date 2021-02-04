from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user
#cifrar contraseñas
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.debug = True
bcrypt = Bcrypt()
bcrypt.init_app(app)
# Configuración de la app  para manejar  sesión
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.log_view='index'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI']='postgres://joeolbucwloayc:2b934d8dced2238b0b02808933f5eab33f9fd26431447d254c172461f4c9b1a4@ec2-3-222-11-129.compute-1.amazonaws.com:5432/d8o69s1d6r6hlq'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)


#-----------------CONSTRUCCIÓN DE LA BASE DE DATOS-----------------------

#modelo de datos
class Usuarios(db.Model):
	__Tablename__ = 'usuarios'

	id_usr = db.Column(db.Integer, primary_key = True)
	correo = db.Column(db.String(250), unique = True, nullable = False, index = True)
	nombre_usr = db.Column(db.String(250))
	pwd_usr = db.Column(db.String(250))
	level = db.Column(db.Integer)

	def is_authenticated(self):
		return True
	
	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False
	
	def get_id(self):
		return str(self.id_usr)

@login_manager.user_loader
def load_user(user_id):
	return Usuarios.query.filter_by(id_usr=user_id).first()

class Editorial(db.Model):
	__Tablename__ = 'editorial'

	id_editorial = db.Column(db.Integer, primary_key = True)
	nombre = db.Column(db.String(80))

	def __init__(self, nombre):
		self.nombre = nombre

class Libros(db.Model):
	__Tablename__ = 'libros'

	id_libro = db.Column(db.Integer, primary_key = True)
	titulo = db.Column(db.String(500), nullable = False, index = True)
	autor = db.Column(db.String(80))
	clasificacion = db.Column(db.String(80))
	formato = db.Column(db.String(50))
	url_img = db.Column(db.String(100), unique = True)
	no_pags = db.Column(db.Integer)
	#fecha_publicacion = db.Column(db.DateTime, default = datetime.now(tz = 'UTC'))

	#Establecer la relacion entre tablas
	id_editorial = db.Column(db.Integer, db.ForeignKey('editorial.id_editorial'))

	def __init__(self, titulo, autor, clasificacion, formato, url_img, no_pags, id_editorial):
		self.titulo = titulo
		self.autor = autor
		self.clasificacion = clasificacion
		self.formato = formato
		self.url_img = url_img
		self.no_pags = no_pags
		self.id_editorial = id_editorial

#------------RUTA DE LOGIN--------------------------
	global correo
#Definimos la ruta del Login
@app.route('/', methods=['GET','POST'])
def index():
	if request.method == "POST":
		correo = request.form["correo"]
		pwd = request.form["pwd"]
		usuario_existe = Usuarios.query.filter_by(correo = correo).first()
		print (usuario_existe)
		#mensaje = usuario_existe
		if usuario_existe != None:
			if bcrypt.check_password_hash(usuario_existe.pwd_usr, pwd):
				login_user(usuario_existe)
				print(login_user(usuario_existe))
				if current_user.is_authenticated:
					mensaje = usuario_existe
					#return redirect("/home")
					return render_template("Ahome.html", usuario_existe = usuario_existe)
		return render_template("index.html")
	return render_template("index.html")

@app.route('/createacount', methods = ['GET', 'POST'])
def createacount():
	mensaje = ""
	if request.method == "POST":
		pwd = request.form["pwd"]
		password = request.form["password"]	
		if pwd != password:
			mensaje = "¡Las contraseñas no coinciden!"
			return render_template("createacount.html", mensaje = mensaje)
		else:
			nombre = request.form["nombre"]
			correo = request.form["correo"]
			contraseña = request.form["pwd"]
			nivel = request.form["nivel"]
			mensaje = "Usuario registrado"

			usuarios = Usuarios(
				nombre_usr = nombre,
				correo = correo,
				pwd_usr = bcrypt.generate_password_hash(contraseña).decode('Utf-8'),
				level = nivel
			)
			db.session.add(usuarios)
			db.session.commit()

			return render_template("index.html", mensaje = mensaje)
	return render_template("createacount.html", mensaje = mensaje)
#-------------RUTAS DE LIBROS------------------------

#Definimos la ruta del menú
@app.route('/home', methods = ['GET', 'POST'])
def home():	
	return render_template("home2.html")
	#return redirect(url_for("acerca"))
@app.route('/Ahome', methods = ['GET', 'POST'])
def Ahome():
	id_usuario = current_user.get_id()
	usuario_existe = Usuarios.query.get(id_usuario)
	return render_template("Ahome.html", usuario_existe = usuario_existe)

#Definimos la ruta para registrar libros
@app.route('/addbooks',methods=['GET','POST'])
def addbooks():
	id_usuario = current_user.get_id()
	usuario_existe = Usuarios.query.get(id_usuario)
	if request.method == "POST":
		print("request")
		titulo = request.form['titulo']
		autor = request.form['autor']
		clasificacion = request.form['clasificacion']
		formato = request.form['formato']
		url_img = request.form['urlimg']
		no_pags = request.form['no_pags']
		id_editorial = request.form['id_edit']
		libro = Libros(titulo=titulo,autor=autor, clasificacion=clasificacion, formato=formato, url_img=url_img, no_pags=no_pags, id_editorial=id_editorial)
		db.session.add(libro)
		db.session.commit()
		mensaje = "Libro registrado"
		return render_template('Ahome.html', usuario_existe = usuario_existe)
	return render_template("addbooks.html")

#Definimos la ruta para ver libros
@app.route('/books')
def books():
	consulta = Libros.query.all()
	return render_template("books.html", books = consulta)

#Definimos la ruta editar libro
@app.route('/bookedit/<id_libro>')
def bookedit(id_libro):
	reg = Libros.query.filter_by(id_libro = id_libro).first()
	return render_template('bookedit.html', libro = reg)

@app.route('/bactualizar',methods=['GET','POST'])
def bactualizar():
	id_usuario = current_user.get_id()
	usuario_existe = Usuarios.query.get(id_usuario)
	if request.method == "POST":
		query = Libros.query.get(request.form['id_libro'])
		query.titulo = request.form['tituloE']
		query.autor = request.form['autorE']
		query.clasificacion = request.form['clasificacionE']
		query.formato = request.form['formatoE']
		query.url_img = request.form['urlimgE']
		query.no_pags = request.form['no_pagsE']
		query.id_editorial = request.form['id_editE']
		db.session.commit()
		return render_template('Ahome.html', usuario_existe = usuario_existe)
	return render_template("addbooks.html")

#Definimos ruta para eliminar libro
@app.route('/bookdelete/<id_libro>')
def bookdelete(id_libro):
	reg = Libros.query.filter_by(id_libro = id_libro).delete()
	db.session.commit()
	return redirect(url_for('books'))

#--------------RUTAS DE EDITORIALES-----------------------

#Definimos la ruta para registrar editoriales
@app.route('/addedits', methods=['GET','POST'])
def addedits():
	id_usuario = current_user.get_id()
	usuario_existe = Usuarios.query.get(id_usuario)
	if request.method == "POST":
		print("request")
		nombre = request.form['editorial']
		editorial = Editorial(nombre=nombre)
		db.session.add(editorial)
		db.session.commit()
		mensaje = "Editorial registrada"
		return render_template('Ahome.html', usuario_existe = usuario_existe)
	return render_template("addedits.html")

#Definimos la ruta para ver editoriales
@app.route('/edits')
def edits():
	consulta = Editorial.query.all()
	return render_template("edits.html", edits = consulta)

#Definimos la ruta editar editorial
@app.route('/editedit/<id_editorial>')
def editedit(id_editorial):
	reg = Editorial.query.filter_by(id_editorial = id_editorial).first()
	return render_template('editedit.html', editorial = reg)

@app.route('/eactualizar',methods=['GET','POST'])
def eactualizar():
	id_usuario = current_user.get_id()
	usuario_existe = Usuarios.query.get(id_usuario)
	if request.method == "POST":
		query = Editorial.query.get(request.form['id_editorial'])
		query.nombre = request.form['editorialE']
		db.session.commit()
		return render_template("Ahome.html", usuario_existe = usuario_existe)
	return render_template("addedits.html")

#Definimos ruta para eliminar editorial
@app.route('/eeliminar/<id_editorial>')
def eeliminar(id_editorial):
	reg = Editorial.query.filter_by(id_editorial = id_editorial).delete()
	db.session.commit()
	return redirect(url_for('edits'))

#-----------------RUTAS VARIAS-------------------

#Definimos la ruta acerca de la app
@app.route('/acerca')
def acerca():
	return render_template("acerca.html")

#Definimos la ruta logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    
    return redirect(url_for("index"))

if __name__ == "__main__":
	db.create_all()
	app.run()