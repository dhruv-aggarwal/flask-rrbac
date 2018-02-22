from flask import Flask, Response
from flask_rrbac import (
    RoleRouteBasedACL,
    ACLUserMixin,
    ACLRoleMixin,
    ACLRoleRouteMapMixin,
    ACLRouteMixin,
    ACLUserRoleMapMixin
)
from flask.ext.login import current_user
from flask_sqlalchemy import SQLAlchemy
import pytest
from flask.ext.login import LoginManager, UserMixin
from werkzeug.exceptions import Forbidden

app = Flask(__name__)
app.debug = True

rrbac = RoleRouteBasedACL(
    app,
    user_loader=lambda: current_user
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_app.db'
app.config['SECRET_KEY'] = 'sqlite:///test_app.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@rrbac.as_role_model
class Role(db.Model, ACLRoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)


@rrbac.as_user_model
class User(db.Model, ACLUserMixin, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)


@rrbac.as_route_model
class Route(db.Model, ACLRouteMixin):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    method = db.Column(db.String(10), nullable=False)
    rule = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)


@rrbac.as_user_role_map_model
class UserRoleMap(db.Model, ACLUserRoleMapMixin):
    __tablename__ = 'user_role_map'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    user = db.relationship(
        'User', backref=db.backref(
            'user_role_map_entries',
            cascade='all,delete-orphan'
        )
    )
    role = db.relationship(
        'Role', backref=db.backref(
            'user_role_map_entries',
            cascade='all,delete-orphan'
        )
    )


@rrbac.as_role_route_map_model
class RoleRouteMap(db.Model, ACLRoleRouteMapMixin):
    __tablename__ = 'role_route_map'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    route_id = db.Column(
        db.Integer,
        db.ForeignKey('routes.id'),
        nullable=False
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    route = db.relationship(
        'Route', backref=db.backref(
            'role_route_map_entries',
            cascade='all,delete-orphan'
        )
    )
    role = db.relationship(
        'Role', backref=db.backref(
            'role_route_map_entries',
            cascade='all,delete-orphan'
        )
    )


@app.route('/uncovered_route')
def uncovered_route():
    return Response('uncovered_route')


@app.route('/covered_route', methods=['GET', 'POST'])
@rrbac._authenticate
def covered_route():
    return Response('covered_route')


def tear_down():
    db.session.close()
    db.drop_all()


test_client = app.test_client()


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def data_setup():
    # Add Roles
    admin_role = Role(name='admin')
    base_role = Role(name='base')
    super_admin_role = Role(name='super_admin')
    db.session.add(admin_role)
    db.session.add(base_role)
    db.session.add(super_admin_role)
    db.session.commit()

    # Add Users
    admin_user = User(name='admin')
    base_user = User(name='base')
    super_admin_user = User(name='super_admin')
    db.session.add(admin_user)
    db.session.add(base_user)
    db.session.add(super_admin_user)
    db.session.commit()

    # Attach role to users
    db.session.add(UserRoleMap(role=admin_role, user=admin_user))
    db.session.add(UserRoleMap(role=base_role, user=base_user))
    db.session.add(UserRoleMap(role=super_admin_role, user=super_admin_user))
    db.session.commit()

    # Add Routes
    get_route = Route(rule='/covered_route', method='GET')
    post_route = Route(rule='/covered_route', method='POST')
    db.session.add(get_route)
    db.session.add(post_route)
    db.session.commit()

    # Add Role Route Map
    db.session.add(RoleRouteMap(role=admin_role, route=get_route))
    db.session.add(RoleRouteMap(role=super_admin_role, route=get_route))
    db.session.add(RoleRouteMap(role=super_admin_role, route=post_route))
    db.session.commit()
    db.session.refresh(base_user)
    db.session.refresh(admin_user)
    db.session.refresh(super_admin_user)
    return [base_user, admin_user, super_admin_user]


@pytest.fixture(scope='function')
def fixture_success(request):
    """
    Input:
    Output:
    Test Cases:
    """

    db.create_all()
    base_user, admin_user, super_admin_user = data_setup()

    data_to_send = [
        {
            'input': {
                'method': 'GET',
                'url_rule': '/uncovered_route',
                'user': base_user,
                'function': 'uncovered_route'
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/uncovered_route',
                'user': admin_user,
                'function': 'uncovered_route'
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/uncovered_route',
                'user': super_admin_user,
                'function': 'uncovered_route'
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route',
                'user': admin_user,
                'function': 'covered_route'
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route',
                'user': super_admin_user,
                'function': 'covered_route'
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route',
                'user': super_admin_user,
                'function': 'covered_route'
            },
            'output': {
                'status_code': 200
            }
        }
    ]
    request.addfinalizer(tear_down)
    return data_to_send


@pytest.fixture(scope='function')
def fixture_failure(request):
    """
    Input:
    Output:
    Test Cases:
    """

    db.create_all()
    base_user, admin_user, super_admin_user = data_setup()

    data_to_send = [
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route',
                'user': admin_user,
                'function': 'covered_route'
            },
            'output': {
                'status_code': 403
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route',
                'user': base_user,
                'function': 'covered_route'
            },
            'output': {
                'status_code': 403
            }
        }
    ]
    request.addfinalizer(tear_down)
    return data_to_send


class TestRRBAC():
    @pytest.mark.usefixtures("fixture_success")
    def test_success(self, fixture_success):
        for index, data in enumerate(fixture_success):
            print '\nScenario {} Started'.format(index + 1)
            with app.test_request_context(
                data['input']['url_rule'], method=data['input']['method']
            ) as request_ctx:
                request_ctx.user = data['input']['user']
                output = eval(data['input']['function'])()
                assert output.status_code == data['output']['status_code']
                print '\nScenario {} Passed'.format(index + 1)

    @pytest.mark.usefixtures("fixture_failure")
    def test_failure(self, fixture_failure):
        for index, data in enumerate(fixture_failure):
            print '\nScenario {} Started'.format(index + 1)
            with app.test_request_context(
                data['input']['url_rule'],
                method=data['input']['method']
            ) as request_ctx:
                request_ctx.user = data['input']['user']
                try:
                    eval(data['input']['function'])()
                except Forbidden:
                    print '\nScenario {} Passed'.format(index + 1)
