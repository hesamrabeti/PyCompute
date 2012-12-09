'''
 PyComputeServer by Hesam Rabeti

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
from multiprocessing import Queue, AuthenticationError, connection, Process
import PyComputeMsg
import socket

def ListenForClients(port, password, message_queue, task_queue):
    listener = connection.Listener((socket.gethostbyname(socket.gethostname()), port), family='AF_INET', backlog=5, authkey=password)
    message_queue.put("PyComputeServer: Listener: Accepting connections on port " + str(port))
    while True:
        try:
            conn = listener.accept()
            address = listener.last_accepted
            message_queue.put("PyComputeServer: Listener: New connection from " + str(address))
            Process(target=HandleConnection, args=(conn, address, task_queue, message_queue)).start()
        except AuthenticationError:
            message_queue.put("PyComputeServer: Listener: New connection authorization attempt failed.")

def HandleConnection(conn, address, task_queue, message_queue):
    try:
        running = True
        tasks_pending = 0
        while running == True:
            message_type, message_content = conn.recv()

            if message_type == PyComputeMsg.CLIENT_SHUTDOWN:
                message_queue.put("PyComputeServer: Connection: Client Connection Shutdown. " + str(address))
                running = False
                
            elif message_type == PyComputeMsg.CLIENT_TASK_DONE:
                task_queue.task_done()
                tasks_pending -= 1
            elif message_type == PyComputeMsg.CLIENT_TASK_ERROR:
                message_queue.put("PyComputeServer: Warning: Task " + str(message_content) + " failed.")
                tasks_pending -= 1
                task_queue.task_done()
                
            elif message_type == PyComputeMsg.CLIENT_REQUEST_TASKS:
                tasks = []
                #Create a list of tasks
                try:
                    for i in range(message_content):
                        tasks.append(task_queue.get_nowait())
                except Exception:
                    pass
                
                #Send response
                out_message = None
                if len(tasks) == 0:
                    #If we don't have any tasks, respond with appropriate 
                    out_message = (PyComputeMsg.SERVER_NO_TASKS, None)
                else:
                    out_message = (PyComputeMsg.SERVER_TASKS_ASSIGNED, tasks)

                conn.send(out_message)
                tasks_pending += len(tasks)

            elif message_type == PyComputeMsg.CLIENT_REQUEST_CODE:
                process_file_content = open("PyComputeClientProcess.py").read()
                message = (PyComputeMsg.SERVER_SEND_CODE, process_file_content)
                conn.send(message)
            else:
                message_queue.put("PyComputeServer: Connection: Error: Unrecognized Message Type. " + str(address))
    except Exception as E:
        message_queue.put("PyComputeServer: Connection: Error: Client Connection Unexpectedly Shutdown. " + str(address))
        

class PyComputeServer:
    task_queue = multiprocessing.JoinableQueue()
    listener_process = None
    message_queue = Queue()
    client_connections = {}
    task_number = 0
    
    def __init__(self, password='password', port=6666):
        self.listener_process = Process(target=ListenForClients, args=(port, 
            password, self.message_queue, self.task_queue))
        self.listener_process.start()
        print "PyComputeServer by Hesam Rabeti"
        print "Starting on " + strftime("%d %b %Y %H:%M:%S", localtime())
        print "--------------------------------"    
        
    def printMessages(self):
        printed = False
        try:
            while True: 
                print self.message_queue.get_nowait()
                printed = True
        except:
            return printed       
        
    def addTask(self, task):
        self.task_queue.put((self.task_number, task))
        self.task_number += 1
        return self.task_number - 1 #HACCCKKKKK
    
    def countTasks(self):
        return self.task_queue.qsize()
    
    def finish(self):
        ''' Wait till we have finished all tasks '''
        self.task_queue.join()