import datetime

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail

from data import db_session
from data.goods import Goods
from data.users import User
from forms.goods_form import GoodsForm
from forms.user_form import RegisterForm, LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
menu = {'name': 'обратная связь', 'url': 'feedback'}

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/irons.db")
    app.run()


@app.route('/goods_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def goods_delete(id):
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods).filter(Goods.id == id, Goods.user == current_user).first()
    if goods:
        db_sess.delete(goods)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/goods/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_goods(id):
    form = GoodsForm()
    photo = ""
    if request.method == "GET":
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods).filter(Goods.id == id, Goods.user == current_user).first()
        if goods:
            form.category.default = goods.category_id
            form.process()
            form.title.data = goods.title
            form.content.data = goods.content
            photo = goods.photo
        else:
            redirect('/add_goods')
        # form.title.data = ""
        # form.content.data = ""
        # photo = None
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if id > 0:
            print("id>0")
            goods = db_sess.query(Goods).filter(Goods.id == id).first()
            if goods:
                goods.title = form.title.data
                goods.content = form.content.data
                uploaded_file = request.files['file']
                if uploaded_file.filename != '':
                    uploaded_file.save(f'./static/img/{form.category.data}/{goods.photo}')
                    goods.photo = uploaded_file.filename
                    db_sess.commit()
                return redirect('/')
            else:
                abort(404)
        else:
            print("id==0")
            # goods = Goods()
            # goods.title = form.title.data
            # goods.content = form.content.data
            # goods.category_id = form.category.data
            # goods.created_date = datetime.date.today()
            # goods.photo = ""
            # uploaded_file = request.files['file']
            # if uploaded_file.filename != '':
            #     goods.photo = uploaded_file.filename
            #     uploaded_file.save(f'./static/img/{form.category.data}/{uploaded_file.filename}')
            # current_user.goods.append(goods)
            # print("goods", goods.id, goods.category_id, goods.photo)
            # db_sess.merge(current_user)
            # db_sess.commit()
            # goods = db_sess.query(Goods.id).order_by(Goods.id.desc()).first()
            return redirect('/add_goods')
    return render_template('goods.html', title='Редактировать', form=form, photo=photo)


@app.route("/add_goods", methods=['GET', 'POST'])
def add_goods():
    form = GoodsForm()
    if request.method == "GET":
        # db_sess = db_session.create_session()
        # goods = db_sess.query(Goods).filter(Goods.id == id, Goods.user == current_user).first()
        # if goods:
        #     form.category.default = goods.category_id
        #     form.process()
        #     form.title.data = goods.title
        #     form.content.data = goods.content
        #     photo = goods.photo
        # else:
        form.title.data = ""
        form.content.data = ""
        photo = None
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # получаем номер последнего эелемента таблицы goods
        goods = db_sess.query(Goods).order_by(Goods.id.desc()).first()
        id = goods.id + 1
        # if id > 0:
        #     print("id>0")
        #     goods = db_sess.query(Goods).filter(Goods.id == id).first()
        #     if goods:
        #         goods.title = form.title.data
        #         goods.content = form.content.data
        #         db_sess.commit()
        #         uploaded_file = request.files['file']
        #         if uploaded_file.filename != '':
        #             uploaded_file.save(f'./static/img/{form.category.data}/{goods.photo}')
        #         return redirect('/goods/')
        #     else:
        #         abort(404)
        # else:
        print("id=", goods.id)
        goods = Goods()
        goods.id = id
        goods.title = form.title.data
        goods.content = form.content.data
        goods.category_id = form.category.data
        goods.created_date = datetime.date.today()
        goods.photo = ""
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            goods.photo = uploaded_file.filename
            uploaded_file.save(f'./static/img/{form.category.data}/{uploaded_file.filename}')
        current_user.goods.append(goods)
        print("goods", goods.id, goods.category_id, goods.photo)
        db_sess.merge(current_user)
        db_sess.commit()
        goods = db_sess.query(Goods.id).order_by(Goods.id.desc()).first()
        return redirect('/')
    return render_template('goods.html', title='Редактировать', form=form, photo=photo)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    vensels = db_sess.query(Goods).filter(Goods.category_id == 1)
    num_vensels = db_sess.query(Goods).filter(Goods.category_id == 1).count()
    print(num_vensels)
    num_gratings = db_sess.query(Goods).filter(Goods.category_id == 3).count()
    gratings = db_sess.query(Goods).filter(Goods.category_id == 3)
    print(num_gratings)
    return render_template("navs.html", vensels=vensels, gratings=gratings)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     #form = ContactForm()
#     form1 = ContactForm(MultiDict([('name', 'jerry'), ('email', 'jerry@mail.com')]))
#
#     # if form.validate_on_submit():
# 	# name = form.name.data
# 	# email = form.email.data
# 	# message = form.message.data
# 	# print(name)
# 	# print(email)
# 	# print(message)
# 	# # здесь логика базы данных
# 	# print("\nData received. Now redirecting ...")
# 	# return redirect(url_for('contact'))
#
#     return render_template('contact.html', form=form1)
#
#
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        print(request.form)
    return render_template('contact.html', title='Обратная связь', menu=menu)


if __name__ == '__main__':
    main()
