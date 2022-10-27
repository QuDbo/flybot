# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Handle cancel and help intents."""

from botbuilder.core import BotTelemetryClient, NullTelemetryClient
from botbuilder.dialogs import (
    ComponentDialog,
    DialogContext,
    DialogTurnResult,
    DialogTurnStatus,
)
from botbuilder.schema import ActivityTypes

from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper, Intent

from config import DefaultConfig

class CancelAndHelpDialog(ComponentDialog):
    """Implementation of handling cancel and help."""

    def __init__(
        self,
        dialog_id: str,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(CancelAndHelpDialog, self).__init__(dialog_id)
        self.telemetry_client = telemetry_client

    async def on_begin_dialog(
        self, inner_dc: DialogContext, options: object
    ) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_begin_dialog(inner_dc, options)

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_continue_dialog(inner_dc)

    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        """Detect interruptions."""
        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()

            if text in ("help", "?"):
                await inner_dc.context.send_activity("Show Help...")
                return DialogTurnResult(DialogTurnStatus.Waiting)

            if text in ("cancel", "quit"):
                await inner_dc.context.send_activity("Cancelling")
                return await inner_dc.cancel_all_dialogs()
            
            # Capture the response to the previous step's prompt
            # previous_response = step_context.result
            previous_response = inner_dc.context
            mini_recognizer = FlightBookingRecognizer(DefaultConfig)
            
            mini_intent, mini_luis_result = await LuisHelper.execute_luis_query(
                mini_recognizer, turn_context=previous_response
            )
            
            if mini_intent == Intent.GOODBYE.value :
                await inner_dc.context.send_activity("Have a nice day !")
                await inner_dc.context.send_activity("This conversation is over. Retype something or refresh to restart.")
                return await inner_dc.cancel_all_dialogs()         
                
        return None
