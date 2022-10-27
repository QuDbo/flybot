# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import (
    WaterfallDialog, 
    WaterfallStepContext, 
    DialogTurnResult
)
from botbuilder.dialogs.prompts import (
    ConfirmPrompt, 
    TextPrompt, 
    PromptOptions,
    ChoicePrompt
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog
from .return_resolver_dialog import ReturnResolverDialog
from .destination_resolver_dialog import DestinationResolverDialog
from .origin_resolver_dialog import OriginResolverDialog
from .passenger_resolver_dialog import PassengerResolverDialog
from .child_resolver_dialog import ChildResolverDialog
from .budget_resolver_dialog import BudgetResolverDialog

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
                self.child_question_step,
                self.child_step,
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
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            DateResolverDialog(DateResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            ReturnResolverDialog(ReturnResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            DestinationResolverDialog(DestinationResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            OriginResolverDialog(OriginResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            PassengerResolverDialog(PassengerResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            ChildResolverDialog(ChildResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            BudgetResolverDialog(BudgetResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for destination."""
        booking_details = step_context.options

        if booking_details.destination is None:
            return await step_context.begin_dialog(
                DestinationResolverDialog.__name__, booking_details.destination
            )
            
        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        booking_details = step_context.options
        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        
        if booking_details.origin is None:
            return await step_context.begin_dialog(
                OriginResolverDialog.__name__, booking_details.origin
            )

        return await step_context.next(booking_details.origin)
    
    async def passenger_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt to specify the number of adults."""
        booking_details = step_context.options
        # Capture the response to the previous step's prompt
        booking_details.origin = step_context.result
        
        if booking_details.adults is None:
            return await step_context.begin_dialog(
                PassengerResolverDialog.__name__, booking_details.adults
            )

        return await step_context.next(booking_details.adults)

    async def child_question_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt to specify if there are children."""
        booking_details = step_context.options
        # Capture the response to the previous step's prompt
        booking_details.adults = step_context.result
        
        if booking_details.children is None:
            # Offer a YES/NO prompt.
            msg = "Is there any children ?"
            return await step_context.prompt(
                ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
            )
    
    async def child_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt to specify the number of children."""
        booking_details = step_context.options
        is_there_children = step_context.result
        
        booking_details.children = 0
        if (is_there_children):
            return await step_context.begin_dialog(
                ChildResolverDialog.__name__, None
            )
        
        return await step_context.next(booking_details.children)

    async def ticket_class_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt to specify the budget."""
        booking_details = step_context.options
        # Capture the response to the previous step's prompt
        booking_details.children = step_context.result
        
        if booking_details.ticket_class is None:
            list_of_choice = [Choice("Eco"),Choice("Business"),Choice("First"),Choice("Any")]
            modif_text = "Do you want a specific seat class ?"
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(modif_text),
                    choices=list_of_choice
                ),
            )

        return await step_context.next(booking_details.ticket_class)

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt to specify the budget."""
        booking_details = step_context.options
        # Capture the response to the previous step's prompt
        ticket_class = step_context.result.value
        booking_details.ticket_class = None if ticket_class=="Any" else ticket_class
        
        if booking_details.budget is None:
            return await step_context.begin_dialog(
                BudgetResolverDialog.__name__, None
            )

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

        if booking_details.adults:
            n_adult = int(booking_details.adults)
        else:
            n_adult=1
        
        if booking_details.children:
            n_child = int(booking_details.children)
        else:
            n_child = 0

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
        booking_details = step_context.options
        if (step_context.result):
            # return await step_context.end_dialog(booking_details)
            return await step_context.end_dialog(step_context.result)
        else:
            # Bot has failed, report it to Insight
            properties = {'interpreted_options': booking_details.__dict__}
            self.telemetry_client.track_trace("Bot failure", properties, "ERROR")
            
            # return await step_context.end_dialog()
            return await step_context.end_dialog(step_context.result)

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
