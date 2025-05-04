import asyncio
import functools
from typing import Optional, Tuple
import click

from dbus_fast.constants import BusType

from openhydroponics.base.endpoint import Endpoint, EndpointClass
from openhydroponics.dbus import NodeManager, Node


class KeyValueType(click.ParamType):
    name = "key=value"

    def convert(
        self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> Tuple[str, str]:
        """
        Parses a 'key=value' string into a (key, value) tuple.
        """
        try:
            # Split only on the first '='
            key, val = value.split("=", 1)
            key = key.strip()
            val = val.strip()
            if not key or not val:  # Ensure neither part is empty after stripping
                raise ValueError("Both key and value are required.")
            return key, val
        except ValueError:
            # Use self.fail for Click-specific error handling
            self.fail(
                f"'{value}' is not a valid key=value string.",
                param,
                ctx,
            )


def make_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def get_node_manager(ctx) -> NodeManager:
    """
    Get the NodeManager instance from the context.
    """
    node_manager = ctx.obj.get("node_manager")
    if not node_manager:
        node_manager = NodeManager(bus_type=ctx.obj["bus_type"])
        ctx.obj["node_manager"] = node_manager
    return node_manager


CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    auto_envvar_prefix="HYPO",
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--node",
    type=click.UUID,
    help="Node UUID. If not set, this is read from the environmental variable HYPO_NODE",
)
@click.option(
    "--bus",
    type=click.Choice(["system", "session"], case_sensitive=False),
    default="system",
    help="Select the dbus bus to connect to.",
)
@click.pass_context
def cli(ctx, node, bus):
    ctx.ensure_object(dict)
    ctx.obj["node"] = node
    if bus == "system":
        ctx.obj["bus_type"] = BusType.SYSTEM
    else:
        ctx.obj["bus_type"] = BusType.SESSION


@cli.group()
def config():
    """Get and set node configuration"""


@config.command(name="get")
@click.argument("endpoint", type=int)
@click.argument("config", type=int)
@click.pass_context
@make_sync
async def config_get(ctx, endpoint, config):
    """Get node endpoint configuration"""
    nm = get_node_manager(ctx)
    await nm.init()

    node: Node = await nm.request_node(ctx.obj["node"])
    if not node:
        click.echo("Could not find node")
        return
    endpoint: Endpoint = node.get_endpoint(endpoint)
    if not endpoint:
        click.echo("Could not find endpoint")
        return
    try:
        config = await endpoint.get_config(config)
        for key, value in config.items():
            click.echo(f"{key}={value}")
    except Exception as e:
        click.echo(f"Error getting config: {e}")


@config.command(name="set")
@click.argument("endpoint", type=int)
@click.argument("config", type=KeyValueType(), nargs=-1, metavar="name=value")
@click.pass_context
@make_sync
async def config_set(ctx, endpoint, config):
    """Set node endpoint configuration"""
    nm = get_node_manager(ctx)
    await nm.init()

    config = dict(config)
    node: Node = await nm.request_node(ctx.obj["node"])
    if not node:
        click.echo("Could not find node")
        return
    endpoint: Endpoint = node.get_endpoint(endpoint)
    if not endpoint:
        click.echo("Could not find endpoint")
        return
    try:
        success = await endpoint.set_config(config)
        if success:
            click.echo("Configuration set successfully")
        else:
            click.echo("Failed to set configuration")
    except Exception as e:
        click.echo(f"Error setting config: {e}")


@cli.command()
@click.pass_context
@make_sync
async def ls(ctx):
    """List nodes"""
    nm = get_node_manager(ctx)
    await nm.init()
    node: Node
    async for node in nm:
        click.echo(f"Node {node.uuid}:")
        for endpoint in node:
            if endpoint.ENDPOINT_CLASS == EndpointClass.Output:
                click.echo(
                    f" - EP{endpoint.endpoint_id} {endpoint.ENDPOINT_CLASS.name}: {endpoint.__class__.__name__}"
                )
                continue
            value, scale = node.get_endpoint_value(endpoint.endpoint_id)
            click.echo(
                f" - EP{endpoint.endpoint_id} {endpoint.ENDPOINT_CLASS.name}: {endpoint.__class__.__name__} {value:.2f}"
            )


@cli.group()
@click.pass_context
@make_sync
async def output(ctx):
    """Node endpoint commands"""


@output.command(name="set")
@click.argument("endpoint", type=int)
@click.argument("value", type=float)
@click.pass_context
@make_sync
async def output_set(ctx, endpoint: int, value: float):
    """Set node endpoint output"""
    nm = get_node_manager(ctx)
    await nm.init()
    node: Node = await nm.request_node(ctx.obj["node"])
    if not node:
        click.echo("Could not find node")
        return
    endpoint: Endpoint = node.get_endpoint(endpoint)
    if not endpoint:
        click.echo("Could not find endpoint")
        return
    if endpoint.ENDPOINT_CLASS != EndpointClass.Output:
        click.echo(f"Endpoint {endpoint} is not an output endpoint")
        return
    await endpoint.set(value)


if __name__ == "__main__":
    cli()
