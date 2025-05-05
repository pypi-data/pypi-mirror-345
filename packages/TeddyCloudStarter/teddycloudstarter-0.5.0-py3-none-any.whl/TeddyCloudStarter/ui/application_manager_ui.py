#!/usr/bin/env python3
"""
Application management UI for TeddyCloudStarter.
"""
import subprocess
from pathlib import Path

import questionary
from rich import box
from rich.panel import Panel

from ..wizard.ui_helpers import console, custom_style


def show_application_management_menu(config_manager, docker_manager, translator):
    """
    Show Application management submenu with options for managing TeddyCloud application.

    Args:
        config_manager: The configuration manager instance
        docker_manager: The docker manager instance
        translator: The translator instance for localization

    Returns:
        bool: True if user chose to exit, False otherwise
    """
    choices = [
        translator.get("Inject tonies.custom.json file"),
        translator.get("Back to main menu"),
    ]

    while True:
        action = questionary.select(
            translator.get("Application Management"),
            choices=choices,
            style=custom_style,
        ).ask()

        if action == translator.get("Inject tonies.custom.json file"):
            result = inject_tonies_custom_json(
                config_manager, docker_manager, translator
            )
            if result == "cancel":
                continue  # Show the Application Management Menu again
            return False
        elif action == translator.get("Back to main menu"):
            console.print(
                f"[bold cyan]{translator.get('Returning to main menu')}...[/]"
            )
            return True
        return False


def inject_tonies_custom_json(config_manager, docker_manager, translator):
    """
    Inject the tonies.custom.json file from ProjectPath/data/ to the config volume.

    Args:
        config_manager: The configuration manager instance
        docker_manager: The docker manager instance
        translator: The translator instance for localization
    """
    project_path = config_manager.config.get("environment", {}).get("path")
    if not project_path:
        console.print(
            f"[bold red]{translator.get('Error')}: {translator.get('No project path set in config.')}[/]"
        )
        return

    base_path = Path(project_path)

    source_file = base_path / "data" / "tonies.custom.json"

    if not source_file.exists():
        console.print(
            f"[bold red]{translator.get('Error')}: {translator.get('The file tonies.custom.json does not exist at')} {source_file}[/]"
        )

        create_empty = questionary.confirm(
            translator.get(
                "Would you like to create an empty tonies.custom.json file?"
            ),
            default=True,
            style=custom_style,
        ).ask()

        if create_empty:
            try:
                with open(source_file, "w") as f:
                    f.write("[]")
                console.print(
                    f"[bold green]{translator.get('Created empty tonies.custom.json file at')} {source_file}[/]"
                )
            except Exception as e:
                console.print(
                    f"[bold red]{translator.get('Error creating file')}: {e}[/]"
                )
                return "cancel"
        else:
            return "cancel"

    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            check=True,
            capture_output=True,
            text=True,
        )
        running_containers = result.stdout.strip().split("\n")
        running_containers = [
            container for container in running_containers if container
        ]

        console.print(
            f"[cyan]{translator.get('Found running containers')}: {', '.join(running_containers)}[/]"
        )

        teddycloud_container = None
        if "teddycloud-app" in running_containers:
            teddycloud_container = "teddycloud-app"
            console.print(
                f"[green]{translator.get('Found teddycloud-app container')}[/]"
            )

        if not teddycloud_container:
            console.print(
                f"[yellow]{translator.get('TeddyCloud container not found running. Will try to use the volume directly.')}[/]"
            )
    except Exception as e:
        console.print(
            f"[yellow]{translator.get('Could not list running containers')}: {e}[/]"
        )
        running_containers = []

    if not running_containers or not teddycloud_container:
        try:
            temp_container_name = "temp_teddycloud_file_injector"

            try:
                check_result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "-a",
                        "--filter",
                        f"name={temp_container_name}",
                        "--format",
                        "{{.Names}}",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                if temp_container_name in check_result.stdout:
                    subprocess.run(
                        ["docker", "rm", "-f", temp_container_name], check=True
                    )
            except Exception as e:
                console.print(f"[yellow]{translator.get('Note')}: {e}[/]")

            try:
                console.print(
                    f"[cyan]{translator.get('Creating temporary container to access the config volume')}[/]"
                )
                create_result = subprocess.run(
                    [
                        "docker",
                        "create",
                        "--name",
                        temp_container_name,
                        "-v",
                        "teddycloudstarter_config:/config",
                        "nginx:stable-alpine",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                teddycloud_container = temp_container_name
                console.print(
                    f"[green]{translator.get('Created temporary container to access the config volume')}[/]"
                )
            except subprocess.CalledProcessError as e:
                console.print(
                    f"[bold red]{translator.get('Failed to create temporary container')}: {e.stderr}[/]"
                )
                try:
                    console.print(
                        f"[cyan]{translator.get('Trying with volume name config')}[/]"
                    )
                    create_result = subprocess.run(
                        [
                            "docker",
                            "create",
                            "--name",
                            temp_container_name,
                            "-v",
                            "config:/config",
                            "nginx:stable-alpine",
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    teddycloud_container = temp_container_name
                    console.print(
                        f"[green]{translator.get('Created temporary container to access the config volume')}[/]"
                    )
                except subprocess.CalledProcessError as e:
                    console.print(
                        f"[bold red]{translator.get('Failed to create temporary container')}: {e.stderr}[/]"
                    )
        except Exception as e:
            console.print(
                f"[bold red]{translator.get('Error creating temporary container')}: {e}[/]"
            )

    if not teddycloud_container:
        console.print(
            f"[bold yellow]{translator.get('Warning')}: {translator.get('TeddyCloud container not found')}.[/]"
        )
        console.print(
            Panel(
                f"[bold]{translator.get('Manual steps')}:[/]\n"
                f"1. {translator.get('Copy')} {source_file}\n"
                f"2. {translator.get('To the config volume of the TeddyCloud container')}\n"
                f"   {translator.get('Using command')}: docker cp {source_file} teddycloud-app:/teddycloud/config/tonies.custom.json\n"
                f"   {translator.get('Or')}: docker run --rm -v {source_file}:/src -v teddycloudstarter_config:/dest alpine cp /src /dest/tonies.custom.json\n",
                title=f"[bold cyan]{translator.get('Manual Injection Instructions')}[/]",
                box=box.ROUNDED,
            )
        )
        return

    confirm = questionary.confirm(
        translator.get(
            "Do you want to inject tonies.custom.json into the TeddyCloud config volume?"
        ),
        default=True,
        style=custom_style,
    ).ask()

    if not confirm:
        console.print(f"[bold yellow]{translator.get('Operation cancelled')}.[/]")
        return

    is_temp_container = teddycloud_container == "temp_teddycloud_config_access"

    target_path = (
        "/config/tonies.custom.json"
        if is_temp_container
        else "/teddycloud/config/tonies.custom.json"
    )

    try:
        try:
            console.print(
                f"[cyan]{translator.get('Injecting file to')} {teddycloud_container}:{target_path}[/]"
            )

            result = subprocess.run(
                [
                    "docker",
                    "cp",
                    str(source_file),
                    f"{teddycloud_container}:{target_path}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            if is_temp_container:
                subprocess.run(["docker", "rm", "-f", teddycloud_container], check=True)
                console.print(
                    f"[green]{translator.get('Cleaned up temporary container')}[/]"
                )

            console.print(
                f"[bold green]{translator.get('Successfully injected tonies.custom.json into config volume')}![/]"
            )

            if not is_temp_container:
                restart = questionary.confirm(
                    translator.get(
                        "Would you like to restart the TeddyCloud container to apply changes?"
                    ),
                    default=True,
                    style=custom_style,
                ).ask()

                if restart:
                    try:
                        console.print(
                            f"[cyan]{translator.get('Restarting container')} {teddycloud_container}[/]"
                        )
                        restart_result = subprocess.run(
                            ["docker", "restart", teddycloud_container],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        console.print(
                            f"[bold green]{translator.get('TeddyCloud container restarted successfully')}![/]"
                        )
                    except Exception as e:
                        console.print(
                            f"[bold red]{translator.get('Error restarting container')}: {e}[/]"
                        )
                        console.print(
                            f"[yellow]{translator.get('You may need to restart the container manually')}[/]"
                        )
            else:
                console.print(
                    f"[bold yellow]{translator.get('You should restart your TeddyCloud container to apply changes')}.[/]"
                )
                console.print(
                    f"[green]{translator.get('Use command')}: docker restart teddycloud-app[/]"
                )

        except subprocess.CalledProcessError as e:
            console.print(
                f"[bold red]{translator.get('Error injecting file')}: {e.stderr}[/]"
            )

    except Exception as e:
        console.print(
            f"[bold red]{translator.get('Error during file injection')}: {e}[/]"
        )
        if is_temp_container:
            try:
                subprocess.run(
                    ["docker", "rm", "-f", teddycloud_container], check=False
                )
            except:
                pass
