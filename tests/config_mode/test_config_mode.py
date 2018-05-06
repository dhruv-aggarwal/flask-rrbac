import pytest
from . import uncovered_route, covered_route, number_covered_route
from werkzeug.exceptions import Forbidden


class TestRRBAC2():
    @pytest.mark.usefixtures("fixture_success")
    def test_success(
        self, fixture_success
    ):
        app = fixture_success[0]
        fixture_success = fixture_success[1]
        for index, data in enumerate(fixture_success):
            print '\nScenario {} Started'.format(index + 1)
            with app.test_request_context(
                data['input']['url_rule'], method=data['input']['method']
            ) as request_ctx:
                if data['input']['user']:
                    request_ctx.user = data['input']['user']
                output = eval(data['input']['function'])()
                assert output.status_code == data['output']['status_code']
                print '\nScenario {} Passed'.format(index + 1)

    @pytest.mark.usefixtures("fixture_failure")
    def test_failure(self, fixture_failure):
        app = fixture_failure[0]
        fixture_failure = fixture_failure[1]
        for index, data in enumerate(fixture_failure):
            print '\nScenario {} Started'.format(index + 1)
            with app.test_request_context(
                data['input']['url_rule'],
                method=data['input']['method']
            ) as request_ctx:
                if data['input']['user']:
                    request_ctx.user = data['input']['user']
                try:
                    result = 0
                    eval(data['input']['function'])()
                except Forbidden:
                    result = 1
                finally:
                    assert result
                    print '\nScenario {} Passed'.format(index + 1)

    @pytest.mark.usefixtures("fixture_regex_success")
    def test_regex_success(
        self, fixture_regex_success
    ):
        app = fixture_regex_success[0]
        fixture_success = fixture_regex_success[1]
        for index, data in enumerate(fixture_success):
            print '\nScenario {} Started'.format(index + 1)
            with app.test_request_context(
                data['input']['url_rule'], method=data['input']['method']
            ) as request_ctx:
                if data['input']['user']:
                    request_ctx.user = data['input']['user']
                output = eval(data['input']['function'])()
                assert output.status_code == data['output']['status_code']
                print '\nScenario {} Passed'.format(index + 1)

    @pytest.mark.usefixtures("fixture_regex_failure")
    def test_regex_failure(self, fixture_regex_failure):
        app = fixture_regex_failure[0]
        fixture_regex_failure = fixture_regex_failure[1]
        for index, data in enumerate(fixture_regex_failure):
            print '\nScenario {} Started'.format(index + 1)
            with app.test_request_context(
                data['input']['url_rule'],
                method=data['input']['method']
            ) as request_ctx:
                if data['input']['user']:
                    request_ctx.user = data['input']['user']
                try:
                    result = 0
                    eval(data['input']['function'])()
                except Forbidden:
                    result = 1
                finally:
                    assert result
                    print '\nScenario {} Passed'.format(index + 1)
