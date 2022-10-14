#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    # APP_ID = os.environ.get("MicrosoftAppId", "")
    # APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_ID = ""
    APP_PASSWORD = ""    
    # LUIS_APP_ID = os.environ.get("LuisAppId", "")
    # LUIS_API_KEY = os.environ.get("LuisAPIKey", "")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    # LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "")
    # APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
    #     "AppInsightsInstrumentationKey", ""
    # )
    LUIS_API_HOST_NAME = "francecentral.api.cognitive.microsoft.com"
    LUIS_APP_ID = "0a91afe0-750a-4339-baab-b238d9f84e5b"
    LUIS_API_KEY = "e49c1e19e82245e5a61af32b8c71334f"
    APPINSIGHTS_INSTRUMENTATION_KEY = "eae92f51-bcc8-4fa0-abcd-2a5e090a2a11"
