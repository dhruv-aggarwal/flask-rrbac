import pytest
from . import app
from werkzeug.exceptions import Forbidden


class TestRRBAC():
    @pytest.mark.usefixtures("fixture_success")
    def test_success(self, fixture_success):
        for index, data in enumerate(fixture_success):
            print '\nScenario {} Started'.format(index + 1)
            with app.test_request_context(
                data['input']['url_rule'], method=data['input']['method']
            ) as request_ctx:
                if data['input']['user']:
                    request_ctx.user = data['input']['user']
                output = data['input']['function']()
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
                if data['input']['user']:
                    request_ctx.user = data['input']['user']
                try:
                    result = 0
                    data['input']['function']()
                except Forbidden:
                    result = 1
                finally:
                    assert result
                    print '\nScenario {} Passed'.format(index + 1)

    @pytest.mark.usefixtures("fixture_regex_success")
    def test_regex_success(self, fixture_regex_success):
        for index, data in enumerate(fixture_regex_success):
            print '\nScenario {} Started'.format(index + 1)
            with app.test_request_context(
                data['input']['url_rule'], method=data['input']['method']
            ) as request_ctx:
                if data['input']['user']:
                    request_ctx.user = data['input']['user']
                output = data['input']['function']()
                assert output.status_code == data['output']['status_code']
                print '\nScenario {} Passed'.format(index + 1)

    @pytest.mark.usefixtures("fixture_regex_failure")
    def test_regex_failure(self, fixture_regex_failure):
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
                    data['input']['function']()
                except Forbidden:
                    result = 1
                finally:
                    assert result
                    print '\nScenario {} Passed'.format(index + 1)
