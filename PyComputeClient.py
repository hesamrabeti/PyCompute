'''
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
    
from time import localtime, strftime, clock, sleep
import multiprocessing
from multiprocessing import Process, Queue
import PyComputeMsg

def NewChildProcess(task_queue, response_queue, process_id):
    import PyComputeClientProcessRemote
    client = PyComputeClientProcessRemote.PyComputeClientProcess()
    running = True
    while running == True:
        task_type, task_content = task_queue.get()
        if task_content != None:
            task_number = task_content[0]
            task = task_content[1]
            
        if task_type == PyComputeMsg.PROCESS_TERMINATE:
            message = (PyComputeMsg.PROCESS_TERMINATED, process_id)
            response_queue.put(message)
            running = False
        else:
            message = None
            if client.processTask(task) == True:
                message = (PyComputeMsg.CLIENT_TASK_DONE, task_number)
            else:
                message = (PyComputeMsg.CLIENT_TASK_ERROR, task_number)
            response_queue.put(message)

class PyComputeClient:
    conn = None
    server_address = None
    password = None
    max_processes = None

    reseting = False
    resets = 0
    processes = {}
    last_process = 0
    task_queue = Queue()
    response_queue = Queue()
    tasks_pending = 0
    no_task_retry_period = 5
    response_queue_get_wait = 5
    task_batch_size = 0
    
    total_tasks_completed = 0
    tasks_completed_since_last = 0
    
    def __init__(self, server_address=("127.0.0.1", 6666), password='password', 
                 max_processes=1):
        self.password = password
        self.server_address = server_address
        self.max_processes = max_processes
        self.task_max = self.max_processes * 4
        self.task_min = self.task_max / 2
        self.no_task_retry_period = 10
        
    def connectToServer(self, report):
        try:
            self.conn = multiprocessing.connection.Client(self.server_address, 
                                                "AF_INET", self.password)
        except:
            if report == True:
                print 'PyComputeClient: Error: Unable to connect to PyComputeServer.'
            exit(1)
    
        print 'PyComputeClient: Connected to PyComputeServer. ' + self.server_address[0] + \
                ':' + str(self.server_address[1])
                
        #Download PyComputeClientProcessRemote.py
        message = (PyComputeMsg.CLIENT_REQUEST_CODE, None)
        self.conn.send(message)
        
        message_type, message_content = self.conn.recv()
        if message_type != PyComputeMsg.SERVER_SEND_CODE:
            print 'PyComputeClient: Error: PyComputeServer did not send code.'
            exit(1)

        #Write the code that we just received to file
        open("PyComputeClientProcessRemote.py", "wb").write(message_content)
        print "PyComputeClient: Received 'PyComputeClientProcessRemote.py'."
    
    #Instantiate our client processes and kick them off
    def initProcesses(self):
        for i in range(self.max_processes):
            #print 'PyComputeClient: Process ' + str(self.last_process) + ' started.' 
            self.processes[i] = Process(target=NewChildProcess, args=(
                    self.task_queue, self.response_queue, self.last_process))
            self.processes[i].start()
            self.last_process += 1
    
    def requestTasks(self):
        if self.reseting == True:
            return
        
        message = (PyComputeMsg.CLIENT_REQUEST_TASKS, self.task_max - self.tasks_pending)
        self.conn.send(message)

        message_type, message_content = self.conn.recv()
        
        if message_type == PyComputeMsg.SERVER_TASKS_ASSIGNED:
            for task in message_content:
                self.tasks_pending += 1
                task_var = (PyComputeMsg.PROCESS_TASK, task) 
                self.task_queue.put(task_var)
                self.total_tasks_completed += 1
                self.tasks_completed_since_last += 1
        elif message_type == PyComputeMsg.SERVER_NO_TASKS:
            #No tasks, so wait for a bit
            sleep(self.no_task_retry_period)
        elif message_type == PyComputeMsg.SERVER_RESET_CLIENT:
            self.terminateProcesses()
        else:
            print 'PyComputeClient: Error: Server message not recognized.'
        
    def processResponses(self):
        try:
            while True:
                message_type, message_content = self.response_queue.get(True, 
                                                self.response_queue_get_wait)
                if message_type == PyComputeMsg.PROCESS_TERMINATED:
                    if self.processes[message_content] != None:
                        del self.processes[message_content]
                        print "PyComputeClient: PyComputeClientProcess shutdown: " + str(message_content)
                elif message_type == PyComputeMsg.CLIENT_TASK_DONE:
                    self.tasks_pending -= 1
                    self.conn.send((message_type, message_content))
                else:                            
                    print "PyComputeClient: Error: Unrecognized client message. message='" + \
                        str(message_type) + "', content='" + str(message_content) + "'"
        except Exception:
            pass
    
    def terminateProcesses(self):
        self.reseting = True
        for i in range(len(self.processes)):
            message = (PyComputeMsg.PROCESS_TERMINATE, None)
            self.task_queue.put(message)
    
    def run(self):
        running = True
        self.resets = 0
        report_connection_error = True 
        while running == True:
            connected_once = False
            
            try:
                self.last_process = 0
                self.task_queue = Queue()
                self.response_queue = Queue()
                self.tasks_pending = 0
                last_report = clock()
                
                #Connect to server
                self.connectToServer(report_connection_error)
                
                connected_once = True
                #Instantiate our client processes and kick them off
                self.initProcesses()
              
                #Processes messages until there are no more processes running
                while len(self.processes) > 0:
                    if clock() - last_report > 60:
                        last_report = clock()
                        print "PyComputeClient: Total Tasks Completed: " + \
                            str(self.total_tasks_completed) + ", Delta: " + \
                            str(self.tasks_completed_since_last) 
                        self.tasks_completed_since_last = 0
                        
                    if self.tasks_pending == 0:
                        #We have nothing to do, ask for tasks.
                        self.requestTasks()
                    else:
                        self.processResponses()
    
                        if self.tasks_pending < self.task_min:
                            self.requestTasks()
            except:
                pass
            
            if connected_once == True:
                self.conn.close()
                self.terminateProcesses()
                #At this point we have terminated every client process, restart everything
                self.resets += 1
                self.reseting = False
                report_connection_error = True
                print "PyComputeClient: Resets so far: " + str(self.resets)
            else:
                report_connection_error = False
                
            sleep(10)
            
def main():
    #Client mode
    max_processes = multiprocessing.cpu_count() * 2
    server_address = ("127.0.0.1", 6666)
    password = 'password'
    
    print "PyComputeClient by Hesam Rabeti v0.01b"
    print "Starting on " + strftime("%d %b %Y %H:%M:%S", localtime())
    print "--------------------------------"

    client = PyComputeClient(server_address, password, max_processes)
    
    client.run()

if __name__ == '__main__':
    main()
    
