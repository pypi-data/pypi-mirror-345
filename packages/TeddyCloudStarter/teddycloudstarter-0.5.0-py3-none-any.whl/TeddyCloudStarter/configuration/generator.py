#!/usr/bin/env python3
"""
Configuration generators for TeddyCloudStarter.
"""
import os

import jinja2

from ..wizard.ui_helpers import console


def generate_docker_compose(config, translator, templates):
    """
    Generate docker-compose.yml based on configuration.

    Args:
        config: The configuration dictionary
        translator: The translator instance for localization
        templates: The templates dictionary containing templates

    Returns:
        bool: True if generation was successful, False otherwise
    """
    try:
        env = jinja2.Environment(autoescape=True)

        template = env.from_string(templates.get("docker-compose", ""))

        project_path = config.get("environment", {}).get("path", "")
        if not project_path:
            console.print(
                f"[bold yellow]{translator.get('Warning')}: {translator.get('No project path set. Using current directory.')}[/]"
            )
            project_path = os.getcwd()

        data_dir = os.path.join(project_path, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            console.print(
                f"[green]{translator.get('Created data directory at')}: {data_dir}[/]"
            )

        context = {"mode": config["mode"]}
        context["teddycloud_image_tag"] = config.get("teddycloud_image_tag", "latest")

        if config["mode"] == "direct":
            context.update(
                {
                    "admin_http": config["ports"]["admin_http"],
                    "admin_https": config["ports"]["admin_https"],
                    "teddycloud": config["ports"]["teddycloud"],
                }
            )
        else:
            crl_file = os.path.exists(
                os.path.join(data_dir, "client_certs", "crl", "ca.crl")
            )

            context.update(
                {
                    "domain": config["nginx"]["domain"],
                    "https_mode": config["nginx"]["https_mode"],
                    "security_type": config["nginx"]["security"]["type"],
                    "allowed_ips": config["nginx"]["security"]["allowed_ips"],
                    "crl_file": crl_file,
                }
            )

            if config["nginx"]["https_mode"] == "user_provided":
                server_certs_path = os.path.join(data_dir, "server_certs")
                if not os.path.exists(server_certs_path):
                    os.makedirs(server_certs_path, exist_ok=True)
                    console.print(
                        f"[green]{translator.get('Created server_certs directory at')}: {server_certs_path}[/]"
                    )

                context.update({"cert_path": "./server_certs:/etc/nginx/certificates"})
            elif config["nginx"]["https_mode"] == "self_signed":
                context.update({"cert_path": "./server_certs:/etc/nginx/certificates"})
            elif config["nginx"]["https_mode"] == "user_provided":
                context.update({"cert_path": "./server_certs:/etc/nginx/certificates"})

        rendered = template.render(**context)
        with open(os.path.join(data_dir, "docker-compose.yml"), "w") as f:
            f.write(rendered)

        console.print(
            "[bold green]Docker Compose configuration generated successfully.[/]"
        )
        return True
    except Exception as e:
        console.print(f"[bold red]Error generating Docker Compose file: {e}[/]")
        return False


def generate_nginx_configs(config, translator, templates):
    """
    Generate nginx configuration files.

    Args:
        config: The configuration dictionary
        translator: The translator instance for localization
        templates: The templates dictionary containing templates

    Returns:
        bool: True if generation was successful, False otherwise
    """
    try:
        env = jinja2.Environment(autoescape=True)

        project_path = config.get("environment", {}).get("path", "")
        if not project_path:
            console.print(
                f"[bold yellow]{translator.get('Warning')}: {translator.get('No project path set. Using current directory.')}[/]"
            )
            project_path = os.getcwd()

        data_dir = os.path.join(project_path, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            console.print(
                f"[green]{translator.get('Created data directory at')}: {data_dir}[/]"
            )

        config_dir = os.path.join(data_dir, "configurations")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
            console.print(
                f"[green]{translator.get('Created configurations directory at')}: {config_dir}[/]"
            )

        edge_template = env.from_string(templates.get("nginx-edge", ""))
        edge_context = {
            "domain": config["nginx"]["domain"],
            "https_mode": config["nginx"]["https_mode"],
            "security_type": config["nginx"]["security"]["type"],
            "allowed_ips": config["nginx"]["security"]["allowed_ips"],
        }

        with open(os.path.join(config_dir, "nginx-edge.conf"), "w") as f:
            f.write(edge_template.render(**edge_context))

        auth_template = env.from_string(templates.get("nginx-auth", ""))
        auth_context = {
            "domain": config["nginx"]["domain"],
            "https_mode": config["nginx"]["https_mode"],
            "security_type": config["nginx"]["security"]["type"],
            "allowed_ips": config["nginx"]["security"]["allowed_ips"],
            "auth_bypass_ips": config["nginx"]["security"].get("auth_bypass_ips", []),
            "crl_file": os.path.exists(
                os.path.join(data_dir, "client_certs", "crl", "ca.crl")
            ),
        }

        with open(os.path.join(config_dir, "nginx-auth.conf"), "w") as f:
            f.write(auth_template.render(**auth_context))

        console.print("[bold green]Nginx configurations generated successfully.[/]")
        return True
    except Exception as e:
        console.print(f"[bold red]Error generating Nginx configurations: {e}[/]")
        return False
