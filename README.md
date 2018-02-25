# flask_rrbac
RBAC library for Flask


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


Check the source folder for detailed documentation