import os
from dotenv import load_dotenv
from lumaai import LumaAI
import requests
import time
import logging

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv('LUMAAI_API_KEY')

# Initialize the LumaAI client
client = LumaAI()
client.api_key = api_key

# Set up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

generation = client.generations.create(
    prompt="a cartoon video of a flower blooming in a coffee shop",
)
# generation = client.generations.create(
#     prompt="Man giving a wink with a discrete lip smile",
#     keyframes={
#       "frame0": {
#         "type": "image",
#         "url": "https://drive.google.com/file/d/1k0T7NJOmupt2FXIdcF89AzhdSOoTZ1Vn/view?usp=sharing"
#       }
#     }
# )

# Check the status of the generation
generation_id = generation.id
status = client.generations.get(generation_id).state

print(f"Generation status: {status}")

# Poll for completion
max_attempts = 30
attempt = 0
while attempt < max_attempts:
    status = client.generations.get(generation_id).state
    logger.info(f"Generation status: {status}")
    
    if status == "completed":  # Note: changed from "complete" to "completed"
        # Retrieve the result
        result = client.generations.get(generation_id)
        print(result)
        print(dir(result))
        
        # Download the video
        print(result.assets)
        output_url = result.assets.video  # or whatever the correct field is
        response = requests.get(output_url)
        if response.status_code == 200:
            with open("output_video.mp4", "wb") as file:
                file.write(response.content)
            logger.info("Video saved as output_video.mp4")
        else:
            logger.error("Failed to download the video")
        break
    elif status == "failed":
        generation = client.generations.get(generation_id)
        if generation.state == "failed":
            failure_reason = generation.failure_reason
            logger.error(f"Generation failed. Reason: {failure_reason}")
            if failure_reason == "Frame moderation failed":
                logger.warning("The input image may have violated content guidelines. Please check your input and try again with a different image.")
        else:
            # Handle unexpected state
            logger.warning(f"Unexpected state encountered: {generation.state}")
        break
    else:
        attempt += 1
        time.sleep(10)  # Wait for 10 seconds before checking again

if attempt == max_attempts:
    logger.warning("Generation did not complete within the expected time.")