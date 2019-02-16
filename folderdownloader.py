from multiprocessing import Process, Queue, current_process
from EsuRestApi import EsuRestApi, EsuException
from os.path import exists 
from os import makedirs 
from time import sleep

pool = 24 
write_location= "/data"
errorlogfile= "./err.txt"
host, port, uid, secret = "0.0.0.0", 80, "", ""

#Something to write the logs
def logwriter(errorlogger):
    while True:
	if not errorlogger.empty():
	    error = errorlogger.get()
	    with open(errorlogfile,"a+") as errorfile:
		errorfile.write(str(errorlogger.get()))
		

def crawler(q,errorlogger):
    api = EsuRestApi(host, port, uid, secret)
    while True:
	def logexception(problematic_item,problem):
	    print problematic_item, problem
	    log = problematic_item + [problem]
	    errorlogger.put(log)

        if not q.empty():
            task = q.get()
            typeof , item_uid , path = task[0] , task[1], task[2]
            if typeof == "regular":
                #download the item
		uri = write_location+path
                print q.qsize(), current_process(), "Downloading ", path
                with open(uri, "w") as file:
		    try :
    		        file.write(api.read_object(item_uid))
		    except EsuException:
			logexception(task, ["EsuExp"])
			continue
            elif typeof == "directory":
                #explore the directory
                path = path + "/"
                print q.qsize(), current_process() , "exploring :", path
		
		
		folder = write_location  + path.rsplit('/', 1)[0] + "/"
		print folder

		if not exists(folder):
		    makedirs(folder)
		token = None
		# if more than 10000 files in the dir, a token is returned for pagination
		while True:
		    try:
		        reply = api.list_directory(path, token=token)
		        list_of_items, token = reply[0] , reply[1]
		    except EsuException:
		        logexception(task, ["EsuExp"])		    
		    
		    else:    
                        for item in list_of_items:
                            res_uid , res_name,  res_typeof = item[0] , item[2] ,  item[1]
                            fullpath = path + res_name 
                            q.put([res_typeof,res_uid,fullpath])
  		
		    if token == None:
		        break	
	    elif typeof == "bye":
		break
            else :
		# this should not happen
                msg = typeof + " is not a known type. "
		raise Exception(msg)
		continue


if __name__ == '__main__':
    q = Queue()
    err = Queue()
    ppool = dict()
    logger = Process(target=logwriter,args=(err,))
    logger.start()
    for process in range(pool):
        ppool[process] = Process(target=crawler, args=(q,err))
	ppool[process].daemon = True
        ppool[process].start()

# a point to start
    q.put(["directory","null",""])
    
# check if work is done
    end = 0 
    while True:
	sleep(15)
	print "check:", end, q.qsize()
	if q.qsize() < 1 :
	    end = end + 1 
	else:
	    end = 0
	if end > 3:
	    print "No more work!, stopping worker processes"
	    for process in range(pool):
		q.put(["bye","",""])
	    for process in range(pool):
		ppool[process].join()
	    break
	
    logger.terminate()

