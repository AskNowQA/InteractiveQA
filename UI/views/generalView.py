import flask
from flask_login import login_user, login_required, logout_user
from flask.ext.classy import FlaskView, route
from werkzeug.security import generate_password_hash, check_password_hash

from UI.forms.loginForm import LoginForm
from UI.forms.registerForm import RegisterForm
from UI.database.tabledef import User


class GeneralView(FlaskView):
    route_base = '/'
    db = None

    def index(self):
        return flask.render_template('index.html')

    @route('login', methods=['GET', 'POST'])
    def login(self):
        form = LoginForm()

        if form.validate_on_submit():
            user = self.db.session.query(User).filter_by(username=form.username.data).first()
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    return flask.redirect(flask.url_for('GeneralView:index'))
            flask.flash('Error: Invalid username or password')

        return flask.render_template('login.html', form=form)

    @login_required
    def logout(self):
        logout_user()
        return flask.redirect(flask.url_for('GeneralView:index'))

    @route('signup', methods=['GET', 'POST'])
    def signup(self):
        form = RegisterForm()

        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            self.db.session.add(new_user)
            self.db.session.commit()
            flask.flash('New user has been created!')

        return flask.render_template('signup.html', form=form)
