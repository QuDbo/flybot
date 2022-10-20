# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog
from .return_resolver_dialog import ReturnResolverDialog

from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper

from config import DefaultConfig

class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.passenger_step,
                self.ticket_class_step,
                self.budget_step,
                self.travel_date_step,
                self.return_date_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            DateResolverDialog(DateResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            ReturnResolverDialog(ReturnResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for destination."""
        booking_details = step_context.options

        if booking_details.destination is None:
            modif_text = "To what city would you like to travel?"
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(modif_text)
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            modif_text = "From what city will you be travelling?"
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(modif_text)
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.origin)
    
    async def passenger_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt to specify the number of passengers."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.origin = step_context.result
        if booking_details.adults is None:
            modif_text = "How many adults and children ?"
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(modif_text)
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.adults)

    async def ticket_class_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt to specify the budget."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        # previous_response = step_context.result
        previous_response = step_context.context
        mini_recognizer = FlightBookingRecognizer(DefaultConfig)
        
        mini_intent, mini_luis_result = await LuisHelper.execute_luis_query(
            mini_recognizer, turn_context=previous_response
        )
        
        booking_details.adults = mini_luis_result.adults
        booking_details.children = mini_luis_result.children
        
        if booking_details.ticket_class is None:
            modif_text = "Do you want a sepcific seat class ?"
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(modif_text)
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.ticket_class)

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt to specify the budget."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.ticket_class = step_context.result
        if booking_details.budget is None:
            modif_text = "Do you have a maximal budget ?"
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(modif_text)
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.budget)

    async def travel_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.budget = step_context.result
        if not booking_details.travel_date or self.is_ambiguous(
            booking_details.travel_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, booking_details.travel_date
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.travel_date)
    
    async def return_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.travel_date = step_context.result
        if not booking_details.return_date or self.is_ambiguous(
            booking_details.return_date
        ):
            return await step_context.begin_dialog(
                ReturnResolverDialog.__name__, booking_details.return_date
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.return_date)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.return_date = step_context.result

        if booking_details.return_date:
            msg_return = f" You want to return on { booking_details.return_date}."
        else:
            msg_return = " This is a one-way ticket."
            
        if booking_details.budget:
            msg_budget = f" Your max budget is { booking_details.budget}."
        else:
            msg_budget = " You don't have a max budget."
            
        if booking_details.ticket_class:
            msg_class = f" Ticket will be in { booking_details.ticket_class} class."
        else:
            msg_class = " No specific seat class is demanded."

        n_adult = int(booking_details.adults)
        n_child = int(booking_details.children)
        if (n_adult>1) or (n_child>0):
            s_adult = "s" if (n_adult>1) else ""
            s_child = "ren" if (n_child>1) else ""
            with_child = f" and {n_child} child{s_child}." if (n_child>0) else "."
            msg_passenger = f" The trip concern {n_adult} adult{s_adult}{with_child}"

        msg = (
            f"Please confirm, I have you traveling to { booking_details.destination }"
            f" from { booking_details.origin } on { booking_details.travel_date}."
            f"{msg_return}"
            f"{msg_passenger}"
            f"{msg_class}"
            f"{msg_budget}"
            
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        if step_context.result:
            booking_details = step_context.options
            booking_details.return_date = step_context.result

            return await step_context.end_dialog(booking_details)

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
