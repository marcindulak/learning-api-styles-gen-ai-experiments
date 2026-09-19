import asyncio


def before_scenario(context, scenario):
    # WebSocket steps (see fr_004_alerts_steps.py) need one persistent event
    # loop per scenario: Channels' consumer Tasks and its InMemoryChannelLayer
    # queues are bound to whichever loop first created them, so a scenario's
    # connect/trigger/receive calls must all run on the same loop rather than
    # each spinning up their own via asyncio.run()/async_to_sync(), which
    # would leave the consumer listening on a queue nothing else can reach.
    context.ws_loop = asyncio.new_event_loop()


def after_scenario(context, scenario):
    # Disconnecting removes each consumer's channel from its alert group
    # before the loop closes; skipping this would leave a stale channel
    # bound to a now-dead loop in the group, and a later scenario reusing
    # the same city (hence the same group name) would crash trying to wake
    # it via group_send.
    for communicator in getattr(context, "ws_clients", {}).values():
        context.ws_loop.run_until_complete(communicator.disconnect())
    context.ws_loop.close()
