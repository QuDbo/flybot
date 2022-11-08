# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails

import re


class Intent(Enum):
    # BOOK_FLIGHT = "BookFlight"
    BOOK_FLIGHT = "BookingFlight"
    CANCEL = "Cancel"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    THANKYOU = "thankyou"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()
                result.initial_demand = recognizer_result.text
                result.resolver_dialog = []
                # We need to get the result from the LUIS JSON which at every level returns an array.
                # to_entities = recognizer_result.entities.get("$instance", {}).get(
                    # "To", []
                # )
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Destination", []
                )
                if len(to_entities) > 0:
                    # if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                    #     "$instance"
                    # ]:
                    if recognizer_result.entities.get("Destination", ["Neverland"])[0]:
                        result.destination = to_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            to_entities[0]["text"].capitalize()
                        )

                # from_entities = recognizer_result.entities.get("$instance", {}).get(
                    # "From", []
                # )
                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Origin", []
                )
                if len(from_entities) > 0:
                    # if recognizer_result.entities.get("From", [{"$instance": {}}])[0][
                    #     "$instance"
                    # ]:
                    if recognizer_result.entities.get("Origin", ["Neverland"])[0]:
                        result.origin = from_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            from_entities[0]["text"].capitalize()
                        )

                # Budget
                max_budget_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Budget", []
                )
                if len(max_budget_entities) > 0:
                    if recognizer_result.entities.get("Budget", [0])[0]:
                        result.budget = max_budget_entities[0]["text"]
                
                # number of adults
                adult_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Number_of_adults", []
                )
                if len(adult_entities) > 0:
                    if recognizer_result.entities.get("Number_of_adults", [1])[0]:
                        result.adults = adult_entities[0]["text"]
                
                # number of child
                child_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Number_of_children", []
                )
                if len(child_entities) > 0:
                    if recognizer_result.entities.get("Number_of_children", [0])[0]:
                        result.children = child_entities[0]["text"]
                
                # ticket class
                class_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Class", []
                )
                if len(class_entities) > 0:
                    if recognizer_result.entities.get("Class", [0])[0]:
                        result.ticket_class = class_entities[0]["text"]
                        
                # travel date
                travel_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Travel date", []
                )
                if len(travel_date_entities) > 0:
                    if recognizer_result.entities.get("Travel Date", ["today"])[0]:
                        result.travel_date = travel_date_entities[0]["text"]
                
                # return date
                return_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Return date", []
                )
                if len(return_date_entities) > 0:
                    if recognizer_result.entities.get("Return date", ["tomorrow"])[0]:
                        result.return_date = return_date_entities[0]["text"]
                
                # geography entities
                geography_entities = recognizer_result.entities.get("$instance", {}).get(
                    "geographyV2_city", []
                )
                if len(geography_entities) > 0:
                    if recognizer_result.entities.get("geographyV2_city", ["Neverland"])[0]:
                        for geo in geography_entities:
                            result.geo += [geo["text"].capitalize()]
                            
                # datetime entities
                dt_entities = recognizer_result.entities.get("$instance", {}).get(
                    "datetime", []
                )
                if len(dt_entities) > 0:
                    if recognizer_result.entities.get("datetimeV2", ["today"])[0]:
                        for date in dt_entities:
                            result.datetimeV2 += [date["text"]]
                            
                # number entities
                nb_entities = recognizer_result.entities.get("$instance", {}).get(
                    "number", []
                )
                if len(nb_entities) > 0:
                    if recognizer_result.entities.get("number", [0])[0]:
                        for nb in nb_entities:
                            result.number += [nb["text"]]
                        
                # # Add some rule to verify stuff or interpreted more ?
                        
                # # # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
                # # # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
                # # # e.g. missing a Year.
                # # date_entities = recognizer_result.entities.get("datetime", [])
                # # if date_entities:
                # #     timex = date_entities[0]["timex"]

                # #     if timex:
                # #         datetime = timex[0].split("T")[0]

                # #         result.travel_date = datetime

                # # else:
                # #     result.travel_date = None

        except Exception as exception:
            print(exception)

        return intent, result
