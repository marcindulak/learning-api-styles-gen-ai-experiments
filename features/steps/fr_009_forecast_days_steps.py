from behave import then
from common_steps import _response_body


@then("the response body contains {count:d} forecast entries")
def step_then_forecast_entry_count(context, count):
    assert len(_response_body(context)) == count


@then("the response body contains an error message stating the maximum is 7 days")
def step_then_error_message_max_seven_days(context):
    assert "maximum is 7 days" in _response_body(context)["error"]
