# Copyright 2017 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Build Info APIs implemented using Google Cloud Endpoints."""

import datetime
import endpoints

from protorpc import remote

from webapp.src.proto import model


BUILD_INFO_RESOURCE = endpoints.ResourceContainer(
    model.BuildInfoMessage)


@endpoints.api(name="build_info", version="v1")
class BuildInfoApi(remote.Service):
    """Endpoint API for build_info."""

    @endpoints.method(
        BUILD_INFO_RESOURCE,
        model.DefaultResponse,
        path="set",
        http_method="POST",
        name="set")
    def set(self, request):
        """Sets the build info based on the `request`."""
        build_query = model.BuildModel.query()
        existing_builds = build_query.fetch()

        found = False
        for existing_build in existing_builds:
            if (request.build_id == existing_build.build_id and
                request.build_target == existing_build.build_target and
                request.build_type == existing_build.build_type):
                found = True
                break

        if not found:
            build = model.BuildModel()
            build.manifest_branch = request.manifest_branch
            build.build_id = request.build_id
            build.build_target = request.build_target
            build.build_type = request.build_type
            build.artifact_type = request.artifact_type
            build.artifacts = request.artifacts
            build.timestamp = datetime.datetime.now()
            build.put()

        return model.DefaultResponse(
            return_code=model.ReturnCodeMessage.SUCCESS)
