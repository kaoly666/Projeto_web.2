from flask import Flask
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'uma_chave_muito_secreta_e_complexa' # mude para uma chave real e forte
	app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

	# cria a pasta de uploads se nao existir
	if not os.path.exists(UPLOAD_FOLDER):
		os.makedirs(UPLOAD_FOLDER)

	from . import routes
	app.register_blueprint(routes.bp) # se usar blueprints, ou importar diretamente as rotas

	# filtro jinja para formatacao de moeda
	@app.template_filter('format_currency')
	def format_currency_filter(value):
		return f'{value:,.2f}'.replace(',', 'X').replace('.', '.').replace('X', '.')

	return app

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
