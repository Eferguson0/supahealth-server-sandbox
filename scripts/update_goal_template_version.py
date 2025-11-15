#!/usr/bin/env python3
"""
Clone the latest version of a goal template (by slug) into a new version,
optionally overriding name/description and updating defaults JSON.

Usage:
    docker compose exec app python scripts/update_goal_template_version.py \
        --slug lean_defined \
        --workout-delta 250 \
        --name "Lean & Defined (v2)" \
        --description "Look leaner. Calorie deficit + strength training (3-5x/week) + high protein."
"""

import argparse
import sys
from datetime import datetime

from sqlalchemy.orm import Session

sys.path.append("/app")

from app.db.session import SessionLocal
from app.models.goal.templates import GoalTemplate


def parse_args():
    parser = argparse.ArgumentParser(description="Duplicate goal template version with updated defaults.")
    parser.add_argument("--slug", required=True, help="Template slug to clone (e.g., lean_defined)")
    parser.add_argument("--workout-delta", type=float, required=True, help="Workout kcal delta for new version")
    parser.add_argument("--name", help="Optional new template name")
    parser.add_argument("--description", help="Optional new template description")
    return parser.parse_args()


def clone_template(db: Session, slug: str, workout_delta: float, name: str | None, description: str | None):
    source = (
        db.query(GoalTemplate)
        .filter(GoalTemplate.slug == slug)
        .order_by(GoalTemplate.version.desc())
        .first()
    )
    if not source:
        raise ValueError(f"Template '{slug}' not found.")

    new_version = source.version + 1
    new_defaults = dict(source.defaults)
    new_defaults["workout_delta_kcal"] = workout_delta

    new_template = GoalTemplate(
        slug=slug,
        version=new_version,
        name=name or source.name,
        description=description or source.description,
        defaults=new_defaults,
        active=True,
        created_at=datetime.utcnow(),
    )
    db.add(new_template)
    db.commit()
    print(f"Created template {slug} v{new_version} with workout_delta_kcal={workout_delta}")


def main():
    args = parse_args()
    db = SessionLocal()
    try:
        clone_template(db, args.slug, args.workout_delta, args.name, args.description)
    finally:
        db.close()


if __name__ == "__main__":
    main()



# Script to run in docker compose:
# docker compose exec app python scripts/update_goal_template_version.py \
#     --slug lean_defined \
#     --workout-delta 250 \
#     --name "Lean & Defined (v2)" \
#     --description "Look leaner. Calorie deficit + strength training (3-5x/week) + high protein."
