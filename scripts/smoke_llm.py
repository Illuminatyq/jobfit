"""Contract probe: which structured-output strategy does the endpoint honor?

Never prints the API key. Reads it from JOBFIT_NVIDIA_API_KEY or NVIDIA_API_KEY.
Exit codes: 0 gate passed, 2 config error, 3 transport error, 4 no strategy worked.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError


class Claim(BaseModel):
    text: str = Field(min_length=10, max_length=300)
    evidence_refs: list[str] = Field(min_length=1)


class Draft(BaseModel):
    greeting: str
    claims: list[Claim] = Field(min_length=2, max_length=6)
    closing: str


SYSTEM = (
    "Ты пишешь сопроводительное письмо. Каждое утверждение обязано опираться на "
    "идентификатор доказательства из профиля. Новые факты придумывать запрещено. "
    "Ответь только JSON по заданной схеме."
)


def build_user(schema: dict[str, Any]) -> str:
    return (
        "ПРОФИЛЬ (доказательства):\n"
        "e1: 4.5 года коммерческого тестирования web, mobile, backend.\n"
        "e2: Сократил время регрессионного прогона с 8 до 4 часов.\n\n"
        "ВАКАНСИЯ: QA Engineer. Требуется API-тестирование и оптимизация регресса.\n\n"
        "Задача: письмо из двух утверждений, каждое со ссылкой на e1 или e2.\n"
        f"JSON schema: {json.dumps(schema, ensure_ascii=False)}\n"
    )


def strategies(schema: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    return [
        ("nvext.guided_json", {"nvext": {"guided_json": schema}}),
        (
            "response_format.json_schema",
            {
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {"name": "cover_letter", "schema": schema, "strict": True},
                }
            },
        ),
        ("response_format.json_object", {"response_format": {"type": "json_object"}}),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://integrate.api.nvidia.com/v1")
    parser.add_argument("--model", default=os.environ.get("JOBFIT_NVIDIA_MODEL", ""))
    parser.add_argument("--list-models", action="store_true")
    args = parser.parse_args()

    key = os.environ.get("JOBFIT_NVIDIA_API_KEY") or os.environ.get("NVIDIA_API_KEY", "")
    if not key:
        print("FAIL config: set JOBFIT_NVIDIA_API_KEY in .env or environment")
        return 2

    schema = Draft.model_json_schema()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    accepted: list[str] = []
    sample = ""

    with httpx.Client(base_url=args.base_url, headers=headers, timeout=180.0) as client:
        if args.list_models:
            try:
                listing = client.get("/models")
                if listing.status_code == 200:
                    ids = [m.get("id") for m in listing.json().get("data", [])]
                    print("available models:", ", ".join(filter(None, ids))[:2000])
                else:
                    print(f"note: /models returned {listing.status_code}, use the catalog")
            except httpx.HTTPError as exc:
                print(f"note: /models unavailable: {exc}")

        if not args.model:
            print("FAIL config: pass --model with the exact slug from the model card")
            return 2

        for name, extra in strategies(schema):
            payload: dict[str, Any] = {
                "model": args.model,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": build_user(schema)},
                ],
                "temperature": 0,
                "max_tokens": 900,
                "stream": False,
            }
            payload.update(extra)

            started = time.perf_counter()
            try:
                response = client.post("/chat/completions", json=payload)
            except httpx.HTTPError as exc:
                print(f"{name}: transport error: {exc}")
                return 3
            elapsed = time.perf_counter() - started

            if response.status_code in (401, 403):
                print(f"FAIL auth {response.status_code}: key revoked or invalid")
                return 2
            if response.status_code == 429:
                print("FAIL rate limit 429: pause and retry later")
                return 3
            if response.status_code >= 400:
                print(f"{name}: rejected {response.status_code} {response.text[:200]}")
                continue

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            try:
                draft = Draft.model_validate_json(content)
            except ValidationError as exc:
                print(f"{name}: HTTP 200 but schema invalid: {str(exc)[:300]}")
                print("  raw:", content[:400])
                continue

            usage = data.get("usage", {})
            print(f"{name}: OK {elapsed:.2f}s tokens={usage.get('total_tokens', 'n/a')}")
            print(f"  claims={len(draft.claims)} refs={draft.claims[0].evidence_refs}")
            accepted.append(name)
            if not sample:
                sample = content

        if not accepted:
            print("GATE FAILED: no strategy produced schema-valid output")
            return 4

        chosen = accepted[0]
        extra = dict(strategies(schema))[chosen]
        payload = {
            "model": args.model,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": build_user(schema)},
            ],
            "temperature": 0,
            "max_tokens": 900,
            "stream": False,
            **extra,
        }
        second = client.post("/chat/completions", json=payload)
        again = second.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        same = again == sample
        print(f"determinism: {'identical' if same else 'differs'}")
        print(f"GATE PASSED, strategy={chosen}")
        print(json.dumps({"strategy": chosen, "deterministic": same}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
