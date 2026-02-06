def before_scenario(context, scenario):
    """Set up before each scenario."""
    pass


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Clean up WebSocket connections
    if hasattr(context, "communicator") and hasattr(context, "event_loop"):
        import asyncio

        async def disconnect():
            await context.communicator.disconnect()

        context.event_loop.run_until_complete(disconnect())
        context.event_loop.close()
