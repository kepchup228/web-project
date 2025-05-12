from flask import Flask, render_template, redirect, request, abort, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename

from data.db_session import create_session
from forms.photo import PhotoForm
from forms.user import RegisterForm, LoginForm
from data.photos import Photo
from data.tags import Tag
from data.users import User
from data import db_session
from data.comments import Comment


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

# Для загрузки пользователей
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# Для выхолда из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

# Для добавления фотографий
@app.route('/add_photo', methods=['GET', 'POST'])
@login_required
def add_photo():
    form = PhotoForm() # Форма для фото
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        try:
            # Получаем пользователя из текущей сессии
            user = db_sess.query(User).get(current_user.id)

            # Сохраняем файл
            file = form.photo.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Создаем запись о фото
                photo = Photo(
                    title=form.title.data,
                    description=form.description.data,
                    filename=filename,
                    is_private=form.is_private.data,
                    user=user  # Связываем с пользователем из сессии
                )

                # Обрабатываем теги
                tags = [t.strip() for t in form.tags.data.split(',') if t.strip()]
                for tag_name in tags:
                    tag = db_sess.query(Tag).filter(Tag.name == tag_name.lower()).first()
                    if not tag:
                        tag = Tag(name=tag_name.lower())
                        db_sess.add(tag)
                    photo.tags.append(tag)

                db_sess.add(photo)
                db_sess.commit()
                return redirect('/')
            else:
                # Если не тот формат
                return render_template('photo.html',
                                       title='Добавление фотографии',
                                       form=form,
                                       message="Недопустимый формат файла")
        finally:
            db_sess.close()
    return render_template('photo.html', title='Добавление фотографии', form=form)

# Проверка разрешенных расширений
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/edit_photo/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_photo(id):
    form = PhotoForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        photo = db_sess.query(Photo).filter(Photo.id == id, Photo.user == current_user).first()
        if photo:
            # Заполняем текущими данными
            form.title.data = photo.title
            form.description.data = photo.description
            form.tags.data = ', '.join([tag.name for tag in photo.tags])
            form.is_private.data = photo.is_private
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        photo = db_sess.query(Photo).filter(Photo.id == id, Photo.user == current_user).first()
        if photo:
            photo.title = form.title.data
            photo.description = form.description.data
            photo.is_private = form.is_private.data

            photo.tags = [] # Очищаем старые теги
            tags = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tags:
                tag = db_sess.query(Tag).filter(Tag.name == tag_name.lower()).first()
                if not tag:
                    tag = Tag(name=tag_name.lower())
                    db_sess.add(tag)
                photo.tags.append(tag)

            # Если загружен новый файл
            file = form.photo.data
            if file and allowed_file(file.filename):
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
                except:
                    pass

                # Сохраняем новый файл
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                photo.filename = filename

            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('photo.html', title='Редактирование фотографии', form=form)


@app.route('/delete_photo/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_photo(id):
    db_sess = db_session.create_session()
    # Ищем принадлежащее текущему пользователю
    photo = db_sess.query(Photo).filter(Photo.id == id, Photo.user == current_user).first()
    if photo:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
        except:
            pass

        db_sess.delete(photo)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower() # Поисковой запрос
    if not query:
        return redirect(url_for('index')) # Если пустой, то на главную

    db_sess = db_session.create_session()
    search_terms = query.split()
    filters = []

    # Фильтры по приватности
    if current_user.is_authenticated:
        filters.append((Photo.user == current_user) | (Photo.is_private != True))
    else:
        filters.append(Photo.is_private != True)

    for term in search_terms:
        filters.append(
            (Photo.title.contains(term)) |
            (Photo.description.contains(term)) |
            (Photo.tags.any(Tag.name.contains(term)))
        )

    photos = db_sess.query(Photo).filter(*filters).order_by(Photo.created_date.desc()).all()
    # Доп фото, другие
    other_photos = db_sess.query(Photo).filter(
        ~Photo.id.in_([photo.id for photo in photos])
    ).order_by(Photo.created_date.desc()).limit(5).all()

    return render_template('index.html', photos=photos, other_photos=other_photos, search_query=query)

@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        # Авторизованные пользователи видят свои и публичные фото
        photos = db_sess.query(Photo).filter((Photo.user == current_user) | (Photo.is_private != True))
    else:
        photos = db_sess.query(Photo).filter(Photo.is_private != True)
    # Сортируем по дате создания (новые сначала)
    photos = photos.order_by(Photo.created_date.desc()).all()
    return render_template("index.html", photos=photos)

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        # Создаем нового пользователя
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data) # Хешируем пароль
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

# Страница с фотографиями текущего пользователя
@app.route('/my_photos')
@login_required
def my_photos():
    db_sess = db_session.create_session()
    photos = db_sess.query(Photo).filter(Photo.user == current_user).all()
    return render_template('my_photos.html', photos=photos)

# Комментарии, но надо доделать
@app.route('/add_comment/<int:photo_id>', methods=['POST'])
@login_required
def add_comment(photo_id):
    db_sess = db_session.create_session()
    photo = db_sess.query(Photo).get(photo_id)
    if not photo:
        abort(404)

    content = request.form.get('content')
    if content:
        comment = Comment(photo_id=photo_id, user_id=current_user.id, content=content)
        db_sess.add(comment)
        db_sess.commit()

    return redirect(url_for('photo_detail', photo_id=photo_id))

# Для комментариев
@app.route('/photo/<int:photo_id>')
def photo_detail(photo_id):
    db_sess = db_session.create_session()
    photo = db_sess.query(Photo).get(photo_id)
    if not photo:
        abort(404)

    comments = db_sess.query(Comment).filter(Comment.photo_id == photo_id).all()
    return render_template('photo_detail.html', photo=photo, comments=comments)


# для автодополнения тего
@app.route('/api/tags')
def api_tags():
    query = request.args.get('q', '').strip().lower()
    db_sess = db_session.create_session()
    tags = db_sess.query(Tag).filter(Tag.name.contains(query)).limit(10).all()
    return jsonify({
        'tags': [tag.name for tag in tags]
    })


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


def main():
    db_session.global_init("db/blogs.db")
    # Создаем папку для загрузок, если ее нет
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)


if __name__ == '__main__':
    main()
