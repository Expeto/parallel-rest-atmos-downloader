from multiprocessing import Process, Queue, current_process
from EsuRestApi import EsuRestApi, EsuException
from time import sleep

pool = 32
write_location = "/data/"
errorlogfile = "./err.txt"
host, port, uid, secret = "0.0.0.0", 80, "", ""
max_queue_length = 500
objects_list_file= "objects.csv"
# Something to write the logs


def logwriter(errorlogger):
    while True:
        if not errorlogger.empty():
            error = errorlogger.get()
            with open(errorlogfile, "a+") as errorfile:
                errorfile.write(str(errorlogger.get())+"\n")


def crawler(q, errorlogger):
    api = EsuRestApi(host, port, uid, secret)

    def logexception(problematic_item, problem):
        print problematic_item, problem
        log = problematic_item + str(problem)
        errorlogger.put(log)
    while 1:
        if not q.empty():
            task = str(q.get())
            if task == "bye":
                break
            

            task = task
            path = write_location+str(task)
            print q.qsize(), current_process(), "Downloading ", path
            try:
                data = api.read_object(task)
                with open(path, "w") as file:
                    file.write(data)

            except EsuException:
                logexception(task, ["EsuExc"])
                continue
            except:
                logexception(task, ["UnknownExc"])



if __name__ == '__main__':
    q = Queue()
    err = Queue()
    ppool = dict()
    logger = Process(target=logwriter, args=(err,))
    logger.start()
    for process in range(pool):
        ppool[process] = Process(target=crawler, args=(q, err))
        ppool[process].daemon = True
        ppool[process].start()


    with open(objects_list_file, "r") as ins:
        for line in ins:
            if q.qsize() < max_queue_length :
                q.put(line.strip())
            else:
                sleep(1)


    logger.terminate()
    
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


