===========
Flask-RRBAC
===========
.. currentmodule:: flask_rrbac

Flask-RRBAC provides the facility to manage user access based on the assigned
roles. The accesses are to the level of endpoint and method.

It will:

- Give you helpers to figure out of a user is authorised to access your route
  or not.
- Let you add the same on static files.

However, it does not:

- Impose a particular database or other storage method on you.
- Create the reqiured models for you.
- Make the required entries for you in the database.


Table Of Contents


.. contents::
   :local:
   :backlinks: none


Installation
============
Install the extension with pip::

    $ pip install flask-rrbac


Configuring your Application
============================
The most important part of an application that uses Flask-RRBAC is the
`RoleRouteBasedACL` class. You should create one for your application 
somewhere in your code, like this::

    rrbac = RoleRouteBasedACL()

The acl manager contains the code that lets your application and Flask-RRBAC
work together, such as what all endpoints to check for user auth, the method in
the endpoint, etc.

Once the actual application object has been created, you can configure it for
acl with::

    rrbac.init_app(app)


How it Works
============
You will need to provide the following callbacks:

    `~RoleRouteBasedACL.user_loader` callback.
    This callback is used to reload the user object from the user ID stored in the
    session. It should take the `unicode` ID of a user, and return the
    corresponding user object. For example::

        @rrbac.set_user_loader
        def load_user(user_id):
            return User.get(user_id)

    It should return `None` (**not raise an exception**) if the ID is not valid.
    (Will be treated as an anonymous user)


    `~RoleRouteBasedACL.set_auth_fail_hook` callback.
    This callback is called when the authorization fails. Defaults to abort(403).
    For example::

        @rrbac.set_auth_failed_hook
        def permission_denied_hook():
            abort('User is not authorized!', 403)

    `~RoleRouteBasedACL.as_role_model` decorator.
    This decorator is used to set the model to be used for storing the roles.
    For example::

        @rrbac.as_role_model
        class Role(db.Model, ACLRoleMixin):
            __tablename__ = 'roles'

            id = db.Column(db.Integer, nullable=False, primary_key=True)
            name = db.Column(db.String(128), nullable=False)
            deleted_at = db.Column(db.DateTime, default=None, nullable=True)


    `~RoleRouteBasedACL.as_role_model` decorator.
    This decorator is used to set the model to be used for storing the roles.
    For example::

        @rrbac.as_role_model
        class Role(db.Model, ACLRoleMixin):
            __tablename__ = 'roles'

            id = db.Column(db.Integer, nullable=False, primary_key=True)
            name = db.Column(db.String(128), nullable=False)
            deleted_at = db.Column(db.DateTime, default=None, nullable=True)


    `~RoleRouteBasedACL.as_role_model` decorator.
    This decorator is used to set the model to be used for storing the roles.
    For example::

        @rrbac.as_role_model
        class Role(db.Model, ACLRoleMixin):
            __tablename__ = 'roles'

            id = db.Column(db.Integer, nullable=False, primary_key=True)
            name = db.Column(db.String(128), nullable=False)
            deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    `~RoleRouteBasedACL.as_route_model` decorator.
    This decorator is used to set the model to be used for storing the routes.
    For example::

        @rrbac.as_route_model
        class Route(db.Model, ACLRouteMixin):
            __tablename__ = 'routes'

            id = db.Column(db.Integer, nullable=False, primary_key=True)
            method = db.Column(db.String(10), nullable=False)
            rule = db.Column(db.String(255), nullable=False)
            deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    `~RoleRouteBasedACL.as_user_model` decorator.
    This decorator is used to set the model to be used for storing the users.
    For example::

        @rrbac.as_user_model
        class User(db.Model, ACLUserMixin, UserMixin):
            __tablename__ = 'users'

            id = db.Column(db.Integer, nullable=False, primary_key=True)
            name = db.Column(db.String(128), nullable=False)
            deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    `~RoleRouteBasedACL.as_user_role_map_model` decorator.
    This decorator is used to set the association class
    to be used for storing the user role mappings.
    For example::

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

    `~RoleRouteBasedACL.as_role_route_map_model` decorator.
    This decorator is used to set the association class
    to be used for storing the role route mappings.
    For example::

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


Your User Class
===============
The class that you use to represent users needs to implement these properties
and methods:

`is_authenticated`
    This property should return `True` if the user is authenticated, i.e. they
    have provided valid credentials. (Only authenticated users will fulfill
    the criteria of `login_required`.)

To make implementing a user class easier, you can inherit from `UserMixin`,
which provides default implementations for all of these properties and methods.
(It's not required, though.)
This class should also inherit sqlalchemy's Model class (db.Model).
Check test.py for example implementation


Your Role Class
===============
The class that you use to represent roles needs to implement these properties
and methods:

`is_deleted`
    This property should return `True` if the user is deleted

You can inherit from `ACLRoleMixin`, which provides default implementations
for all of these properties and methods.
(It's not required, though.)
This class should also inherit sqlalchemy's Model class (db.Model).
Check test.py for example implementation


Your Route Class
===============
The class that you use to represent routes (paths/rules) needs to implement
these properties and methods:

`is_deleted`
    This property should return `True` if the user is deleted

`get_method`
    This property should return the request method for this rule

`get_rule`
    This property should return the url rule for which this route entry was
    created.

You can inherit from `ACLRouteMixin`, which provides default implementations
for all of these properties and methods.
(It's not required, though.)
This class should also inherit sqlalchemy's Model class (db.Model).
Check test.py for example implementation


Your UserRoleMap Class
===============
The class that you use to represent the mapping between user and role.
This is an association class and it needs to implement these properties and methods:

`is_deleted`
    This property should return `True` if the user is deleted

`get_id`
    This property should return the id for this entry

`role`
    The role attached to this map entry

`user`
    The user attached to this map entry

You can inherit from `ACLUserRoleMapMixin`, which provides default implementations
for all of these properties and methods.
(It's not required, though.)
This class should also inherit sqlalchemy's Model class (db.Model).
Check test.py for example implementation


Your RoleRouteMap Class
===============
The class that you use to represent the mapping between route and role.
This is an association class and it needs to implement these properties and methods:

`is_deleted`
    This property should return `True` if the user is deleted

`get_id`
    This property should return the id for this entry

`role`
    The role attached to this map entry

`route`
    The route attached to this map entry

You can inherit from `ACLRoleRouteMapMixin`, which provides default implementations
for all of these properties and methods.
(It's not required, though.)
This class should also inherit sqlalchemy's Model class (db.Model).
Check test.py for example implementation


User Object Helpers
-------------------
.. autoclass:: ACLUserMixin
   :members:
