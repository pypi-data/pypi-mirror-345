from collections.abc import Callable

import pytest
from loguru import logger

from universal_mcp.applications import app_from_slug


@pytest.mark.parametrize(
    "app_name",
    [
        "ahrefs",
        "cal-com-v2",
        "calendly",
        "clickup",
        "coda",
        "crustdata",
        "e2b",
        "elevenlabs",
        "falai",
        "figma",
        "firecrawl",
        "github",
        "gong",
        "google-calendar",
        "google-docs",
        "google-drive",
        "google-mail",
        "google-sheet",
        "hashnode",
        "heygen",
        "mailchimp",
        "markitdown",
        "neon",
        "notion",
        "perplexity",
        "reddit",
        "replicate",
        "resend",
        "retell",
        "rocketlane",
        "serpapi",
        "shortcut",
        "spotify",
        "supabase",
        "tavily",
        "wrike",
        "youtube",
        "zenquotes",
    ],
)
def test_application(app_name):
    app = app_from_slug(app_name)(integration=None)
    assert app is not None
    assert app.name == app_name
    tools = app.list_tools()
    logger.info(f"Tools for {app_name}: {tools}")
    assert len(tools) > 0
    assert isinstance(tools[0], Callable)
    important_tools = []
    for tool in tools:
        assert tool.__name__ is not None
        assert tool.__doc__ is not None
        if "important" in tool.__doc__:
            important_tools.append(tool.__name__)
    assert len(important_tools) > 0
