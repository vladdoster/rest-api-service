"""Validate cookiecutter input against the platform's service.yaml rules."""

import re
import sys

# memory values ECS accepts for each Fargate CPU setting
FARGATE_MEMORY = {
    256: (512, 1024, 2048),
    512: range(1024, 4097, 1024),
    1024: range(2048, 8193, 1024),
    2048: range(4096, 16385, 1024),
    4096: range(8192, 30721, 1024),
    8192: range(16384, 61441, 4096),
    16384: range(32768, 122881, 8192),
}

errors = []


def as_int(name: str, raw: str) -> int | None:
    try:
        return int(raw)
    except ValueError:
        errors.append("%s %r must be an integer" % (name, raw))
        return None


SLUG = "{{ cookiecutter.project_slug }}"
PREFIX = "{{ cookiecutter.path_prefix }}"
PORT = as_int("port", "{{ cookiecutter.port }}")
SCALING_MIN = as_int("scaling_min", "{{ cookiecutter.scaling_min }}")
SCALING_MAX = as_int("scaling_max", "{{ cookiecutter.scaling_max }}")
CPU = as_int("cpu", "{{ cookiecutter.cpu }}")
MEMORY = as_int("memory", "{{ cookiecutter.memory }}")

# stricter than the platform regex: svc/<slug> is an ECR name, which rejects stray hyphens
if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", SLUG) or len(SLUG) > 40:
    errors.append("project_slug %r must be lowercase alphanumerics joined by single hyphens, max 40 chars" % SLUG)
if not re.fullmatch(r"/[A-Za-z0-9/_-]+", PREFIX) or PREFIX.endswith("/"):
    errors.append("path_prefix %r must start with '/', not be '/', and have no trailing '/'" % PREFIX)
if PORT is not None and not 1 <= PORT <= 65535:
    errors.append("port %d out of range 1-65535" % PORT)
if SCALING_MIN is not None and SCALING_MAX is not None and not 1 <= SCALING_MIN <= SCALING_MAX:
    errors.append("scaling_min %d must be >= 1 and <= scaling_max %d" % (SCALING_MIN, SCALING_MAX))
if CPU is not None and CPU not in FARGATE_MEMORY:
    errors.append("cpu %d must be one of %s" % (CPU, sorted(FARGATE_MEMORY)))
elif CPU is not None and MEMORY is not None and MEMORY not in FARGATE_MEMORY[CPU]:
    errors.append("memory %d is not a valid Fargate size for cpu %d; valid values: %s" % (MEMORY, CPU, sorted(FARGATE_MEMORY[CPU])))

if errors:
    print("ERROR: invalid cookiecutter input:\n  " + "\n  ".join(errors), file=sys.stderr)
    sys.exit(1)
