# Weather Forecast Service

See [REQUIREMENTS.md](REQUIREMENTS.md) for the project's requirements and its
main documented build/run/test commands.

## Testing

The integration test suite (`docker compose exec app python manage.py behave
--no-input`, per REQUIREMENTS.md) excludes scenarios tagged `@host-verified`:
these test the "app" container's own lifecycle (stopping/restarting it), so
they cannot run from a behave process launched inside that same container --
it would be killed by the very command it is testing. Those scenarios are
covered by standalone scripts instead, run directly on the host/CI runner:

```
docker compose up --detach --wait
tests/single_unit_lifecycle.sh
```
