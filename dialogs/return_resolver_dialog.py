# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Handle date/time resolution for booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.dialogs import WaterfallDialog, DialogTurnResult, WaterfallStepContext
from botbuilder.dialogs.prompts import (
    DateTimePrompt,
    PromptValidatorContext,
    PromptOptions,
    DateTimeResolution,
    TextPrompt,
)
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from helpers.luis_helper import LuisHelper, Intent
from flight_booking_recognizer import FlightBookingRecognizer
from config import DefaultConfig

class ReturnResolverDialog(CancelAndHelpDialog):
    """Resolve the return date"""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(ReturnResolverDialog, self).__init__(
            dialog_id or ReturnResolverDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client

        # date_time_prompt = DateTimePrompt(
        #     DateTimePrompt.__name__, ReturnResolverDialog.datetime_prompt_validator
        # )
        date_time_prompt = TextPrompt(TextPrompt.__name__)
        date_time_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__ + "2", [self.initial_step,
                                             self.analysis_date_step,
                                             self.final_step]
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(date_time_prompt)
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__ + "2"

    async def initial_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for the date."""
        user_response = step_context.options
        prompt_msg = "On what date would you like to return?"
        reprompt_msg = (
            "I'm sorry, for best results, please enter your return "
            "date including the month, day and year."
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

        # # if timex is None:
        # #     # We were not given any date at all so prompt the user.
        # #     return await step_context.prompt(
        # #         DateTimePrompt.__name__,
        # #         PromptOptions(  # pylint: disable=bad-continuation
        # #             prompt=MessageFactory.text(prompt_msg),
        # #             retry_prompt=MessageFactory.text(reprompt_msg),
        # #         ),
        # #     )

        # # # We have a Date we just need to check it is unambiguous.
        # # if "definite" in Timex(timex).types:
        # #     # This is essentially a "reprompt" of the data we were given up front.
        # #     return await step_context.prompt(
        # #         DateTimePrompt.__name__, PromptOptions(prompt=reprompt_msg)
        # #     )

        # # return await step_context.next(DateTimeResolution(timex=timex))

    async def analysis_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        user_response = step_context.context
        
        # We should have a response, send it to luis  
        mini_recognizer = FlightBookingRecognizer(DefaultConfig)

        mini_intent, mini_luis_result = await LuisHelper.execute_luis_query(
                mini_recognizer, turn_context=user_response
        )

        if mini_intent == Intent.BOOK_FLIGHT.value:
            if mini_luis_result.return_date:
                to_return = {
                    'step_value' : mini_luis_result.return_date,
                    'input_user' : mini_luis_result.initial_demand
                }
                return await step_context.next(to_return)
            elif len(mini_luis_result.datetimeV2)>0:
                to_return = {
                    'step_value' : mini_luis_result.datetimeV2[-1],
                    'input_user' : mini_luis_result.initial_demand
                }
                return await step_context.next(to_return)
                
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
        # """Cleanup - set final return value and end dialog."""
        # timex = step_context.result[0].timex
        # to_return = {
        #             'step_value' : timex,
        #             'input_user' : "mini luis not implemented here"
        #         }
        # return await step_context.end_dialog(to_return)
        
        """Cleanup - set final return value and end dialog."""
        user_response = step_context.result
        return await step_context.end_dialog(user_response)
        

    # @staticmethod
    # async def datetime_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
    #     """ Validate the date provided is in proper form. """
    #     if prompt_context.recognized.succeeded:
    #         timex = prompt_context.recognized.value[0].timex.split("T")[0]

    #         # TODO: Needs TimexProperty
    #         return "definite" in Timex(timex).types

    #     return False
