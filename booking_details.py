# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        travel_date: str = None,
        return_date: str = None,
        adults: int = None,
        children: int = None,
        ticket_class : str = None,
        budget : int = None, 
        unsupported_airports=None,
        initial_demand : str = None,
        trace_input=[],
        geo=[],
        datetimeV2=[],
        number=[],
    ):
        if unsupported_airports is None:
            unsupported_airports = []
        self.destination = destination
        self.origin = origin
        self.travel_date = travel_date
        self.return_date = return_date
        self.adults = adults
        self.children = children
        self.ticket_class = ticket_class
        self.budget = budget
        self.unsupported_airports = unsupported_airports
        self.initial_demand = initial_demand
        self.trace_input = trace_input
        self.geo = geo
        self.datetimeV2 = datetimeV2
        self.number=number
