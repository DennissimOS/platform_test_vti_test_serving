#!/usr/bin/env python
#
# Copyright (C) 2017 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import webapp2

from google.appengine.api import users

from webapp.src import webapp_config
from webapp.src.proto import model


class DevicePage(webapp2.RequestHandler):
    """Main class for /device web page."""

    def get(self):
        """Generates an HTML page based on the device info kept in DB."""
        device_query = model.DeviceModel.query()
        devices = device_query.fetch()

        lab_query = model.LabModel.query()
        labs = lab_query.fetch()

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = "Logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = "Login"

        template_values = {
            "user": user,
            "now": datetime.datetime.now(),
            "devices": devices,
            "labs": labs,
            "url": url,
            "url_linktext": url_linktext,
        }

        template = webapp_config.JINJA_ENVIRONMENT.get_template(
            "static/device.html")
        self.response.write(template.render(template_values))
