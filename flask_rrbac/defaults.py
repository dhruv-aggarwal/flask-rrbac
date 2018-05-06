"""
Determines if the role-route mapping should be picked from the
app environment or the DB.

The keys are routes (rules) and the value if a map of request method and the
set of roles allowed to access the rule-method combination
Example:
    app.config['RRBAC_ROUTE_ROLE_MAP'] = {
        '/route1': {
            'GET': {'admin', 'super_admin'},
            'POST': {'super_admin'}
        },
        '/uncovered_route': {
            'GET': {'admin', 'super_admin', 'Anon'}
        }
    }
"""
RRBAC_ROUTE_ROLE_MAP = {}

"""
Determines if static files should be mapped to Anonymous user role or not.
If True, they will be mapped by default.

Example:
    app.config['RRBAC_ALLOW_STATIC'] = True
"""
# RRBAC_ALLOW_STATIC = True

"""
Determines the name of the Anonymous role. This name will be matched in the
db/config while fetching the anonymous routes.

Example:
    app.config['RRBAC_ANONYMOUS_ROLE'] = 'ANON'
"""
RRBAC_ANONYMOUS_ROLE = 'Anonymous'

"""
Methods which mean the same (have the same level of access).
This is to be interpreted as:
If the user has hit method1, then it is to be treated as if he has hit the
alternative methods as far as ACL is concerned.

Example:
    app.config['RRACL_METHOD_ALTERNATES'] = {
        'HEAD': 'GET',
        'OPTIONS': 'GET'
    }
"""
RRACL_METHOD_ALTERNATES = {
    'HEAD': 'GET',
    'OPTIONS': 'GET'
}
