# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import (
    MessageFactory,
    TurnContext,
    BotTelemetryClient,
    NullTelemetryClient,
)
from botbuilder.schema import InputHints

from booking_details import BookingDetails
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper, Intent
from .booking_dialog import BookingDialog


class MainDialog(ComponentDialog):
    def __init__(
        self,
        luis_recognizer: FlightBookingRecognizer,
        booking_dialog: BookingDialog,
        telemetry_client: BotTelemetryClient = None,
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.telemetry_client = telemetry_client or NullTelemetryClient()

        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = self.telemetry_client

        booking_dialog.telemetry_client = self.telemetry_client

        wf_dialog = WaterfallDialog(
            "WFDialog", [self.intro_step, self.act_step, self.final_step]
        )
        wf_dialog.telemetry_client = self.telemetry_client

        self._luis_recognizer = luis_recognizer
        self._booking_dialog_id = booking_dialog.id

        self.add_dialog(text_prompt)
        self.add_dialog(booking_dialog)
        self.add_dialog(wf_dialog)

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)
        message_text = (
            str(step_context.options)
            if step_context.options
            else "Can you tell me about your trip ?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            # LUIS is not configured, we just run the BookingDialog path with an empty BookingDetailsInstance.
            return await step_context.begin_dialog(
                self._booking_dialog_id, BookingDetails()
            )

        # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )
        
        if intent == Intent.BOOK_FLIGHT.value and luis_result:
            # Show a warning for Origin and Destination if we can't resolve them.
            await MainDialog._show_warning_for_unsupported_cities(
                step_context.context, luis_result
            )

            # Run the BookingDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._booking_dialog_id, luis_result)

        elif intent == Intent.GREETING.value:
            greeting_text = (
                "Hi !"
            )
            greeting_message = MessageFactory.text(
                greeting_text, greeting_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(greeting_message)
            prompt_message = "Can you tell me about your trip ?"
            return await step_context.replace_dialog(self.id, prompt_message)
        
        elif intent == Intent.GOODBYE.value:
            goodbye_text = (
                "Have a nice day !"
            )
            goodbye_message = MessageFactory.text(
                goodbye_text, goodbye_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(goodbye_message)
            
            close_text = (
                "This conversation is over. Retype something or refresh to restart."
            )
            close_message = MessageFactory.text(
                close_text, close_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(close_message)
            return await inner_dc.cancel_all_dialogs()
            
        elif intent == Intent.THANKYOU.value:
            thank_text = (
                "You're welcome."
            )
            thank_message = MessageFactory.text(
                thank_text, thank_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(thank_message)
            prompt_message = "Can you tell me about your trip ?"
            return await step_context.replace_dialog(self.id, prompt_message)

        else:
            # didnt_understand_text = (
            #     "Sorry, I didn't get that. Please try asking in a different way."
            # )
            # didnt_understand_message = MessageFactory.text(
            #     didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            # )
            # await step_context.context.send_activity(didnt_understand_message)
            prompt_message = "Sorry, I didn't get that. Please try asking in a different way."
            return await step_context.replace_dialog(self.id, prompt_message)

        return await step_context.next(None)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # If the child dialog ("BookingDialog") was cancelled or the user failed to confirm,
        # the Result here will be null.
        if step_context.result is not None:
            if (step_context.result):
                msg_txt = "This is (imaginary) booked !"
                message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
                await step_context.context.send_activity(message)
                prompt_message = "Is there something else I can do for you?"
                return await step_context.replace_dialog(self.id, prompt_message)
            else:
                msg_txt = "Sorry that I didn't understand your request."
                message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
                await step_context.context.send_activity(message)
                msg_txt = "I'm just a bot and i'm still in early development..."
                message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
                await step_context.context.send_activity(message)
                prompt_message = "Can you explain me again your trip, like I'm a 3yo child ?"
                return await step_context.replace_dialog(self.id, prompt_message)
            
        return await step_context.end_dialog()
    
    @staticmethod
    async def _show_warning_for_unsupported_cities(
        context: TurnContext, luis_result: BookingDetails
    ) -> None:
        """
        Shows a warning if the requested From or To cities are recognized as entities but they are not in the Airport entity list.
        In some cases LUIS will recognize the From and To composite entities as a valid cities but the From and To Airport values
        will be empty if those entity values can't be mapped to a canonical item in the Airport.
        """
        if luis_result.unsupported_airports:
            message_text = (
                f"Sorry but the following airports are not supported:"
                f" {', '.join(luis_result.unsupported_airports)}"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await context.send_activity(message)
