# app/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
import os
from . import allowed_file
from .models import get_ads, add_ad, Ad

bp = Blueprint('main', __name__)

@bp.before_app_request
def before_request():
    if 'cart' not in session:
        session['cart'] = []

@bp.route('/')
def index():
    anuncios = get_ads()
    return render_template('index.html', anuncios=anuncios)

@bp.route('/criar_anuncio', methods=['GET', 'POST'])
def criar_anuncio():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo de imagem enviado.', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Nenhum arquivo selecionado para upload.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(file_path)
            except Exception as e:
                flash(f'Erro ao salvar a imagem: {e}', 'error')
                return redirect(request.url)

            nome = request.form['nome']
            descricao = request.form['descricao']
            categoria = request.form['categoria']
            preco = request.form.get('preco', type=float)

            if not nome or not descricao or not categoria or preco is None:
                flash('Todos os campos (Nome, Descricao, Categoria, Preco) sao obrigatorios!', 'error')
                if os.path.exists(file_path):
                    os.remove(file_path)
                return redirect(request.url)

            if preco < 0:
                flash('O preco nao pode ser negativo!', 'error')
                if os.path.exists(file_path):
                    os.remove(file_path)
                return redirect(request.url)

            new_ad = Ad(nome=nome, descricao=descricao, categoria=categoria, imagem=filename, preco=preco)
            add_ad(new_ad)

            flash('Anuncio criado com sucesso!', 'success')
            return render_template('ad_success.html', ad=new_ad)
        else:
            flash('Tipo de arquivo nao permitido.', 'error')
            return redirect(request.url)

    return render_template('create_ad.html')

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/add_to_cart/<int:ad_id>')
def add_to_cart(ad_id):
    all_ads = get_ads()
    ad_to_add = next((ad for ad in all_ads if ad.id == ad_id), None)

    if ad_to_add:
        found_in_cart = False
        for item in session['cart']:
            if item['id'] == ad_id:
                item['quantity'] += 1
                found_in_cart = True
                break
        if not found_in_cart:
            session['cart'].append({
                'id': ad_to_add.id,
                'name': ad_to_add.nome,
                'price': ad_to_add.preco,
                'image': ad_to_add.imagem,
                'quantity': 1
            })
        session.modified = True
        flash(f'"{ad_to_add.nome}" adicionado ao carrinho!', 'success')
    else:
        flash('Anuncio nao encontrado.', 'error')
    return redirect(url_for('main.index'))

@bp.route('/cart')
def view_cart():
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@bp.route('/update_cart/<int:ad_id>/<action>')
def update_cart_item(ad_id, action):
    for item in session['cart']:
        if item['id'] == ad_id:
            if action == 'increase':
                item['quantity'] += 1
            elif action == 'decrease':
                if item['quantity'] > 1:
                    item['quantity'] -= 1
                else:
                    session['cart'] = [i for i in session['cart'] if i['id'] != ad_id]
            break
    session.modified = True
    return redirect(url_for('main.view_cart'))

@bp.route('/remove_from_cart/<int:ad_id>')
def remove_from_cart(ad_id):
    session['cart'] = [item for item in session['cart'] if item['id'] != ad_id]
    session.modified = True
    flash('Item removido do carrinho.', 'success')
    return redirect(url_for('main.view_cart'))

@bp.route('/get_cart_count')
def get_cart_count():
    count = sum(item['quantity'] for item in session.get('cart', []))
    return jsonify(count=count)

