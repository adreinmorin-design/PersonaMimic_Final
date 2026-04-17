import os

import logfire
import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.fastapi import FastApiIntegration


def setup_observability(app: FastAPI):
    """
    Industrialized observability setup for PersonaMimic.
    Strictly Open Source / Free by default: SaaS integrations are OPT-IN.
    """
    # 1. Sentry (Proprietary SaaS - Opt-in only)
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn and sentry_dsn.startswith("http"):
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
            environment=os.getenv("ENVIRONMENT", "production"),
        )
        print("Sentry Observability Integration Active (SaaS).")

    # 2. Logfire (SaaS Tracing - Opt-in only)
    # Defaulting to False to ensure 100% local operation without tokens.
    logfire_token = os.getenv("LOGFIRE_TOKEN")
    logfire.configure(
        send_to_logfire=bool(logfire_token), environment=os.getenv("ENVIRONMENT", "production")
    )
    logfire.instrument_fastapi(app)

    if logfire_token:
        print("Logfire Neural Tracing Active (SaaS).")
    else:
        print("Local Structured Logging Active (Open Source).")
