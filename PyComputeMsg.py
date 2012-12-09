'''
 PyComputeMsg by Hesam Rabeti

 This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

CLIENT_TERMINATED = 1
CLIENT_SHUTDOWN = 2
CLIENT_STARTED = 3
CLIENT_TASK_DONE = 4
CLIENT_REQUEST_TASKS = 5
CLIENT_REQUEST_CODE = 6
CLIENT_TASK_ERROR = 7

SERVER_TASKS_ASSIGNED = 1000000
SERVER_NO_TASKS = 1000001

SERVER_RESET_CLIENT = 1000002
SERVER_SEND_CODE = 1000003

PROCESS_TASK = 2000002
PROCESS_TERMINATE = 2000000
PROCESS_TERMINATED = 2000001