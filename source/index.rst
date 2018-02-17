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

- Impose a particular database or other storage method on you. You are
  entirely in charge of how the user is loaded.
- Create the reqiured models for you.
- Make the required entries for you in the database.

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

Your User Class
===============
The class that you use to represent users needs to implement these properties
and methods:

`is_authenticated`
    This property should return `True` if the user is authenticated, i.e. they
    have provided valid credentials. (Only authenticated users will fulfill
    the criteria of `login_required`.)

`is_active`
    This property should return `True` if this is an active user - in addition
    to being authenticated, they also have activated their account, not been
    suspended, or any condition your application has for rejecting an account.
    Inactive accounts may not log in (without being forced of course).

`is_anonymous`
    This property should return `True` if this is an anonymous user. (Actual
    users should return `False` instead.)

`get_id()`
    This method must return a `unicode` that uniquely identifies this user,
    and can be used to load the user from the `~LoginManager.user_loader`
    callback. Note that this **must** be a `unicode` - if the ID is natively
    an `int` or some other type, you will need to convert it to `unicode`.

To make implementing a user class easier, you can inherit from `UserMixin`,
which provides default implementations for all of these properties and methods.
(It's not required, though.)

Login Example
=============

Once a user has authenticated, you log them in with the `login_user`
function.

    For example:

.. code-block:: python

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Here we use a class of some kind to represent and validate our
        # client-side form data. For example, WTForms is a library that will
        # handle this for us, and we use a custom LoginForm to validate.
        form = LoginForm()
        if form.validate_on_submit():
            # Login and validate the user.
            # user should be an instance of your `User` class
            login_user(user)

            flask.flash('Logged in successfully.')

            next = flask.request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return flask.abort(400)

            return flask.redirect(next or flask.url_for('index'))
        return flask.render_template('login.html', form=form)

It's that simple. You can then access the logged-in user with the
`current_user` proxy, which is available in every template::

    {% if current_user.is_authenticated %}
      Hi {{ current_user.name }}!
    {% endif %}

Views that require your users to be logged in can be
decorated with the `login_required` decorator::

    @app.route("/settings")
    @login_required
    def settings():
        pass

When the user is ready to log out::

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(somewhere)

They will be logged out, and any cookies for their session will be cleaned up.


API Documentation
=================
This documentation is automatically generated from Flask-Login's source code.


User Object Helpers
-------------------
.. autoclass:: ACLUserMixin
   :members:
