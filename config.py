#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 8000
    HOST = "0.0.0.0"
    APP_ID = os.environ.get("MICROSOFTAPPID", "")
    APP_PASSWORD = os.environ.get("MICROSOFTAPPPASSWORD", "")   
    LUIS_APP_ID = os.environ.get("LUISAPPID", "")
    LUIS_API_KEY = os.environ.get("LUISAPIKEY", "")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LUISAPIHOSTNAME", "")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "APPINSIGHTSINSTRUMENTATIONKEY", ""
    )

