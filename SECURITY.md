# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in StadiumPulse AI, please report it
responsibly. **Do not open a public GitHub issue.**

Email: security@stadiumpulse.example.com

We will acknowledge your report within 48 hours and aim to provide a fix or
mitigation plan within 5 business days.

## Security Measures

- **Authentication**: Staff-only endpoints (Ops Copilot, Workforce Scheduler)
  require an `X-API-Key` header. The key is configured via the `OPS_API_KEY`
  environment variable and must be changed from the default before production
  deployment.

- **Rate Limiting**: Every endpoint is protected by a per-IP sliding-window
  rate limiter (30 requests per 60-second window) to prevent abuse.

- **Input Validation**: All request bodies are validated and length-constrained
  via Pydantic models, reducing prompt-injection and denial-of-service surface.

- **Grounded Generation**: The LLM is never asked to invent facts. It only
  rephrases data already computed deterministically in Python, limiting
  hallucination and injected-instruction blast radius.

- **CORS**: Configurable via `ALLOWED_ORIGINS`; defaults to `*` for development
  but should be restricted in production.

- **Non-root Container**: The Docker image runs as a non-root user (`appuser`).

- **No Secrets in Code**: API keys are read from environment variables, never
  committed to source control.

## Supported Versions

Only the latest release on the `main` branch receives security updates.
