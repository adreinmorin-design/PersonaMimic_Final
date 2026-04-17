"""
app/swarm/tools.py - Package Facade
Redirects all imports to the new modular tools package for backward compatibility.
"""

from .tools import (
    TOOLS,
    TOOL_HANDLERS,
    execute_tool,
    MUTATING_TOOLS,
    CACHEABLE_TOOLS,
    FACTORY_MIN_SCORE,
    # Export other common tools for compatibility
    web_search,
    web_fetch,
    file_manager,
    python_executor,
    shell_executor,
    assemble_full_product,
    package_product,
    validate_product,
    generate_compliance_bundle,
)

# Shared schemas for external usage
from .tools.engineering import FileManagerArgs, SaaSArchitectArgs
from .tools.commerce import EcommerceArgs
from .tools.base import SearchArgs, ComplianceArgs
