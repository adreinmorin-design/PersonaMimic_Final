import argparse
import json
import random
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
PROMPT_BANK_PATH = APP_DIR / "prompt_bank.json"


def load_prompt_bank() -> dict:
    with PROMPT_BANK_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def choose(rng: random.Random, items: list[str], count: int) -> list[str]:
    count = min(count, len(items))
    return rng.sample(items, count)


def render_templates(
    templates: list[str], brief: dict, count: int, rng: random.Random
) -> list[str]:
    selected = choose(rng, templates, count)
    return [template.format(**brief) for template in selected]


def build_offer_payload(brief: dict, seed: int | None = None) -> dict:
    rng = random.Random(seed if seed is not None else brief["niche"])
    bank = load_prompt_bank()

    title_words = choose(rng, bank["power_words"], 2)
    generated_title = f"{title_words[0]} {brief['niche'].title()} {title_words[1]}"

    payload = {
        "product_name": generated_title,
        "brief": brief,
        "headlines": render_templates(bank["headline_templates"], brief, 6, rng),
        "hooks": render_templates(bank["hook_templates"], brief, 5, rng),
        "cta_lines": render_templates(bank["cta_templates"], brief, 4, rng),
        "bundle_angles": render_templates(bank["bundle_templates"], brief, 4, rng),
        "bonus_ideas": render_templates(bank["bonus_templates"], brief, 4, rng),
    }
    return payload


def to_text(payload: dict) -> str:
    lines = [
        f"# {payload['product_name']}",
        "",
        f"Niche: {payload['brief']['niche']}",
        f"Audience: {payload['brief']['audience']}",
        f"Pain Point: {payload['brief']['pain_point']}",
        f"Outcome: {payload['brief']['outcome']}",
        f"Tone: {payload['brief']['tone']}",
        "",
        "## Headlines",
    ]
    lines.extend(f"- {item}" for item in payload["headlines"])
    lines.append("")
    lines.append("## Hooks")
    lines.extend(f"- {item}" for item in payload["hooks"])
    lines.append("")
    lines.append("## CTA Lines")
    lines.extend(f"- {item}" for item in payload["cta_lines"])
    lines.append("")
    lines.append("## Bundle Angles")
    lines.extend(f"- {item}" for item in payload["bundle_angles"])
    lines.append("")
    lines.append("## Bonus Ideas")
    lines.extend(f"- {item}" for item in payload["bonus_ideas"])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OfferIgniter Studio turns a basic product brief into hooks, headlines, CTAs, and bonus angles."
    )
    parser.add_argument("--niche", default="creator offers", help="Product niche or category.")
    parser.add_argument("--audience", default="solo creators", help="Who the product serves.")
    parser.add_argument(
        "--pain-point",
        dest="pain_point",
        default="their offers sound generic",
        help="The core pain point.",
    )
    parser.add_argument(
        "--outcome",
        default="clearer positioning and faster conversions",
        help="The promised result.",
    )
    parser.add_argument("--tone", default="bold", help="Preferred tone for the copy.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    parser.add_argument(
        "--seed", type=int, default=None, help="Optional random seed for reproducible outputs."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    brief = {
        "niche": args.niche,
        "audience": args.audience,
        "pain_point": args.pain_point,
        "outcome": args.outcome,
        "tone": args.tone,
    }
    payload = build_offer_payload(brief, args.seed)
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(to_text(payload))


if __name__ == "__main__":
    main()
