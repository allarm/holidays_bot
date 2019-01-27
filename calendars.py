#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
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
        return return_events


def send_slack(webhook_url, channel, text):
    """TODO: Docstring for send_slack.

    :channel: TODO
    :title: TODO
    :message: TODO
    :attachments: list of attachments
    :returns: TODO

    """

    # slack_data = {
    #     'link_names': 1,
    #     "text": text,
    #     "attachments": attachments,
    #     'username': 'Holidays Bot',
    #     'icon_emoji': ':robot_face:',
    #     'channel': channel,
    # }

    slack_data = text

    # print(slack_data)
    # exit()
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

    days = 30

    webhook_url = 'https://hooks.slack.com/services/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'

    url = {'USA': 'https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics',
        'Singapore': 'https://calendar.google.com/calendar/ical/en.singapore%23holiday%40group.v.calendar.google.com/public/basic.ics',
        'Ireland': 'https://calendar.google.com/calendar/ical/en.irish%23holiday%40group.v.calendar.google.com/public/basic.ics'}

    flags = {
        'USA': ':flag-us',
        'Singapore': ':flag-sg',
        'Ireland': ':flag-ir'
    }

    output=[]

    output_json= {
        "attachments": [
            {
                "title": "Holidays",
                "attachment_type": "default",
                "color": "#764FA5",
                "fields": [ ],
            }
        ]
    }

    for k, v in url.items():
        country = k
        c = HolidaysCal(url[k])
        holidays = None
        holidays = c.GetEvents(days)

        if holidays:
            # print('Holidays in {}'.format(country))
            # output.append("Holidays in {}".format(country))

            print(holidays)

            output=[]

            for _ in holidays:
                output.append(_.name)
                output.append(" - ")
                output.append("{} ({})".format(_.begin.humanize(),
                                _.begin.format('MMMM DD, YYYY')))
                output.append("\n\n")
                # we have now a list of holiday for a country in output

            output_json['attachments'][0]['fields'].append(
                {
                    "title": country,
                    "value": "",
                    "short": True
                }
            )

            output_json['attachments'][0]['fields'].append(
                {
                    "title": "Holidays",
                    "value": ''.join(output),
                    "short": False
                }
            )

    pprint(output_json)

    send_slack(webhook_url=webhook_url, channel='', text=output_json)
