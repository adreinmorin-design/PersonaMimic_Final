from typing import Any
import json
import logging

from app.database.memory_service import memory_service as memory_engine
from app.swarm import tool_runtime

# Import logic from domains
from .base import tool_cache, SearchArgs, ComplianceArgs, FACTORY_MIN_SCORE
from .search import web_search, web_fetch, maps_search
from .engineering import (
    file_manager, python_executor, shell_executor, system_monitor, 
    performance_bridge, binary_analyzer, assemble_full_product, saas_architect,
    FileManagerArgs, SaaSArchitectArgs
)
from .discovery import market_research, market_analyzer, discover_new_niche, add_to_global_niches, affiliate_researcher
from .commerce import package_product, list_products, ecommerce_publisher, revenue_auditor, EcommerceArgs
from .quality import validate_product, peer_review, objective_validator
from .marketing import generate_marketing_copy, generate_whop_app, generate_app_visuals, social_publisher
from .meta import create_custom_tool, spawn_sub_brain

from ..compliance_service import compliance_service

logger = logging.getLogger("swarm.tools")

def generate_compliance_bundle(product_name: str, niche: str, specs: str = ""):
    return compliance_service.write_compliance_docs(product_name, niche, specs)

# --- Registry ---

MUTATING_TOOLS = {
    "file_manager", "package_product", "create_custom_tool", "spawn_sub_brain",
    "social_publisher", "generate_marketing_copy", "generate_whop_app",
    "generate_app_visuals", "assemble_full_product", "ecommerce_publisher",
    "python_executor", "shell_executor", "saas_architect", "generate_compliance_bundle"
}

CACHEABLE_TOOLS = {"web_search", "web_fetch", "market_research"}

TOOLS = [
    {"name": "web_search", "description": "Search the web.", "parameters": SearchArgs.model_json_schema()},
    {"name": "web_fetch", "description": "Fetch URL content.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "market_research", "description": "Research niches.", "parameters": {"type": "object", "properties": {"niche": {"type": "string"}}, "required": ["niche"]}},
    {"name": "file_manager", "description": "Manage files.", "parameters": FileManagerArgs.model_json_schema()},
    {"name": "python_executor", "description": "Execute Python.", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}},
    {"name": "shell_executor", "description": "Run shell.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "validate_product", "description": "Quality gate.", "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}}, "required": ["product_name"]}},
    {"name": "package_product", "description": "Zip files.", "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}}, "required": ["product_name"]}},
    {"name": "ecommerce_publisher", "description": "Publish product.", "parameters": EcommerceArgs.model_json_schema()},
    {"name": "spawn_sub_brain", "description": "Spawn brain.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "peer_review", "description": "Review design.", "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}, "status": {"type": "string"}}, "required": ["product_name", "status"]}},
    {"name": "assemble_full_product", "description": "Build asset.", "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}, "product_type": {"type": "string"}}, "required": ["product_name", "product_type"]}},
    {"name": "discover_new_niche", "description": "Scan niches.", "parameters": {"type": "object", "properties": {"depth": {"type": "integer"}}}},
    {"name": "generate_compliance_bundle", "description": "Generate Legal & FAQ.", "parameters": ComplianceArgs.model_json_schema()},
    # ... other tools
]

TOOL_HANDLERS = {
    "file_manager": lambda a: file_manager(a.get("action"), a.get("filename"), a.get("content"), a.get("target"), a.get("replacement")),
    "web_search": lambda a: web_search(a.get("query")),
    "market_research": lambda a: market_research(a.get("niche")),
    "validate_product": lambda a: validate_product(a.get("product_name"), a.get("files")),
    "package_product": lambda a: package_product(a.get("product_name"), a.get("files")),
    "create_custom_tool": lambda a: create_custom_tool(a.get("name"), a.get("schema"), a.get("code")),
    "list_products": lambda a: list_products(),
    "spawn_sub_brain": lambda a: spawn_sub_brain(a.get("name"), a.get("model"), a.get("persona_type"), a.get("niche")),
    "web_fetch": lambda a: web_fetch(a.get("url")),
    "python_executor": lambda a: python_executor(a.get("code")),
    "shell_executor": lambda a: shell_executor(a.get("command")),
    "peer_review": lambda a: peer_review(a.get("product_name"), a.get("reviewer_brain"), a.get("status"), a.get("critique")),
    "social_publisher": lambda a: social_publisher(a.get("platform"), a.get("content")),
    "revenue_auditor": lambda a: revenue_auditor(a.get("days", 7)),
    "saas_architect": lambda a: saas_architect(a.get("product_name"), a.get("niche"), a.get("stack"), a.get("features")),
    "affiliate_researcher": lambda a: affiliate_researcher(a.get("niche")),
    "assemble_full_product": lambda a: assemble_full_product(a.get("product_name"), a.get("niche"), a.get("product_type"), a.get("specs")),
    "generate_marketing_copy": lambda a: generate_marketing_copy(a.get("product_name"), a.get("niche")),
    "generate_whop_app": lambda a: generate_whop_app(a.get("product_name"), a.get("niche")),
    "generate_app_visuals": lambda a: generate_app_visuals(a.get("product_name"), a.get("description")),
    "ecommerce_publisher": lambda a: ecommerce_publisher(a.get("platform"), a.get("api_key"), a.get("title"), a.get("description"), a.get("price"), a.get("currency"), a.get("company_id")),
    "discover_new_niche": lambda a: discover_new_niche(a.get("depth", 5)),
    "add_to_global_niches": lambda a: add_to_global_niches(a.get("niche")),
    "maps_search": lambda a: maps_search(a.get("location_query")),
    "binary_analyzer": lambda a: binary_analyzer(a.get("filename"), a.get("scan_type")),
    "objective_validator": lambda a: objective_validator(a.get("product_name")),
    "performance_bridge": lambda a: performance_bridge(a.get("code"), a.get("language")),
    "generate_compliance_bundle": lambda a: generate_compliance_bundle(a.get("product_name"), a.get("niche"), a.get("specs")),
}

def execute_tool(name: str, args: dict[str, Any]) -> str:
    cache_key = f"{name}:{json.dumps(args, sort_keys=True, default=str)}"
    if name in CACHEABLE_TOOLS:
        hit = tool_cache.get(cache_key)
        if hit: return hit

    try:
        handler = TOOL_HANDLERS.get(name)
        if handler:
            result = handler(args)
        else:
            from app.swarm import tool_runtime
            custom_result = tool_runtime.execute_custom_tool(name, args)
            result = custom_result if custom_result is not None else f"Unknown tool: {name}"

        if result and not tool_runtime.is_failure_result(result):
            if name in CACHEABLE_TOOLS: tool_cache.add(cache_key, result)
            if name in MUTATING_TOOLS:
                memory_engine.store_tool_outcome(tool_name=name, tool_args=args, result=result, brain_name="System")
        return result
    except Exception as e:
        logger.error(f"[TOOL ERROR] {e}")
        return f"Tool execution error ({name}): {str(e)}"
