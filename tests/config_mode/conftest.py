from models import (
    Role, User, UserRoleMap
)
import pytest
from . import rrbac, app, db, tear_down


def config_data_setup():
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

    db.session.refresh(base_user)
    db.session.refresh(admin_user)
    db.session.refresh(super_admin_user)
    app.config['RRBAC_ROLE_ROUTE_MAP'] = {
        admin_role.name: {
            'GET': {'/covered_route', '/uncovered_route'},
            'POST': {'/uncovered_route'}
        },
        super_admin_role.name: {
            'GET': {'/covered_route', '/uncovered_route'},
            'POST': {'/covered_route', '/uncovered_route'}
        },
        'Anon': {
            'GET': {'/uncovered_route'},
            'POST': {}
        }
    }
    app.config['RRBAC_ANONYMOUS_ROLE'] = 'Anon'
    rrbac.init_app(app)
    return [base_user, admin_user, super_admin_user]


def config_data_setup_regex():
    # Add Roles
    admin_role = Role(name='admin_regex')
    base_role = Role(name='base')
    db.session.add(admin_role)
    db.session.add(base_role)
    db.session.commit()

    # Add Users
    admin_user = User(name='admin_regex')
    base_user = User(name='base')
    db.session.add(admin_user)
    db.session.add(base_user)
    db.session.commit()

    # Attach role to users
    db.session.add(UserRoleMap(role=admin_role, user=admin_user))
    db.session.add(UserRoleMap(role=base_role, user=base_user))
    db.session.commit()

    db.session.refresh(base_user)
    db.session.refresh(admin_user)
    app.config['RRBAC_ROLE_ROUTE_MAP'] = {
        admin_role.name: {
            'GET': {'.+'},
            'POST': {'.+'}
        },
        base_role.name: {
            'GET': {'/covered_route/\d+', '/covered_route'},
            'POST': {'/covered_route/1'}
        }
    }
    app.config['RRBAC_ANONYMOUS_ROLE'] = 'Anon'
    rrbac.init_app(app)
    return app, base_user, admin_user


@pytest.fixture(scope='function')
def fixture_success(request):
    """
    Test Cases:
    1. Hitting uncovered route as base user (logged in flow). Will return 200
    since uncovered route is an open endpoint and thus Anonymous users can also
    access it.
    2. Hitting uncovered route as base user and HEAD request
    3. Hitting uncovered route as admin user and HEAD request
    4. Hitting uncovered route as super admin user and GET request
    5. Hitting uncovered route as super admin user and HEAD request
    6. Hitting uncovered route as anonymous user and GET request
    7. Hitting uncovered route as anonymous user and HEAD request
    8. Hitting covered route as admin user and GET request
    9. Hitting covered route as admin user and HEAD request
    10. Hitting covered route as super admin user and POST request
    11. Hitting covered route as super admin user and GET request
    12. Hitting covered route as super admin user and HEAD request
    """

    db.create_all()
    base_user, admin_user, super_admin_user = config_data_setup()

    data_to_send = [
        {
            'input': {
                'method': 'GET',
                'url_rule': '/uncovered_route',
                'user': base_user,
                'function': app.view_functions['uncovered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'HEAD',
                'url_rule': '/uncovered_route',
                'user': base_user,
                'function': app.view_functions['uncovered_route']
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
                'function': app.view_functions['uncovered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'HEAD',
                'url_rule': '/uncovered_route',
                'user': admin_user,
                'function': app.view_functions['uncovered_route']
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
                'function': app.view_functions['uncovered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'HEAD',
                'url_rule': '/uncovered_route',
                'user': super_admin_user,
                'function': app.view_functions['uncovered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/uncovered_route',
                'user': None,
                'function': app.view_functions['uncovered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'HEAD',
                'url_rule': '/uncovered_route',
                'user': None,
                'function': app.view_functions['uncovered_route']
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
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'HEAD',
                'url_rule': '/covered_route',
                'user': admin_user,
                'function': app.view_functions['covered_route']
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
                'function': app.view_functions['covered_route']
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
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'HEAD',
                'url_rule': '/covered_route',
                'user': super_admin_user,
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 200
            }
        }
    ]
    request.addfinalizer(tear_down)
    return app, data_to_send


@pytest.fixture(scope='function')
def fixture_failure(request):
    """
    Test Cases:
    1. Making POST request on covered route as admin user.
    2. Making GET request on covered route as base user.
    3. Making GET request on covered route as anonymous user.
    4. Making POST request on covered route as anonymous user.
    """

    db.create_all()
    base_user, admin_user, super_admin_user = config_data_setup()

    data_to_send = [
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route',
                'user': admin_user,
                'function': app.view_functions['covered_route']
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
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 403
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route',
                'user': None,
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 403
            }
        },
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route',
                'user': None,
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 403
            }
        }
    ]
    request.addfinalizer(tear_down)
    return app, data_to_send


@pytest.fixture(scope='function')
def fixture_regex_success(request):
    """
    Test Cases:
    1. GET covered_route for admin
    2. POST covered_route for admin
    3. GET covered_route/1 for admin
    4. POST covered_route/1 for admin
    5. GET uncovered_route for admin
    6. GET covered_route/1 for base user
    7. GET covered_route/2 for base user
    8. POST covered_route/1 for base user
    9. GET covered_route for base user
    """

    db.create_all()
    app, base_user, admin_user = config_data_setup_regex()

    data_to_send = [
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route',
                'user': admin_user,
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route',
                'user': admin_user,
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route/1',
                'user': admin_user,
                'function': app.view_functions['number_covered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route/1',
                'user': admin_user,
                'function': app.view_functions['number_covered_route']
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
                'function': app.view_functions['uncovered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route/1',
                'user': base_user,
                'function': app.view_functions['number_covered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route/2',
                'user': base_user,
                'function': app.view_functions['number_covered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route/1',
                'user': base_user,
                'function': app.view_functions['number_covered_route']
            },
            'output': {
                'status_code': 200
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route',
                'user': base_user,
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 200
            }
        }
    ]
    request.addfinalizer(tear_down)
    return app, data_to_send


@pytest.fixture(scope='function')
def fixture_regex_failure(request):
    """
    Test Cases:
    1. POST covered_route/2 for base user
    2. POST covered_route for base user
    3. GET uncovered_route for base user
    """

    db.create_all()
    app, base_user, admin_user = config_data_setup_regex()

    data_to_send = [
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route/2',
                'user': base_user,
                'function': app.view_functions['number_covered_route']
            },
            'output': {
                'status_code': 403
            }
        },
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route',
                'user': base_user,
                'function': app.view_functions['covered_route']
            },
            'output': {
                'status_code': 403
            }
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/uncovered_route',
                'user': base_user,
                'function': app.view_functions['uncovered_route']
            },
            'output': {
                'status_code': 403
            }
        }
    ]
    request.addfinalizer(tear_down)
    return app, data_to_send
