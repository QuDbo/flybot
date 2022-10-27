import sys
import os
import aiounittest
import json

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from helpers.luis_helper import LuisHelper
from flight_booking_recognizer import FlightBookingRecognizer
from config import DefaultConfig
from botbuilder.core import TurnContext
from botbuilder.core.adapters import TestAdapter
from booking_details import BookingDetails

class TestLuisResponse(aiounittest.AsyncTestCase):
    async def test_intent_luis(self): 
        async def exec_test(turn_context : TurnContext):
            test_intent, test_luis_result = await LuisHelper.execute_luis_query(
                test_recognizer, turn_context=turn_context
            )
            await turn_context.send_activity(test_intent)

        # LUIS Configuration like in the bot 
        test_recognizer = FlightBookingRecognizer(DefaultConfig)

        adapter = TestAdapter(exec_test)
        
        # Testing Intent from examples
        await adapter.test("I want to go to Paris",
                           "BookingFlight"
                           )
        await adapter.test("Get me to paris from london for less than 400$.",
                           "BookingFlight"
                           )
        await adapter.test("We would like to go on vacation",
                           "BookingFlight"
                           )
        
    async def test_other_intent_luis(self): 
        async def exec_test(turn_context : TurnContext):
            test_intent, test_luis_result = await LuisHelper.execute_luis_query(
                test_recognizer, turn_context=turn_context
            )
            await turn_context.send_activity(test_intent)

        # LUIS Configuration like in the bot 
        test_recognizer = FlightBookingRecognizer(DefaultConfig)

        adapter = TestAdapter(exec_test)
        
        # Testing Intent from examples
        await adapter.test("Hello",
                           "greeting"
                           )
        await adapter.test("Bye !",
                           "goodbye"
                           )
        await adapter.test("Thanks !",
                           "thankyou"
                           )
    
    async def test_entities_recognition(self):
        # LUIS Configuration like in the bot 
        test_recognizer = FlightBookingRecognizer(DefaultConfig)
        
        async def exec_test(turn_context : TurnContext):
            test_intent, test_luis_result = await LuisHelper.execute_luis_query(
                test_recognizer, turn_context=turn_context
            )
            await turn_context.send_activity(json.dumps(test_luis_result.__dict__))

        adapter = TestAdapter(exec_test)
        
        # Testing Entities from examples
        # Use BookingDetails to fill the empty entities
        test = BookingDetails(destination="Paris")
        await adapter.test("I want to go to Paris",
                           json.dumps(test.__dict__)
                           )
        test = BookingDetails(destination="Paris",
                                          origin="London",
                                          budget="400 $")
        await adapter.test("Get me to paris from london for less than 400$.",
                           json.dumps(test.__dict__)
                           )
        test = BookingDetails()
        await adapter.test("We would like to go on vacation",
                           json.dumps(test.__dict__)
                           )
        
        
