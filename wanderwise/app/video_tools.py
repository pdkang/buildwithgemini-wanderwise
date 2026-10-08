# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import re
import uuid
from google.adk.tools import ToolContext
from google.cloud import storage
from google import genai
from google.genai import types

GCS_BUCKET_NAME = "wanderwise-qwiklabs-gcp-04-66358bebd184"
PROJECT_ID = "qwiklabs-gcp-04-66358bebd184"


async def generate_travel_video(
    destination_or_lodging: str,
    scene_description: str,
    tool_context: ToolContext,
) -> str:
    """Generates a short travel video clip for a destination, lodging, or attraction using Google's Omni model (gemini-omni-flash-preview).

    Saves the video artifact for display in the Playground's Artifacts panel and uploads the video
    to a public Google Cloud Storage bucket, returning its public HTTPS URL.

    Args:
        destination_or_lodging: The travel item name (e.g., 'Tokyo Shinjuku Stroll', 'Boutique Hotel Paris', 'Colosseum Sunset').
        scene_description: A vivid visual description of what should happen in the video clip (e.g. 'Cherry blossoms gently falling around a traditional lantern in evening Tokyo').
        tool_context: ADK ToolContext used for saving the artifact.

    Returns:
        The public HTTPS URL of the uploaded video in Cloud Storage.
    """
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    prompt = (
        f"A cinematic 3-second travel clip of {destination_or_lodging}. "
        f"{scene_description}. High quality, smooth camera movement."
    )

    interaction = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=prompt,
    )

    video_data = None
    if hasattr(interaction, "output_video") and interaction.output_video:
        raw = interaction.output_video.data
        if isinstance(raw, str):
            video_data = base64.b64decode(raw)
        elif isinstance(raw, bytes):
            video_data = raw

    if not video_data:
        # Fallback check through steps if not populated directly on output_video
        steps = getattr(interaction, "steps", []) or []
        for step in reversed(steps):
            content = getattr(step, "content", []) or []
            if isinstance(content, list):
                for item in reversed(content):
                    if getattr(item, "type", None) == "video" and getattr(item, "data", None):
                        raw = item.data
                        video_data = base64.b64decode(raw) if isinstance(raw, str) else raw
                        break
            if video_data:
                break

    if not video_data:
        raise RuntimeError("No video data was returned by the gemini-omni-flash-preview model.")

    # 1. Save artifact with tool_context.save_artifact so it appears in Playground's Artifacts panel
    clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", destination_or_lodging.lower())[:30]
    unique_suffix = uuid.uuid4().hex[:6]
    artifact_filename = f"video_{clean_name}_{unique_suffix}.mp4"

    artifact_part = types.Part.from_bytes(data=video_data, mime_type="video/mp4")
    try:
        await tool_context.save_artifact(
            filename=artifact_filename,
            artifact=artifact_part,
            custom_metadata={
                "type": "video",
                "destination": destination_or_lodging,
            },
        )
    except Exception as e:
        print(f"Warning: Failed to save artifact via tool_context: {e}")

    # 2. Upload video bytes to public Cloud Storage bucket and return public HTTPS URL
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    object_name = f"videos/{artifact_filename}"
    blob = bucket.blob(object_name)

    blob.upload_from_string(video_data, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{object_name}"
    return public_url
