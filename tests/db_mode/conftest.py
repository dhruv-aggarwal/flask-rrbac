from models import (
    Role, User, UserRoleMap, Route, RoleRouteMap
)
import pytest
from . import rrbac, app, db, tear_down


def db_data_setup():
    # Add Roles
    admin_role = Role(name='admin')
    base_role = Role(name='base')
    super_admin_role = Role(name='super_admin')
    anon_role = Role(name='Anon')
    db.session.add(admin_role)
    db.session.add(base_role)
    db.session.add(super_admin_role)
    db.session.add(anon_role)
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
    anon_route = Route(rule='/uncovered_route', method='GET')
    db.session.add(get_route)
    db.session.add(post_route)
    db.session.add(anon_route)
    db.session.commit()

    # Add Role Route Map
    db.session.add(RoleRouteMap(role=admin_role, route=get_route))
    db.session.add(RoleRouteMap(role=super_admin_role, route=get_route))
    db.session.add(RoleRouteMap(role=super_admin_role, route=post_route))
    db.session.add(RoleRouteMap(role=anon_role, route=anon_route))
    db.session.commit()
    db.session.refresh(base_user)
    db.session.refresh(admin_user)
    db.session.refresh(super_admin_user)
    rrbac.init_app(app)
    return [base_user, admin_user, super_admin_user]


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
    base_user, admin_user, super_admin_user = db_data_setup()

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
                'method': 'HEAD',
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
                'method': 'HEAD',
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
                'method': 'HEAD',
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
                'url_rule': '/uncovered_route',
                'user': None,
                'function': 'uncovered_route'
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
                'method': 'HEAD',
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
        },
        {
            'input': {
                'method': 'HEAD',
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
    Test Cases:
    1. Making POST request on covered route as admin user.
    2. Making GET request on covered route as base user.
    3. Making GET request on covered route as anonymous user.
    4. Making POST request on covered route as anonymous user.
    """

    db.create_all()
    base_user, admin_user, super_admin_user = db_data_setup()

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
        },
        {
            'input': {
                'method': 'GET',
                'url_rule': '/covered_route',
                'user': None,
                'function': 'covered_route'
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
                'function': 'covered_route'
            },
            'output': {
                'status_code': 403
            }
        }
    ]
    request.addfinalizer(tear_down)
    return data_to_send


def db_data_setup_regex():
    # Add Roles
    base_role = Role(name='base')
    admin_role = Role(name='admin_regex')
    db.session.add(base_role)
    db.session.add(admin_role)
    db.session.commit()

    # Add Users
    base_user = User(name='base')
    admin_user = User(name='admin_regex')
    db.session.add(base_user)
    db.session.add(admin_user)
    db.session.commit()

    # Attach role to users
    db.session.add(UserRoleMap(role=base_role, user=base_user))
    db.session.add(UserRoleMap(role=admin_role, user=admin_user))
    db.session.commit()

    # Add Routes

    # Route for admin
    all_get_route = Route(rule='.+', method='GET')
    all_post_route = Route(rule='.+', method='POST')

    # Route for get of all covered route with ids
    int_route = Route(rule='/covered_route/\d+', method='GET')
    # Route for posting on covered_route, id: 1
    specific_id_route = Route(rule='/covered_route/1', method='POST')

    # base user can also do a get of the covered route
    exact_route = Route(rule='/covered_route', method='GET')
    db.session.add(all_get_route)
    db.session.add(all_post_route)
    db.session.add(int_route)
    db.session.add(specific_id_route)
    db.session.add(exact_route)
    db.session.commit()

    # Add Role Route Map
    # Admin is allowed to get, post all endpoints
    db.session.add(RoleRouteMap(role=admin_role, route=all_post_route))
    db.session.add(RoleRouteMap(role=admin_role, route=all_get_route))
    # base user is allowed to get any covered route id but post only on id 1
    db.session.add(RoleRouteMap(role=base_role, route=int_route))
    db.session.add(RoleRouteMap(role=base_role, route=specific_id_route))
    # base user can also do a get of the covered route
    db.session.add(RoleRouteMap(role=base_role, route=exact_route))
    db.session.commit()
    db.session.refresh(base_user)
    db.session.refresh(admin_user)
    rrbac.init_app(app)
    return [base_user, admin_user]


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
    base_user, admin_user = db_data_setup_regex()

    data_to_send = [
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
                'user': admin_user,
                'function': 'covered_route'
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
                'function': 'number_covered_route'
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
                'function': 'number_covered_route'
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
                'url_rule': '/covered_route/1',
                'user': base_user,
                'function': 'number_covered_route'
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
                'function': 'number_covered_route'
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
                'function': 'number_covered_route'
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
def fixture_regex_failure(request):
    """
    Test Cases:
    1. POST covered_route/2 for base user
    2. POST covered_route for base user
    3. GET uncovered_route for base user
    """

    db.create_all()
    base_user, admin_user = db_data_setup_regex()

    data_to_send = [
        {
            'input': {
                'method': 'POST',
                'url_rule': '/covered_route/2',
                'user': base_user,
                'function': 'number_covered_route'
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
                'function': 'covered_route'
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
                'function': 'uncovered_route'
            },
            'output': {
                'status_code': 403
            }
        }
    ]
    request.addfinalizer(tear_down)
    return data_to_send
