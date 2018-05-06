from . import rrbac, db, login_manager
from flask_rrbac import (
    ACLUserMixin,
    ACLRoleMixin,
    ACLUserRoleMapMixin
)
from flask.ext.login import UserMixin


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


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
