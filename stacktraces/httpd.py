# Copyright 2012 Jeff Trawick, http://emptyhammock.com/
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
#

import sys

# 't': thread name
# 's': thread state
#
# 'cdb': called directly by
# 'cib': called indirectly by
# 'cb': called by

httpd_annotations = [
    ('t', ['cdb', 'listener_thread', 'dummy_worker'], 'MPM child listener thread'),
    ('t', ['cdb', 'worker_thread', 'dummy_worker'], 'MPM child worker thread'),
    ('t', ['is', 'worker_thread'], 'MPM child worker thread'),
    ('t', ['cib', 'child_main', 'event_run'], 'Event MPM child main thread'),
    # less specific
    ('t', ['is', 'child_main'], 'MPM child main thread'),
    ('t', ['cib', 'ap_wait_or_timeout', 'event_run'], 'Event MPM parent'),
    # less specific
    ('t', ['is', 'ap_wait_or_timeout'], 'MPM parent'),
    ('t', ['is', 'cgid_server'], 'mod_cgid daemon'),
    ('t', ['is', 'ConnectionService'], 'SiteMinder thread'),
    ('t', ['ismatch', 'ManageAgentThread'], 'SiteMinder thread'),
    ('s', ['cdb', 'ap_queue_pop_something', 'worker_thread'], 'waiting for connection to handle'),
    ('s', ['cdb', 'ap_queue_pop', 'worker_thread'], 'waiting for connection to handle'),
    ('s', ['cdb', 'ap_queue_pop', 'dummy_worker'], 'waiting for connection to handle'),
    ('s', ['cdb', 'apr_pollset_poll', 'listener_thread'], 'waiting for connection to accept'),
    ('s', ['is', 'ap_event_pod_check'], 'waiting for termination event'),
    ('s', ['is', 'ap_worker_pod_check'], 'waiting for termination event'),
    ('s', ['is', 'ap_mpm_pod_check'], 'waiting for termination event'),
    ('s', ['is', 'ap_mpm_podx_check'], 'waiting for termination event'),
    ('s', ['is', 'ap_read_request'], 'reading client request'),
    ('s', ['cdb', 'apr_proc_mutex_lock', 'listener_thread'], 'waiting for accept mutex'),
    ('s', ['cdb', 'apr_thread_join', 'child_main'], 'waiting for threads to exit'),
    ('s', ['is', '__1cIcm_sleep6FLl_v_'], 'idle'),
    ('s', ['is', '__1cPCSmWorkerThreadFSleep6MLl_v_'], 'idle'),
    ('s', ['is', 'ap_lingering_close'], 'waiting for client to acknowledge connection close'),
    ('s', ['is', 'ap_run_handler'], 'running request handler'),
    ('s', ['cdb', 'ap_queue_push', 'listener_thread'], 'sending connection to worker thread'),
    ('s', ['cib', 'ap_wait_or_timeout', 'ap_run_mpm'], 'idle'),
]

# 'db': delete frames before
# 'da': delete frames after
# 'dda': delete frame and frames after
# 'd': delete frames in range
# 'df': delete first fram in range

httpd_cleanups = [
    ('db', ['is', 'apr_thread_mutex_unlock']),
    ('db', ['cdb', 'apr_thread_cond_wait', 'ap_queue_pop']),
    ('db', ['is', 'apr_sleep']),
    ('df', ['cdb', 'poll', 'poll']),
    ('da', ['is', 'dummy_worker']),
    ('db', ['is', 'apr_proc_mutex_lock']),
    ('db', ['is', 'ap_mpm_pod_check']),
    ('db', ['is', 'ap_event_pod_check']),
    ('db', ['is', 'apr_pollset_poll']),
    ('db', ['is', 'apr_thread_cond_wait']),
    ('db', ['is', 'apr_thread_join']),
    ('db', ['is', 'apr_poll']),
    ('da', ['is', 'main']),
    ('dda', ['is', '_lwp_start']),
]


if __name__ == "__main__":
    print >> sys.stderr, "Don't run this directly."
