from time import sleep, clock

import PyComputeServer

if __name__ == "__main__":
    
    start = clock()
    server = PyComputeServer.PyComputeServer()
    server.printMessages()
    
    print "Waiting 10 seconds so you can connect the clients..."
    
    while clock() - start > 10:
        server.printMessages()
    
    server.addTask(("print", "This is a very simple task. The client simply prints this string"))
    server.addTask(("print", "This is the second string"))
    server.addTask(("print", "This is the third string"))
    server.addTask(("print", "This is the fourth string"))
    
    #Lets wait for all clients to print.
    server.finish()
    
    print "All print tasks were finished."
    while server.printMessages():
        pass
    
    server.addTask(("add", (200,400)))
    server.addTask(("add", (20,40)))
    server.addTask(("add", (2,4)))
    server.addTask(("mult", (12,6)))
    
    server.finish()

    print "All arithmatic tasks were finished."
    while server.printMessages():
        pass
    
    raw_input("Press any key to exit...")