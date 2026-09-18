Feature: NFR-004 probe fixture
  Not a project requirement. A minimal, self-contained pair of scenarios
  used only by NFR-004.feature's own steps (see
  features/steps/nfr_004_testability_steps.py) to invoke a real, separate
  "python manage.py behave" process and observe its exit status, without
  recursively re-running the full suite this file itself lives outside of.
  Never discovered by the project's normal "python manage.py behave
  --no-input" run, since that defaults to the features/ directory and
  this file lives under tests/ instead.

  @nfr_004_probe_pass
  Scenario: A scenario that always passes
    Given a step that always succeeds
    Then the probe records success

  @nfr_004_probe_fail
  Scenario: A scenario that always fails
    Given a step that always fails
    Then the probe records success
