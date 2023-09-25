from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comunidade_dev.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(),Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacaoSenha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botaoSubmitCriarConta = SubmitField('Criar')


    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email = email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça Login para continuar.')


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(),Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrarDados = BooleanField('Lembrar Dados de Acesso')
    botaoSubmitLogin = SubmitField('Fazer Login')



class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(),Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg','png','jpeg'])])

    tech_python = BooleanField('Python')
    tech_javascript = BooleanField('JavaScript')
    tech_java = BooleanField('Java')
    tech_Kotlin = BooleanField('Kotlin')
    tech_C = BooleanField('C')
    tech_react = BooleanField('React')
    tech_NodeJs = BooleanField('Node.js')
    tech_Flask = BooleanField('Flask')
    tech_Django = BooleanField('Django')
    tech_CSharpe = BooleanField('C#')
    tech_CPlusPlus = BooleanField('C++')
    tech_AngularJS = BooleanField('Angular.js')
    tech_Figma = BooleanField('Figma')
    tech_NodeJs = BooleanField('Node.js')
    tech_AWS = BooleanField('AWS')
    tech_HTML = BooleanField('HTML')
    tech_CSS = BooleanField('CSS')

    areaAtuacao = StringField('Digite sua Área de Atuação', validators=[DataRequired()])
    
    botaoSubmitEditarPerfil = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email = email.data).first()
            if usuario:
                raise ValidationError('E-mail já cadastrado com outro Usuário. Cadastre-se com outro e-mail.')




class FormCriarPost(FlaskForm):
    foto_post = FileField('Adicione uma foto ao post', validators=[FileAllowed(['jpg','png','jpeg'])])
    corpo = TextAreaField('Escreva seu post aqui', validators=[DataRequired()])
    botaoSubmitCriarPost = SubmitField('Criar Postagem')



class FormCriarComentario(FlaskForm):
    corpo = TextAreaField('Escreva seu comentario aqui', validators=[DataRequired()])
    botaoSubmitCriarComentario = SubmitField('Criar Comentario')

class FormRecuperarSenha(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(),Email()])
    botaoSubmitEnviarEmail = SubmitField('Enviar Email')


class FormAlterarSenha(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(),Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    botaoSubmitAlterarSenha = SubmitField('Alterar Senha')