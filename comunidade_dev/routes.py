from flask import render_template,url_for, request, flash, redirect, abort
from comunidade_dev import app, database, bcrypt, mail, Message
from .forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost, FormCriarComentario, FormRecuperarSenha, FormAlterarSenha
from .models import Usuario, Post, Comentario
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


@app.route('/')
def capa():
    return render_template('capa.html')

@app.route('/home')
@login_required
def home():
    posts = Post.query.order_by(Post.id.desc())
    quantPosts = posts.count()
    postComFoto = False

    for post in posts:
        if post.fotoPost:
            postComFoto = True


    return render_template('home.html', posts=posts, quantPosts=quantPosts, postComFoto=postComFoto)

@app.route('/home/contato')
def contato():
    return render_template('contato.html')

@app.route('/home/usuarios')
@login_required
def usuarios():

    quantUsuarios = 0

    usuarios = Usuario.query.all()

    for usuario in usuarios:
        quantUsuarios+=1

    return render_template('usuarios.html', usuarios = usuarios, quantUsuarios=quantUsuarios)

@app.route('/home/login', methods=['GET', 'POST'])
def login():
    formLogin = FormLogin()
    formCriarConta = FormCriarConta()

    if formLogin.validate_on_submit() and 'botaoSubmitLogin' in request.form:

        usuario = Usuario.query.filter_by(email = formLogin.email.data).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, formLogin.senha.data):
            login_user(usuario, remember= formLogin.lembrarDados.data)
            # Exibir mensagen de login com sucesso!
            flash(f'Login feito com sucesso no E-mail: {formLogin.email.data}', 'alert-success')

            paramNext = request.args.get('next')

            if paramNext:
                return redirect(paramNext)

            else:
                # Redirecionar para a Homepage
                return redirect(url_for('home'))
        else:
            flash('Falha no Login! E-mail ou senha inválidos', 'alert-danger')


    if formCriarConta.validate_on_submit() and 'botaoSubmitCriarConta' in request.form:
        # Exibir mensagem de que criou a conta com sucesso
        flash(f'Sua conta foi criada com sucesso no E-mail: {formCriarConta.email.data}', 'alert-success')

        # Criação de um Usuario

        senhaCriptografada = bcrypt.generate_password_hash(formCriarConta.senha.data)
        usuario = Usuario(username = formCriarConta.username.data, email = formCriarConta.email.data, senha = senhaCriptografada)

        # Adicionando a sessão no Banco de dados

        database.session.add(usuario)

        # Commitando para o Banco de dados

        database.session.commit()

        # Redirecionar para a Homepage
        return redirect(url_for('home'))

    return render_template('login.html', formLogin = formLogin, formCriarConta = formCriarConta)


@app.route('/home/criarConta', methods=['GET', 'POST'])
def criarConta():
    formCriarConta = FormCriarConta()

    if formCriarConta.validate_on_submit() and 'botaoSubmitCriarConta' in request.form:
        # Exibir mensagem de que criou a conta com sucesso
        flash(f'Sua conta foi criada com sucesso no E-mail: {formCriarConta.email.data}', 'alert-success')

        # Criação de um Usuario

        senhaCriptografada = bcrypt.generate_password_hash(formCriarConta.senha.data)
        usuario = Usuario(username = formCriarConta.username.data, email = formCriarConta.email.data, senha = senhaCriptografada)

        # Adicionando a sessão no Banco de dados

        database.session.add(usuario)

        # Commitando para o Banco de dados

        database.session.commit()

        # Redirecionar para a Homepage
        return redirect(url_for('home'))

    return render_template('criarConta.html', formCriarConta = formCriarConta)



@app.route('/home/recuperar_senha', methods=['GET', 'POST'])
def recuperarSenha():
    form = FormRecuperarSenha()
    email = Usuario.query.filter_by(email = form.email.data).first()
    if form.validate_on_submit():
        if email:
            msg = Message( 
                        'Recuperação de senha do APP-WEB da Comunidade Impressionadora', 
                        sender ='lucasluisouza@gmail.com', 
                        recipients = [form.email.data] 
                    ) 
            msg.body = 'Entre neste link para alterar sua senha: https:http://127.0.0.1:5000/home/alterar_senha'
            mail.send(msg)
            return render_template('emailEnviado.html')
        else:
            flash('Este E-mail não está cadastrado', 'alert-danger')
    return render_template('recuperarsenha.html', form =form )


@app.route('/home/alterar_senha', methods=['GET', 'POST'])
def alterarSenha():
    form = FormAlterarSenha()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email = form.email.data).first()
        senhaCriptografada = bcrypt.generate_password_hash(form.senha.data)
        usuario.senha = senhaCriptografada
        database.session.commit()
        flash('Senha Alterada Com Sucesso', 'alert-danger')
        return redirect(url_for('login'))

    return render_template('alterarsenha.html', form = form )


@app.route('/home/sair')
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso', 'alert-success')
    return redirect(url_for('capa'))



# PERFIL

@app.route('/home/perfil')
@login_required
def perfil():
    meus_posts = []
    posts = Post.query.order_by(Post.id.desc())
    for post in posts:
        if current_user == post.autor:
            meus_posts.append(post)

    fotoPerfilAtual = url_for('static', filename='fotos_perfil/{}'.format(current_user.fotoPerfil))
    return render_template('perfil.html', fotoPerfilAtual=fotoPerfilAtual, meus_posts = meus_posts)


@app.route('/home/perfil/editar', methods=['GET', 'POST'])
@login_required
def editarPerfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_imagem = salvarImagem(form.foto_perfil.data)
            current_user.fotoPerfil= nome_imagem

        current_user.stacks = atualizarStacks(form)
        current_user.areas = atualizarAreas(form)

        database.session.commit()
        flash('Perfil atualizado com sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
        

    fotoPerfilAtual = url_for('static', filename='fotos_perfil/{}'.format(current_user.fotoPerfil))
    return render_template('editarperfil.html', fotoPerfilAtual=fotoPerfilAtual, form = form)


def atualizarStacks(form):
    lista_stacks = []
    for campo in form:
        if 'tech_' in campo.name:
            if campo.data:
                lista_stacks.append(campo.label.text)

    return ';'.join(lista_stacks)


def atualizarAreas(form):
    lista_areas = []
    for campo in form:
        if 'area_' in campo.name:
            if campo.data:
                lista_areas.append(campo.label.text)

    return ';'.join(lista_areas)




def salvarImagem(imagem):
    codigo = secrets.token_hex(8)
    nome ,extensao = os.path.splitext(imagem.filename)
    nome_arquivo =  nome + codigo + extensao

    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)

    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)

    imagem_reduzida.save(caminho_completo)

    return nome_arquivo






# POSTAGENS

def salvarPost(imagem):
    codigo = secrets.token_hex(8)
    nome ,extensao = os.path.splitext(imagem.filename)
    nome_arquivo =  nome + codigo + extensao

    caminho_completo = os.path.join(app.root_path, 'static/fotos_posts', nome_arquivo)

    tamanho = (1000, 1000)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)

    imagem_reduzida.save(caminho_completo)

    return nome_arquivo


@app.route('/home/post/criar', methods=['GET', 'POST'])
@login_required
def criarPost():

    form = FormCriarPost()
    if form.validate_on_submit():
        if form.foto_post.data:
            nome_imagem = salvarPost(form.foto_post.data)
            post = Post(titulo = "000", fotoPost = nome_imagem ,corpo = form.corpo.data, autor = current_user)
        else:
            post = Post(titulo = "000", corpo = form.corpo.data, autor = current_user)

        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    
    return render_template('criarpost.html', form=form)


@app.route('/home/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibirPost(post_id):
    post = Post.query.get(post_id)
    
    comentarios = Comentario.query.filter_by(idPost=post.id).order_by(Comentario.id.desc())
    
    return render_template('post.html', post = post , comentarios = comentarios )
    


@app.route('/home/post/<post_id>/editar', methods=['GET', 'POST'])
@login_required
def editarPost(post_id):
    post = Post.query.get(post_id)

    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.corpo.data = post.corpo
            form.foto_post.data = post.fotoPost
        
        elif form.validate_on_submit():
            post.corpo = form.corpo.data
            if form.foto_post.data:
                nome_imagem = salvarPost(form.foto_post.data)
                post.fotoPost = nome_imagem

            database.session.commit()
            flash('Post Editado com Sucesso', 'alert-success')
            return redirect(url_for('exibirPost', post_id=post.id))
    
    return render_template('editarPost.html', post = post, form = form)

@app.route('/home/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluirPost(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluído com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    else:
        abort(403)


# COMENTARIOS
    
@app.route('/home/post/<post_id>/comentario/<comentario_id>/editar', methods = ['GET','POST'])
@login_required
def editarComentario(comentario_id, post_id):
    comentario = Comentario.query.get(comentario_id)

    if current_user == comentario.autor:
        form_coment = FormCriarComentario()
        if request.method == 'GET':
            form_coment.corpo.data = comentario.corpo
        
        elif form_coment.validate_on_submit():
            comentario.corpo = form_coment.corpo.data

            database.session.commit()
            flash('Comentario Editado com Sucesso', 'alert-success')
            return redirect(url_for('exibirPost', post_id=post_id))
    
    else:
        form_coment = None
        
    return render_template('editarcomentario.html', form_coment =form_coment, post_id=post_id , comentario = comentario)


@app.route('/home/post/<post_id>/comentario/criar', methods = ['GET','POST'])
@login_required
def criarComentario(post_id):
   
    form_coment = FormCriarComentario()
    post = Post.query.get(post_id)

    if form_coment.validate_on_submit():
        
        comentario = Comentario(corpo=form_coment.corpo.data, autor = current_user, idPost=post.id)
            
        database.session.add(comentario)
        database.session.commit()
        flash('Comentario Criado com Sucesso', 'alert-success')

        return redirect(url_for('exibirPost', post_id=post_id))
    
    return render_template('criarComentario.html', form_coment = form_coment)


@app.route('/home/post/<post_id>/comentario/<comentario_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluirComentario(post_id, comentario_id):

    comentario = Comentario.query.get(comentario_id)

    if current_user == comentario.autor:
        database.session.delete(comentario)
        database.session.commit()
        flash('Comentário excluído com sucesso!', 'alert-success')
          
        return redirect(url_for('exibirPost', post_id=post_id))