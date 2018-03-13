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
"""Job Queue Info APIs implemented using Google Cloud Endpoints."""

import datetime
import endpoints
import logging

from protorpc import remote

from webapp.src.proto import model
from webapp.src import vtslab_status as Status

JOB_QUEUE_RESOURCE = endpoints.ResourceContainer(model.JobMessage)


@endpoints.api(name='job_queue', version='v1')
class JobQueueApi(remote.Service):
    """Endpoint API for job_queue."""

    @endpoints.method(
        JOB_QUEUE_RESOURCE,
        model.JobLeaseResponse,
        path='get',
        http_method='POST',
        name='get')
    def get(self, request):
        """Gets the job(s) based on the condition specified in `request`."""
        job_query = model.JobModel.query(
            model.JobModel.hostname == request.hostname,
            model.JobModel.status == Status.JOB_STATUS_DICT["ready"])
        existing_jobs = job_query.fetch()

        def PrioritySortHelper(priority):
            if priority == "high":
                return 1
            elif priority == "low":
                return 3
            else:
                return 2

        priority_sorted_jobs = sorted(
            existing_jobs,
            key=lambda x: (PrioritySortHelper(x.priority), x.timestamp))

        job_message = model.JobMessage()
        job_message.hostname = ""
        job_message.priority = ""
        job_message.test_name = ""
        job_message.device = ""
        job_message.serial = [""]
        job_message.manifest_branch = ""
        job_message.build_target = ""
        job_message.shards = 0
        job_message.param = [""]
        job_message.build_id = ""
        job_message.status = 0
        job_message.period = 0
        job_message.retry_count = 0

        if priority_sorted_jobs:
            job = priority_sorted_jobs[0]
            job.status = Status.JOB_STATUS_DICT["leased"]
            job.put()

            job_message.hostname = job.hostname
            job_message.priority = job.priority
            job_message.test_name = job.test_name
            job_message.device = job.device
            job_message.serial = job.serial
            job_message.manifest_branch = job.manifest_branch
            job_message.build_target = job.build_target
            job_message.shards = job.shards
            job_message.param = job.param
            job_message.build_id = job.build_id
            job_message.status = job.status
            job_message.period = job.period
            job_message.retry_count = job.retry_count
            job_message.gsi_branch = job.gsi_branch
            job_message.gsi_build_target = job.gsi_build_target
            job_message.gsi_pab_account_id = job.gsi_pab_account_id
            job_message.test_branch = job.test_branch
            job_message.test_build_target = job.test_build_target
            job_message.test_pab_account_id = job.test_pab_account_id

            device_query = model.DeviceModel.query(
                model.DeviceModel.serial.IN(job.serial))
            devices = device_query.fetch()
            for device in devices:
                device.scheduling_status = Status.DEVICE_SCHEDULING_STATUS_DICT[
                    "use"]
                device.put()

            return model.JobLeaseResponse(
                return_code=model.ReturnCodeMessage.SUCCESS,
                jobs=[job_message])
        else:
            return model.JobLeaseResponse(
                return_code=model.ReturnCodeMessage.FAIL, jobs=[job_message])

    @endpoints.method(
        JOB_QUEUE_RESOURCE,
        model.JobLeaseResponse,
        path='heartbeat',
        http_method='POST',
        name='heartbeat')
    def heartbeat(self, request):
        """Processes the heartbeat signal from HC which leased queued job(s)."""
        # minify jobs by query and confirm with serial from fetched jobs
        job_query = model.JobModel.query(
            model.JobModel.hostname == request.hostname,
            model.JobModel.manifest_branch == request.manifest_branch,
            model.JobModel.build_target == request.build_target,
            model.JobModel.test_name == request.test_name,
            model.JobModel.status == Status.JOB_STATUS_DICT["leased"])
        existing_jobs = job_query.fetch()
        same_jobs = [
            x for x in existing_jobs if set(x.serial) == set(request.serial)
        ]

        job_message = model.JobMessage()
        job_messages = []

        if len(same_jobs) > 1:
            logging.warning("[heartbeat] more than one job is found!")
            logging.warning(
                "[heartbeat] <hostname>{} <manifest_branch>{} "
                "<build_target>{} <test_name>{} <serials>{}".
                format(request.hostname, request.manifest_branch,
                       request.build_target, request.test_name, request.serial))

        if same_jobs:
            job = same_jobs[0]
            job_message.hostname = job.hostname
            job_message.priority = job.priority
            job_message.test_name = job.test_name
            job_message.device = job.device
            job_message.serial = job.serial
            job_message.manifest_branch = job.manifest_branch
            job_message.build_target = job.build_target
            job_message.shards = job.shards
            job_message.param = job.param
            job_message.build_id = job.build_id
            job_message.status = job.status
            job_message.period = job.period
            job_message.retry_count = job.retry_count
            job_messages.append(job_message)
            device_query = model.DeviceModel.query(
                model.DeviceModel.serial.IN(job.serial))
            devices = device_query.fetch()
            if request.status in [
                    Status.JOB_STATUS_DICT["complete"],
                    Status.JOB_STATUS_DICT["infra-err"]
            ]:
                for device in devices:
                    device.scheduling_status =\
                        Status.DEVICE_SCHEDULING_STATUS_DICT["free"]
                    device.put()
            elif request.status == Status.JOB_STATUS_DICT["leased"]:
                for device in devices:
                    device.timestamp = datetime.datetime.now()
                    device.put()

            job.status = request.status
            job.heartbeat_stamp = datetime.datetime.now()
            job.put()
            return model.JobLeaseResponse(
                return_code=model.ReturnCodeMessage.SUCCESS, jobs=job_messages)

        return model.JobLeaseResponse(
            return_code=model.ReturnCodeMessage.FAIL, jobs=job_messages)