"""Demo application for cjm-fasthtml-settings library."""

from pathlib import Path
from fasthtml.common import *
from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script

# Step 1: Register schemas BEFORE importing routes
from cjm_fasthtml_settings.core.schemas import registry
from cjm_fasthtml_settings.core.config import get_app_config_schema

# Register the default app config schema
try:
    from cjm_fasthtml_daisyui.core.themes import DaisyUITheme
    registry.register(get_app_config_schema(
        app_title="FastHTML Settings Demo",
        server_port=5010,
        themes_enum=[theme.value for theme in DaisyUITheme],
        themes_enum_names=[theme.value.title() for theme in DaisyUITheme],
        default_theme=DaisyUITheme.LIGHT.value,
        include_theme=True
    ))
except ImportError:
    # If DaisyUI themes not available, use basic schema
    registry.register(get_app_config_schema(
        app_title="FastHTML Settings Demo",
        server_port=5010,
        include_theme=False
    ))

# Add a custom database settings schema
registry.register({
    "name": "database",
    "title": "Database Configuration",
    "menu_title": "Database",
    "description": "Database connection settings",
    "type": "object",
    "properties": {
        "db_host": {
            "type": "string",
            "title": "Database Host",
            "description": "Hostname or IP address of the database server",
            "default": "localhost"
        },
        "db_port": {
            "type": "integer",
            "title": "Database Port",
            "description": "Port number for database connection",
            "default": 5432,
            "minimum": 1,
            "maximum": 65535
        },
        "db_name": {
            "type": "string",
            "title": "Database Name",
            "description": "Name of the database to connect to",
            "default": "myapp"
        },
        "use_ssl": {
            "type": "boolean",
            "title": "Use SSL",
            "description": "Enable SSL for database connections",
            "default": True
        }
    },
    "required": ["db_host", "db_name"]
})

# Add an API settings schema
registry.register({
    "name": "api",
    "title": "API Configuration",
    "menu_title": "API",
    "description": "External API settings",
    "type": "object",
    "properties": {
        "api_key": {
            "type": "string",
            "title": "API Key",
            "description": "Your API key for external services",
            "default": ""
        },
        "api_timeout": {
            "type": "number",
            "title": "API Timeout (seconds)",
            "description": "Timeout for API requests in seconds",
            "default": 30.0,
            "minimum": 1.0,
            "maximum": 300.0
        },
        "rate_limit": {
            "type": "integer",
            "title": "Rate Limit (requests/min)",
            "description": "Maximum API requests per minute",
            "default": 60,
            "minimum": 1,
            "maximum": 10000
        }
    }
})

# Step 2: Configure routes behavior (optional)
from cjm_fasthtml_settings.routes import config
config.config_dir = Path("demo_configs")
config.default_schema = "general"

# Step 3: Import the router (AFTER registering schemas)
from cjm_fasthtml_settings.routes import settings_ar


def main():
    """Main entry point - initializes and starts the server."""

    # Create the FastHTML app
    app, rt = fast_app(
        pico=False,
        hdrs=[
            *get_daisyui_headers(),
            create_theme_persistence_script(),
        ],
        title="FastHTML Settings Demo",
        htmlkw={'data-theme': 'light'}
    )

    # Simple homepage
    @rt("/")
    def get():
        """Simple homepage with link to settings."""
        from cjm_fasthtml_tailwind.utilities.spacing import p, m
        from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
        from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align
        from cjm_fasthtml_tailwind.core.base import combine_classes
        from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes

        return Main(
            Div(
                H1("FastHTML Settings Demo",
                   cls=combine_classes(font_size._3xl, font_weight.bold, m.b(4))),
                P("This demo showcases the cjm-fasthtml-settings library.",
                  cls=combine_classes(font_size.lg, m.b(6))),
                P("Click the button below to access the settings interface.",
                  cls=combine_classes(font_size.base, m.b(8))),
                A(
                    "Open Settings",
                    href="/settings",
                    cls=combine_classes(btn, btn_colors.primary, btn_sizes.lg)
                ),
                cls=combine_classes(
                    container,
                    max_w._4xl,
                    m.x.auto,
                    p(8),
                    text_align.center
                )
            )
        )

    # Attach the settings router
    settings_ar.to_app(app)

    print("\n" + "="*60)
    print("FastHTML Settings Demo")
    print("="*60)
    print("\nRegistered settings schemas:")
    for schema_name in registry.list_schemas():
        schema = registry.get(schema_name)
        print(f"  - {schema_name}: {schema.get('title')}")
    print(f"\nConfig directory: {config.config_dir}")
    print("="*60 + "\n")

    return app


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    # Call main to initialize everything and get the app
    app = main()

    def open_browser(url):
        print(f"Opening browser at {url}")
        webbrowser.open(url)

    port = 5010
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"\nServer: http://{display_host}:{port}")
    print("\nAvailable routes:")
    print(f"  http://{display_host}:{port}/          - Homepage")
    print(f"  http://{display_host}:{port}/settings  - Settings interface")
    print("\n" + "="*60 + "\n")

    # Open browser after a short delay
    timer = threading.Timer(1.5, lambda: open_browser(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    # Start server
    uvicorn.run(app, host=host, port=port)
