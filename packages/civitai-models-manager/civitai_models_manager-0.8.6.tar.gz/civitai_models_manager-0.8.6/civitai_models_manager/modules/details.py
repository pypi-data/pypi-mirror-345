import httpx
import subprocess
from typing import Any, Dict, List, Tuple, Optional
import html2text
import questionary
import re
from functools import lru_cache
from .helpers import feedback_message, create_table, add_rows_to_table
from .utils import safe_get, safe_url, format_file_size
from enum import Enum
from rich.text import Text
from rich.markdown import Markdown
from rich.console import Console

__all__ = ["get_model_details_cli"]

console = Console(soft_wrap=True)
h2t = html2text.HTML2Text()


class DetailActions(Enum):
    LOOK_IMAGES = "Look up Images for the Model"
    FULL_DESCRIPTION = "Look at full Description"
    ANOTHER_MODEL = "Get Details on a Version of this Model"
    DOWNLOAD_MODEL = "Download this Model"
    DOWNLOAD_VERSION = "Download a Version"
    GENERATE_IMAGE = "Generate Image from Model on CivitAI"
    CANCEL = "Cancel"


# @lru_cache(maxsize=128)
def fetch_model_data(url: str, model_id: int) -> Optional[Dict]:
    data = make_request(f"{url}/{model_id}")
    if data and "modelVersions" in data:
        # Ensure we have the urn:air for at least the first version
        first_version = data["modelVersions"][0] if data["modelVersions"] else {}
        if "air" not in first_version:
            first_version["air"] = process_string(first_version, data, 0)
    return data


# @lru_cache(maxsize=128)
def fetch_version_data(
    versions_url: str, models_url: str, model_id: int
) -> Optional[Dict]:
    version_data = make_request(f"{versions_url}/{model_id}")
    if version_data:
        parent_model_data = make_request(f"{models_url}/{version_data.get('modelId')}")
        if parent_model_data:
            combined_data = {**version_data, **parent_model_data}
            if "air" not in combined_data:
                combined_data["air"] = process_string(
                    version_data, parent_model_data, 0
                )
            return combined_data
    return None


def make_request(url: str) -> Optional[Dict]:
    try:
        response = httpx.get(url)
        if response.status_code == 404:
            # TODO: Write a check for model versions that return 404 since civitai only gives pages to parent models and not versions
            pass
        else:
            response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        feedback_message(f"Failed to get data from {url}: {e}", "error")
        return None


def get_model_details(
    CIVITAI_MODELS: str, CIVITAI_VERSIONS: str, model_id: int
) -> Dict[str, Any]:
    if not model_id:
        feedback_message("Please provide a valid model ID.", "error")
        return {}

    model_data = fetch_model_data(CIVITAI_MODELS, model_id)
    if "error" in model_data:
        model_data = fetch_version_data(CIVITAI_VERSIONS, CIVITAI_MODELS, model_id)

    return process_model_data(model_data) if model_data else {}


def process_string(v: Dict[str, Any], data: Dict[str, Any], idx: int) -> str:
    model_id = data.get("id") or v.get("modelId")
    version_id = v.get("id")
    base_model = v.get("baseModel", "")
    model_type = data.get("type", "checkpoint")

    input_string = f"urn:air:{base_model}:{model_type}:civitai:{model_id}@{version_id}"
    processed = input_string.lower()

    replacements: List[Tuple[str, str]] = [
        (r"flux\.1\s*[sd](?=:)", "flux1"),
        (r"sd\s*(?:1\.5|1)(?=:)", "sd1"),
        (r"sd\s*(?:2\.5|2)(?=:)", "sd2"),
        (r"sd\s*3(?=:)", "sd3"),
        (r"sdxl(?:\s+1\.0)?(?=:)", "sdxl"),
    ]

    for pattern, replacement in replacements:
        processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)
    
    return processed


def process_model_data(data: Dict) -> Dict[str, Any]:
    is_version = "model" in data
    versions = (
        [
            {
                "id": v.get("id", ""),
                "stats": v.get("stats", ""),
                "name": v.get("name", ""),
                "base_model": v.get("baseModel", ""),
                "download_url": v.get("files", [{}])[0].get("downloadUrl", ""),
                "images": v.get("images", [{}])[0].get("url", ""),
                "file": v.get("files", [{}])[0].get("name", ""),
                "air": process_string(v, data, i),
            }
            for i, v in enumerate(data.get("modelVersions", []))
        ]
        if not is_version
        else []
    )

    return {
        "id": data.get("id", ""),
        "parent_id": data.get("modelId") if is_version else None,
        "parent_name": safe_get(data, ["model", "name"]) if is_version else None,
        "name": data.get("name", ""),
        "stats": data.get("stats", ""),
        "description": data.get("description", ""),
        "type": safe_get(data, ["model", "type"] if is_version else ["type"], ""),
        "base_model": data.get("baseModel", ""),
        "air": data.get("air", ""),
        "download_url": safe_get(
            data,
            ["modelVersions", 0, "downloadUrl"] if not is_version else ["downloadUrl"],
            "",
        ),
        "tags": data.get("tags", []),
        "creator": safe_get(data, ["creator", "username"], ""),
        "trainedWords": safe_get(
            data,
            (
                ["modelVersions", 0, "trainedWords"]
                if not is_version
                else ["trainedWords"]
            ),
            "None",
        ),
        "nsfw": (
            Text("Yes", style="bright_yellow")
            if data.get("nsfw", False)
            else Text("No", style="bright_red")
        ),
        "metadata": get_metadata(data, is_version),
        "versions": versions,
        "images": safe_get(
            data, ["modelVersions", 0, "images"] if not is_version else ["images"], []
        ),
    }

    return {
        "id": data.get("id", ""),
        "parent_id": data.get("modelId") if is_version else None,
        "parent_name": safe_get(data, ["model", "name"]) if is_version else None,
        "name": data.get("name", ""),
        "stats": data.get("stats", ""),
        "description": data.get("description", ""),
        "type": safe_get(data, ["model", "type"] if is_version else ["type"], ""),
        "base_model": data.get("baseModel", ""),
        "air": data.get("air", ""),
        "download_url": safe_get(
            data,
            ["modelVersions", 0, "downloadUrl"] if not is_version else ["downloadUrl"],
            "",
        ),
        "tags": data.get("tags", []),
        "creator": safe_get(data, ["creator", "username"], ""),
        "trainedWords": safe_get(
            data,
            (
                ["modelVersions", 0, "trainedWords"]
                if not is_version
                else ["trainedWords"]
            ),
            "None",
        ),
        "nsfw": (
            Text("Yes", style="bright_yellow")
            if data.get("nsfw", False)
            else Text("No", style="bright_red")
        ),
        "metadata": get_metadata(data, is_version),
        "versions": versions,
        "images": safe_get(
            data, ["modelVersions", 0, "images"] if not is_version else ["images"], []
        ),
    }


def get_metadata(data: Dict, is_version: bool) -> Dict[str, Any]:
    stats_path = ["stats"] if not is_version else ["model", "stats"]
    files_path = ["modelVersions", 0, "files", 0] if not is_version else ["files", 0]
    return {
        "stats": f"{safe_get(data, stats_path + ['downloadCount'], '')} downloads, "
        f"{safe_get(data, stats_path + ['thumbsUpCount'], '')} likes, "
        f"{safe_get(data, stats_path + ['thumbsDownCount'], '')} dislikes",
        "size": format_file_size(safe_get(data, files_path + ["sizeKB"], 0)),
        "format": safe_get(data, files_path + ["metadata", "format"], ".safetensors"),
        "file": safe_get(data, files_path + ["name"], ""),
    }


def print_model_details(
    model_details: Dict[str, Any], desc: bool, images: bool
) -> None:
    model_table = create_table(
        "", [("Attributes", "bright_yellow"), ("Values", "white")]
    )

    add_rows_to_table(
        model_table,
        {
            "Model ID": model_details["id"],
            "Name": model_details["name"],
            "Stats": model_details["stats"],
            "Type": model_details["type"],
            "Tags": model_details.get("tags", []),
            "Creator": model_details["creator"],
            "NSFW": model_details["nsfw"],
            "Size": model_details["metadata"]["size"],
            "AIR": (
                model_details["air"]
                if model_details.get("air")
                else model_details["versions"][0]["air"]
            ),
        },
    )

    console.print(model_table)

    if desc:
        desc_table = create_table("", [("Description", "white")])
        desc_table.add_row(Markdown(h2t.handle(model_details["description"])))
        console.print(desc_table)

    versions = model_details.get("versions", [])
    if versions:
        version_table = create_table(
            "",
            [
                ("Version ID", "cyan"),
                ("Name", "bright_yellow"),
                ("Base Model", "bright_yellow"),
                ("Download URL", "bright_yellow"),
                ("Images", "bright_yellow"),
                ("air", "bright_yellow"),
            ],
        )
        for count, version in enumerate(versions):
            version_table.add_row(
                str(version["id"]),
                version["name"],
                version["base_model"],
                safe_url(version["download_url"]),
                safe_url(version["images"]),
                safe_get(version, ["air"], ""),
            )
        console.print(version_table)

    if images and model_details.get("images"):
        images_table = create_table(
            "", [("NSFW Lvl", "bright_red"), ("URL", "bright_yellow")]
        )
        for image in model_details["images"]:
            nsfw_level = image.get("nsfwLevel", 0)
            if nsfw_level > 10:
                images_table.add_row(
                    Text(f"{nsfw_level} // NSFW", style="bright_red"),
                    safe_url(image["url"]),
                )
            elif nsfw_level > 5:
                images_table.add_row(
                    Text(f"{nsfw_level} // SUGGESTIVE", style="bright_yellow"),
                    safe_url(image["url"]),
                )
            else:
                images_table.add_row(
                    Text(f"{nsfw_level} // SAFE", style="bright_green"),
                    safe_url(image["url"]),
                )
        feedback_message(
            "NSFW Ratings are provided by the API, not by this CLI Tool", "info"
        )
        console.print(images_table)

    if model_details.get("parent_id"):
        feedback_message(
            f"{model_details['name']} is a variant of {model_details['parent_name']} // Model ID: {model_details['parent_id']}",
            "warning",
        )

    if not model_details.get("images"):
        feedback_message(
            f"No images available for model {model_details['name']}.", "warning"
        )

    if not versions and not model_details.get("parent_id"):
        feedback_message(
            f"No versions available for model {model_details['name']}.", "warning"
        )

    details_action_question = questionary.select(
        "What would you like to do?",
        choices=[action.value for action in DetailActions],
    ).ask()

    if details_action_question == "Look up Images for the Model":
        subprocess.run(
            f"civitai-models details --images {model_details['id']}", shell=True
        )
    elif details_action_question == "Look at full Description":
        subprocess.run(
            f"civitai-models details --desc {model_details['id']}", shell=True
        )
    elif details_action_question == "Get Details on a Version of this Model":
        version_details = questionary.select(
            "Select a version to get details on",
            choices=[f"{version['id']} - {version['name']}" for version in versions],
        ).ask()
        if version_details:
            subprocess.run(
                f"civitai-models details {int(version_details.split(' ')[0])}",
                shell=True,
            )
        else:
            feedback_message("Model version details not selected", "warning")
    elif details_action_question == "Download this Model":
        subprocess.run(f"civitai-models download {model_details['id']}", shell=True)
    elif details_action_question == "Download a Version":
        subprocess.run(
            f"civitai-models download {model_details['id']} --select", shell=True
        )
    else:
        feedback_message("Model action cancelled.", "warning")


def get_model_details_cli(
    identifier: str,
    desc: bool = False,
    images: bool = False,
    CIVITAI_MODELS: str = "",
    CIVITAI_VERSIONS: str = "",
) -> None:
    """Get detailed information about a specific model by ID."""
    try:
        model_id = int(identifier)
        model_details = get_model_details(CIVITAI_MODELS, CIVITAI_VERSIONS, model_id)
        if model_details:
            print_model_details(model_details, desc, images)
        else:
            feedback_message(f"No model found with ID: {identifier}", "error")
    except ValueError:
        feedback_message("Invalid model ID. Please enter a valid number.", "error")
