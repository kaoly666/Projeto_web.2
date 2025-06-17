from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
from . import allowed_file # importa a funcao helper do __init__.py
from .models import get_ads, add_ad, ad # importa as funcoes/classes do seu models.py

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
	anuncios = get_ads()
	return render_template('index.html', anuncios=anuncios)

@bp.route('/criar_anuncio', methods=['GET','POST'])
def criar_anuncio():
	if request.method == 'POST':
		# validacao basica
		if 'file' not in request.files:
			flash('nenhum arquivo enviado', 'error')
			return redirect(request.url)

		file = request.files['file']
		nome = request.form['nome']
		descricao = request.form['descricao']
		categoria = request.form['categoria']
		preco = request.form.get('preco', type=float) # pega o preco como float

		if file.filename == '.':
			flash('nenhum arquivo selecionado', 'error')
			return redirect(request.url)

		if not nome or not descricao or not categoria or preco is None:
			flash('todos os campos sao obrigatorios', 'error')
			return redirect(request.url)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
			file.save(file_path)

			new_ad = ad(
				nome=nome,
				descricao=descricao,
				categoria=categoria,
				imagem=filename, # salva o nome dos arquivos da imagem
				preco=preco
			)
			add_ad(new_ad) # adiciona o anuncio aos seus "dados"

			flash('anuncio criado com sucesso.')
			return render_template('ad_success.html', ad=new_ad)
		else:
			flash('tipo de arquivo nao permitido', 'error')
			return redirect(request.url)

	# se for GET request, mostra o formulario 
	return render_template('create_ad.html')

# rota para servir as imagens
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
