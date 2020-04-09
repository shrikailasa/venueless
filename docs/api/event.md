Event configuration
===================

The event configuration is pushed directly after websocket connect with a message structured as

    <- ["event.config", { … }]
    
The body of the configuration is strucured like this:

    {
        "event": {
            "title": "Unsere tolle Online-Konferenz",
        },
        "rooms": [
            {
                "id": "room_1",
                "name": "Plenum",
                "description": "Hier findet die Eröffnungs- und End-Veranstaltung statt",
                "picture": "https://via.placeholder.com/150",
                "access": [
                    {
                        "level": "viewer",
                        "required_groups": "*"
                    },
                    {
                        "level": "moderator",
                        "required_groups": "moderator_plenum"
                    }
                ],
                "modules": [
                    {
                        "type": "livestream.native",
                        "config": {
                            "hls_url": "https://s1.live.pretix.eu/test/index.m3u8"
                        }
                    },
                    {
                        "type": "chat.native",
                        "config": {
                        }
                    },
                    {
                        "type": "agenda.pretalx",
                        "config": {
                            "api_url": "https://pretalx.com/conf/online/schedule/export/schedule.json",
                            "room_id": 3
                        }
                    }
                ]
            },
            {
                "id": "room_2",
                "name": "Gruppenraum 1",
                "description": "Hier findet die Eröffnungs- und End-Veranstaltung statt",
                "picture": "https://via.placeholder.com/150",
                "access": [
                    {
                        "level": "viewer",
                        "required_groups": "*"
                    },
                    {
                        "level": "moderator",
                        "required_groups": "moderator_plenum"
                    }
                ],
                "modules": [
                    {
                        "type": "call.bigbluebutton",
                        "config": {
                            "bbb_join_url": "https://s1.live.pretix.eu/test/index.m3u8"
                        }
                    }
                ]
            }
        ]
    }