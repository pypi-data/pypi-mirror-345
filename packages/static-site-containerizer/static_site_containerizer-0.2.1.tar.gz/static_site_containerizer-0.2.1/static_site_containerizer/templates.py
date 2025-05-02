"""Dockerfile templates."""

# fmt: off
# ruff: noqa

from string import Template


NGINX_DOCKERFILE: Template = Template("""FROM $base_image

COPY $content_path /usr/share/nginx/html
""")
