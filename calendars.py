#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ics import Calendar
from ics import Event
import requests
import arrow

class HolidaysCal:
    def __init__(self, url):
        """TODO: Docstring for __init__.

        :url: URL to an ics calendar
        :returns: TODO

        """
        self.__url=url

        self.__calendar = Calendar(requests.get(self.__url).text)

    def GetEvents(self, days):
        """TODO: Docstring for GetEvents.

        :days: days to check from now
        :returns: list of events

        """
        ev=Event(begin=arrow.utcnow(), end=arrow.utcnow().replace(days=days))
        ev.make_all_day()
        # print(ev)
        return_events=[]

        for _ in self.__calendar.events: # for each event in calendar
            if _.intersects(ev):
                return_events.append(_)
        return(return_events)

if __name__ == "__main__":

    days=30

    url = {'USA': 'https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics',
        'Singapore': 'https://calendar.google.com/calendar/ical/en.singapore%23holiday%40group.v.calendar.google.com/public/basic.ics',
        'Ireland': 'https://calendar.google.com/calendar/ical/en.irish%23holiday%40group.v.calendar.google.com/public/basic.ics'}


    for k,v in url.items():
        country=k
        c=HolidaysCal(url[k])
        holidays=c.GetEvents(days)

        if holidays:
            print('Holidays in {}'.format(country))
            for _ in holidays:
                print(_.name)
                print("{} ({})".format(_.begin.humanize(), _.begin.format('MMMM DD, YYYY')))
            print()

