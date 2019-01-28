#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from ics import Calendar
from pprint import pprint
from ics import Event
import requests
import arrow


class HolidaysCal:
    """Todo: Docstring
    """
    def __init__(self, url):
        """

        :url: URL to an ics calendar
        :returns: HolidaysCal object

        """
        self.__url = url

        self.__calendar = Calendar(requests.get(self.__url).text)

    def GetEvents(self, days):
        """TODO: Docstring for GetEvents.

        :days: days to check from now
        :returns: list of events within `days`

        """
        ev = Event(begin=arrow.utcnow(),
                   end=arrow.utcnow().replace(days=days))
        ev.make_all_day()
        return_events = []

        for _ in self.__calendar.events:     # for each event in calendar
            if _.intersects(ev):
                return_events.append(_)

        return sorted(return_events, key=lambda event: event.begin)


def send_slack(webhook_url, channel, text):
    """TODO: Docstring for send_slack.

    :channel: TODO
    :title: TODO
    :message: TODO
    :attachments: list of attachments
    :returns: TODO

    """

    slack_data = text

    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


if __name__ == "__main__":

    try:
        webhook_url = os.environ["SLACK_HB_WEBHOOK"]
        days = int(os.environ["SLACK_HB_DAYS"])
    except Exception as e:
        print("OS variable is not defined, exiting")
        raise e

    url = {'USA': 'https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics',
        'Singapore': 'https://calendar.google.com/calendar/ical/en.singapore%23holiday%40group.v.calendar.google.com/public/basic.ics',
        'France': 'https://calendar.google.com/calendar/ical/en.french%23holiday%40group.v.calendar.google.com/public/basic.ics',
        'Japan': 'https://calendar.google.com/calendar/ical/en.japanese%23holiday%40group.v.calendar.google.com/public/basic.ics',
        'Ireland': 'https://calendar.google.com/calendar/ical/en.irish%23holiday%40group.v.calendar.google.com/public/basic.ics'}

    flags = {
        'USA': ':flag-us:',
        'Singapore': ':flag-sg:',
        'France': ':flag-fr:',
        'Japan': ':flag-jp:',
        'Ireland': ':flag-ie:'
    }

    output = []

    output_json = {
        "attachments": [
            {
                "title": "Holidays in next {} days".format(days),
                "attachment_type": "default",
                "color": "#764FA5",
                "fields": [],
            }
        ]
    }

    for k, v in url.items():
        country = k
        flag = flags[k]
        c = HolidaysCal(url[k])
        holidays = None
        holidays = c.GetEvents(days)

        if holidays:
            output = []

            for _ in holidays:
                output.append(_.name)
                output.append(" - ")
                output.append(
                    "{} ({})".format(_.begin.humanize(),
                    _.begin.format('MMMM DD, YYYY')
                                    )
                )

                output.append("\n")
                # we have now a list of holiday for a country in output

            output_json['attachments'][0]['fields'].append(
                {
                    "title": country+" "+flag,
                    "value": "",
                    "short": True
                }
            )

            output_json['attachments'][0]['fields'].append(
                {
                    "title": "",
                    "value": ''.join(output),
                    "short": False
                }
            )

    send_slack(webhook_url=webhook_url, channel='', text=output_json)
