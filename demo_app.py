"""Comprehensive demo application for cjm-fasthtml-settings library.

This demo tests all library features:
- Basic schema registration
- SchemaGroup (collapsible sidebar sections)
- Plugin integration with UnifiedPluginRegistry
- Configuration persistence
- Theme integration
- MasterDetail pattern integration (from cjm-fasthtml-interactions)
"""

from pathlib import Path
from fasthtml.common import *
from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script

print("\n" + "="*70)
print("Initializing cjm-fasthtml-settings Demo")
print("="*70)

# Step 1: Register schemas BEFORE importing routes
from cjm_fasthtml_settings.core.schemas import registry
from cjm_fasthtml_settings.core.schema_group import SchemaGroup
from cjm_fasthtml_settings.core.config import get_app_config_schema
from cjm_fasthtml_plugins.core.metadata import PluginMetadata
from cjm_fasthtml_plugins.core.registry import UnifiedPluginRegistry
from dataclasses import dataclass

# Register the default app config schema
print("\n[1/5] Registering application configuration schema...")
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
    print("  ✓ App config with theme support registered")
except ImportError:
    registry.register(get_app_config_schema(
        app_title="FastHTML Settings Demo",
        server_port=5010,
        include_theme=False
    ))
    print("  ✓ App config (no theme support) registered")

# Test Feature 1: Basic individual schemas
print("\n[2/5] Registering individual schemas...")
registry.register({
    "name": "notifications",
    "title": "Notification Settings",
    "menu_title": "Notifications",
    "description": "Configure application notifications",
    "type": "object",
    "properties": {
        "email_enabled": {
            "type": "boolean",
            "title": "Email Notifications",
            "description": "Receive notifications via email",
            "default": True
        },
        "email_address": {
            "type": "string",
            "title": "Email Address",
            "description": "Email address for notifications",
            "default": "user@example.com"
        },
        "notification_frequency": {
            "type": "string",
            "title": "Notification Frequency",
            "description": "How often to send notifications",
            "default": "daily",
            "enum": ["realtime", "hourly", "daily", "weekly"],
            "enumNames": ["Real-time", "Every Hour", "Daily Digest", "Weekly Summary"]
        }
    }
})
print("  ✓ Notifications schema registered")

# Test Feature 2: SchemaGroup (collapsible sections)
print("\n[3/5] Registering schema groups (collapsible sections)...")
database_group = SchemaGroup(
    name="database",
    title="Database Settings",
    schemas={
        "connection": {
            "name": "connection",
            "title": "Connection Settings",
            "menu_title": "Connection",
            "description": "Database connection configuration",
            "type": "object",
            "properties": {
                "db_host": {
                    "type": "string",
                    "title": "Host",
                    "description": "Database server hostname",
                    "default": "localhost"
                },
                "db_port": {
                    "type": "integer",
                    "title": "Port",
                    "description": "Database server port",
                    "default": 5432,
                    "minimum": 1,
                    "maximum": 65535
                },
                "db_name": {
                    "type": "string",
                    "title": "Database Name",
                    "default": "myapp"
                }
            }
        },
        "performance": {
            "name": "performance",
            "title": "Performance Settings",
            "menu_title": "Performance",
            "description": "Database performance tuning",
            "type": "object",
            "properties": {
                "pool_size": {
                    "type": "integer",
                    "title": "Connection Pool Size",
                    "description": "Maximum number of database connections",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                },
                "query_timeout": {
                    "type": "number",
                    "title": "Query Timeout (seconds)",
                    "default": 30.0,
                    "minimum": 1.0
                },
                "enable_caching": {
                    "type": "boolean",
                    "title": "Enable Query Caching",
                    "default": True
                }
            }
        },
        "backup": {
            "name": "backup",
            "title": "Backup Settings",
            "menu_title": "Backup",
            "description": "Automated backup configuration",
            "type": "object",
            "properties": {
                "auto_backup": {
                    "type": "boolean",
                    "title": "Enable Auto Backup",
                    "default": False
                },
                "backup_schedule": {
                    "type": "string",
                    "title": "Backup Schedule",
                    "default": "daily",
                    "enum": ["hourly", "daily", "weekly", "monthly"],
                    "enumNames": ["Every Hour", "Daily", "Weekly", "Monthly"]
                },
                "retention_days": {
                    "type": "integer",
                    "title": "Retention Period (days)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 365
                }
            }
        }
    },
    default_open=True,
    description="Database connection, performance, and backup settings"
)
registry.register(database_group)
print("  ✓ Database group registered (3 sub-schemas)")

# Another schema group for API settings
api_group = SchemaGroup(
    name="api",
    title="API Settings",
    schemas={
        "authentication": {
            "name": "authentication",
            "title": "API Authentication",
            "menu_title": "Authentication",
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "title": "API Key",
                    "description": "Your API key for external services",
                    "default": ""
                },
                "use_oauth": {
                    "type": "boolean",
                    "title": "Use OAuth",
                    "default": False
                }
            }
        },
        "rate_limiting": {
            "name": "rate_limiting",
            "title": "Rate Limiting",
            "menu_title": "Rate Limits",
            "type": "object",
            "properties": {
                "requests_per_minute": {
                    "type": "integer",
                    "title": "Requests Per Minute",
                    "default": 60,
                    "minimum": 1,
                    "maximum": 10000
                },
                "burst_size": {
                    "type": "integer",
                    "title": "Burst Size",
                    "description": "Maximum burst of requests allowed",
                    "default": 10,
                    "minimum": 1
                }
            }
        }
    },
    default_open=False,
    description="API authentication and rate limiting"
)
registry.register(api_group)
print("  ✓ API group registered (2 sub-schemas)")

# Test Feature 3: Plugin integration
print("\n[4/5] Setting up plugin system...")

# Create a simple plugin manager for demo purposes
@dataclass
class DemoPluginData:
    """Simple plugin data holder for demo."""
    name: str
    version: str
    title: str
    description: str
    config_schema: dict

class DemoPluginManager:
    """Simple plugin manager for demonstration."""

    def __init__(self, plugins: list[DemoPluginData]):
        self._plugins = {p.name: p for p in plugins}

    def discover_plugins(self) -> list[DemoPluginData]:
        """Return all registered plugins."""
        return list(self._plugins.values())

    def get_plugin_config_schema(self, name: str) -> dict:
        """Get config schema for a plugin."""
        plugin = self._plugins.get(name)
        return plugin.config_schema if plugin else {}

# Define demo plugins
export_plugins = [
    DemoPluginData(
        name="csv_exporter",
        version="1.0.0",
        title="CSV Exporter",
        description="Export data to CSV format",
        config_schema={
            "type": "object",
            "title": "CSV Export Settings",
            "properties": {
                "delimiter": {
                    "type": "string",
                    "title": "Delimiter",
                    "description": "Character to separate fields",
                    "default": ",",
                    "enum": [",", ";", "\t", "|"],
                    "enumNames": ["Comma (,)", "Semicolon (;)", "Tab", "Pipe (|)"]
                },
                "include_headers": {
                    "type": "boolean",
                    "title": "Include Headers",
                    "default": True
                },
                "quote_all_fields": {
                    "type": "boolean",
                    "title": "Quote All Fields",
                    "default": False
                }
            }
        }
    ),
    DemoPluginData(
        name="json_exporter",
        version="1.0.0",
        title="JSON Exporter",
        description="Export data to JSON format",
        config_schema={
            "type": "object",
            "title": "JSON Export Settings",
            "properties": {
                "indent": {
                    "type": "integer",
                    "title": "Indentation",
                    "description": "Number of spaces for indentation",
                    "default": 2,
                    "minimum": 0,
                    "maximum": 8
                },
                "compact": {
                    "type": "boolean",
                    "title": "Compact Output",
                    "description": "Remove whitespace for smaller files",
                    "default": False
                }
            }
        }
    )
]

processing_plugins = [
    DemoPluginData(
        name="data_validator",
        version="1.2.0",
        title="Data Validator",
        description="Validate data quality",
        config_schema={
            "type": "object",
            "title": "Validation Settings",
            "properties": {
                "strict_mode": {
                    "type": "boolean",
                    "title": "Strict Mode",
                    "description": "Fail on any validation error",
                    "default": False
                },
                "max_errors": {
                    "type": "integer",
                    "title": "Maximum Errors",
                    "description": "Stop after this many errors (0 = unlimited)",
                    "default": 100,
                    "minimum": 0
                },
                "check_duplicates": {
                    "type": "boolean",
                    "title": "Check for Duplicates",
                    "default": True
                }
            }
        }
    ),
    DemoPluginData(
        name="data_cleaner",
        version="2.0.1",
        title="Data Cleaner",
        description="Clean and normalize data",
        config_schema={
            "type": "object",
            "title": "Cleaning Settings",
            "properties": {
                "remove_nulls": {
                    "type": "boolean",
                    "title": "Remove Null Values",
                    "default": True
                },
                "trim_whitespace": {
                    "type": "boolean",
                    "title": "Trim Whitespace",
                    "default": True
                },
                "normalize_case": {
                    "type": "string",
                    "title": "Normalize Text Case",
                    "default": "none",
                    "enum": ["none", "lower", "upper", "title"],
                    "enumNames": ["No Change", "Lowercase", "UPPERCASE", "Title Case"]
                }
            }
        }
    )
]

# Create unified registry and register plugin managers
plugin_registry = UnifiedPluginRegistry(config_dir=Path("demo_configs"))
plugin_registry.register_plugin_manager(
    category="export",
    manager=DemoPluginManager(export_plugins),
    display_name="Export Tools"
)
plugin_registry.register_plugin_manager(
    category="processing",
    manager=DemoPluginManager(processing_plugins),
    display_name="Data Processing"
)

total_plugins = sum(len(plugin_registry.get_plugins_by_category(cat)) for cat in plugin_registry.get_categories())
print(f"  ✓ Registered {total_plugins} plugins")
print(f"  ✓ Categories: {', '.join(plugin_registry.get_categories_with_plugins())}")

# Step 2: Configure routes behavior
print("\n[5/5] Configuring routes...")
from cjm_fasthtml_settings.routes import configure_settings, config

configure_settings(
    config_dir=Path("demo_configs"),
    default_schema="general",
    plugin_registry=plugin_registry
)

print("  ✓ Routes configured with MasterDetail pattern")
print("  ✓ Using cjm-fasthtml-interactions for UI patterns")
print("  ✓ Plugin support enabled")

# Step 3: Import the router (AFTER registering schemas and configuring)
from cjm_fasthtml_settings.routes import settings_ar

# Import styling utilities at module level
from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align
from cjm_fasthtml_tailwind.core.base import combine_classes
from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes
from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors

# Create the FastHTML app at module level
app, rt = fast_app(
    pico=False,
    hdrs=[
        *get_daisyui_headers(),
        create_theme_persistence_script(),
    ],
    title="FastHTML Settings Demo",
    htmlkw={'data-theme': 'light'}
)

# Attach the settings router
settings_ar.to_app(app)

# Define main route at module level
@rt
def index():
    """Homepage with feature showcase."""
    return Main(
        Div(
            H1("cjm-fasthtml-settings Demo",
               cls=combine_classes(font_size._4xl, font_weight.bold, m.b(4))),

            P("Comprehensive demonstration of all library features:",
              cls=combine_classes(font_size.lg, m.b(6))),

            # Feature list
            Div(
                Div(
                    Span("✓", cls=combine_classes(font_size._2xl, m.r(3))),
                    Span("Basic schema registration and configuration forms"),
                    cls=combine_classes(m.b(3))
                ),
                Div(
                    Span("✓", cls=combine_classes(font_size._2xl, m.r(3))),
                    Span("SchemaGroups with collapsible sidebar sections"),
                    cls=combine_classes(m.b(3))
                ),
                Div(
                    Span("✓", cls=combine_classes(font_size._2xl, m.r(3))),
                    Span("Plugin integration with multiple categories"),
                    cls=combine_classes(m.b(3))
                ),
                Div(
                    Span("✓", cls=combine_classes(font_size._2xl, m.r(3))),
                    Span("Configuration persistence (auto-saved to JSON)"),
                    cls=combine_classes(m.b(3))
                ),
                Div(
                    Span("✓", cls=combine_classes(font_size._2xl, m.r(3))),
                    Span("Theme integration with DaisyUI"),
                    cls=combine_classes(m.b(3))
                ),
                Div(
                    Span("✓", cls=combine_classes(font_size._2xl, m.r(3))),
                    Span("MasterDetail pattern from cjm-fasthtml-interactions"),
                    cls=combine_classes(m.b(8))
                ),
                cls=combine_classes(text_align.left, m.b(8))
            ),

            # Statistics badges
            Div(
                Span(
                    Span(f"{len(registry.list_schemas())}", cls=str(font_weight.bold)),
                    " Schema Groups",
                    cls=combine_classes(badge, badge_colors.info, m.r(2))
                ),
                Span(
                    Span(f"{sum(len(plugin_registry.get_plugins_by_category(cat)) for cat in plugin_registry.get_categories())}", cls=str(font_weight.bold)),
                    " Plugins",
                    cls=combine_classes(badge, badge_colors.success, m.r(2))
                ),
                Span(
                    Span(f"{len(plugin_registry.get_categories_with_plugins())}", cls=str(font_weight.bold)),
                    " Plugin Categories",
                    cls=combine_classes(badge, badge_colors.warning)
                ),
                cls=combine_classes(m.b(8))
            ),

            A(
                "Open Settings Interface",
                href=settings_ar.index.to(),
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

print("\n" + "="*70)
print("Demo App Ready!")
print("="*70)
print("\n📋 Registered Settings:")
for schema_name in registry.list_schemas():
    item = registry.get(schema_name)
    if isinstance(item, SchemaGroup):
        print(f"\n  📁 {item.title} (Group)")
        for sub_key in item.schemas:
            print(f"     └─ {item.schemas[sub_key]['title']}")
    else:
        print(f"  📄 {item.get('title')}")

if config.plugin_registry:
    print("\n🔌 Registered Plugins:")
    for category in plugin_registry.get_categories_with_plugins():
        print(f"\n  Category: {category.title()}")
        for plugin in plugin_registry.get_plugins_by_category(category):
            print(f"    • {plugin.title} (v{plugin.version if plugin.version else '1.0'})")

print(f"\n💾 Config directory: {config.config_dir}")
print("="*70 + "\n")


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    def open_browser(url):
        print(f"🌐 Opening browser at {url}")
        webbrowser.open(url)

    port = 5010
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"🚀 Server: http://{display_host}:{port}")
    print("\n📍 Available routes:")
    print(f"  http://{display_host}:{port}/                  - Homepage with feature list")
    print(f"  http://{display_host}:{port}/settings/index    - Settings interface")
    print("\n" + "="*70 + "\n")

    # Open browser after a short delay
    timer = threading.Timer(1.5, lambda: open_browser(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    # Start server
    uvicorn.run(app, host=host, port=port)
