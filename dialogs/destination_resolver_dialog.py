# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Handle destination resolution for booking dialog."""

from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.dialogs import WaterfallDialog, DialogTurnResult, WaterfallStepContext
from botbuilder.dialogs.prompts import (
    PromptOptions,
    TextPrompt,
)
from botbuilder.schema import InputHints

from .cancel_and_help_dialog import CancelAndHelpDialog
from helpers.luis_helper import LuisHelper, Intent
from flight_booking_recognizer import FlightBookingRecognizer
from config import DefaultConfig

class DestinationResolverDialog(CancelAndHelpDialog):
    """Resolve the destination"""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(DestinationResolverDialog, self).__init__(
            dialog_id or DestinationResolverDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client

        destination_prompt = TextPrompt(TextPrompt.__name__)
        destination_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__ + "2", [self.initial_step,
                                             self.analysis_step,
                                             self.final_step]
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(destination_prompt)
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__ + "2"

    async def initial_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for the destination."""
        user_response = step_context.options
        prompt_msg = "To what city would you like to travel?"
        reprompt_msg = (
            "I don't understand, please use syntax like 'I want to go to ...'"
        )
        if user_response is None:
            # We were not given any response at all so prompt the user.
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(  # pylint: disable=bad-continuation
                    prompt=MessageFactory.text(prompt_msg)
                ),
            )
        else:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(  # pylint: disable=bad-continuation
                    prompt=MessageFactory.text(reprompt_msg),
                ),
            )
    
    async def analysis_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        user_response = step_context.context
        # We should have a response, send it to luis  
        mini_recognizer = FlightBookingRecognizer(DefaultConfig)
        mini_intent, mini_luis_result = await LuisHelper.execute_luis_query(
                mini_recognizer, turn_context=user_response
        )

        if mini_intent == Intent.BOOK_FLIGHT.value:
            if mini_luis_result.destination:
                return await step_context.next(mini_luis_result.destination)
                
        if mini_intent == Intent.GREETING.value :
            greeting_text = (
                "Hi !"
            )
            greeting_message = MessageFactory.text(
                greeting_text, greeting_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(greeting_message)
            return await step_context.replace_dialog(self.id)
        if mini_intent == Intent.THANKYOU.value:
            thank_text = (
                "You're welcome."
            )
            thank_message = MessageFactory.text(
                thank_text, thank_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(thank_message)
            return await step_context.replace_dialog(self.id)

        return await step_context.replace_dialog(self.id, "hum...")

    async def final_step(self, step_context: WaterfallStepContext):
        """Cleanup - set final return value and end dialog."""
        user_response = step_context.result
        return await step_context.end_dialog(user_response)
