from behave import given, then


@given("a step that always succeeds")
def step_given_always_succeeds(context):
    pass


@given("a step that always fails")
def step_given_always_fails(context):
    assert False, "deliberate probe failure"


@then("the probe records success")
def step_then_records_success(context):
    pass
