from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


N = 20
K = 10
NPROD = 3
NCONS = 1

def delay(factor = 3):
    sleep(random()/factor)


def add_data(storage_prod, index, data, mutex): #add data to storage_prod
    mutex.acquire()
    try:
        storage_prod[index.value] = data
        delay(6)
        index.value = index.value + 1
    finally:
        mutex.release()


def get_data(storage_prod, index, mutex): #get data from storage_prod
    mutex.acquire()
    try:
        data = storage_prod[0]
        index.value = index.value - 1
        delay()
        for i in range(index.value):
            storage_prod[i] = storage_prod[i + 1]   #overwrites the old storage
        if storage_prod[index.value] != -1:
            storage_prod[index.value] = -1
    finally:
        mutex.release()
    return data


def get_min(storage_prod):  #find the minimum of the values from the different producers
    value = []
    ind_lst = []
    for i in range(NPROD):
        if storage_prod[i][0] > 0:
            value.append(storage_prod[i][0])
            ind_lst.append(i)
    v_min = min(value)
    v_ind = value.index(v_min)
    ind = ind_lst[v_ind]
    return v_min,ind


def is_there_prodcucers(storage_prod):  #checks if there is still positive values left in storage_prod
    for i in range(NPROD):
        if storage_prod[i][0] != -1:
            return True
    return False


def producer(storage_prod, index, empty, non_empty, mutex): #the producer with producing, adding and storing data
    data = 1
    for i in range(N):
        print (f"producer {current_process().name} producing")
        delay(6)
        empty.acquire()
        data += randint(1,10)
        add_data(storage_prod, index, data, mutex)  #adding random number that are increasing
        non_empty.release()
        print (f"producer {current_process().name} storing {i}")
    empty.acquire()
    add_data(storage_prod, index, -1, mutex)     #the last postion -1 to know when to stop
    non_empty.release()


def consumer(storage_prod, storage_cons, index, empty, non_empty, mutex):
    for i in range(NPROD):  #wait so all producers have produced something
        non_empty[i].acquire()

    a = 0
    while is_there_prodcucers(storage_prod) == True:
        print (f"consumer {current_process().name} destoring")
        value, ind = get_min(storage_prod)
        dato = get_data(storage_prod[ind], index[ind], mutex[ind])
        storage_cons[a] = value #add the new increasing value to the final array
        a += 1
        empty[ind].release()
        print (f"consumer {current_process().name} consuming {dato}")
        delay()
    print('Final: ',storage_cons[:]) #when there is no more values in the storage, we print the list


def main():
    storage_prod = [Array('i', K) for i in range(NPROD)]
    storage_cons = Array('i', NPROD*N)
    index = [Value('i', 0) for i in range(NPROD)]

    for i in range(NPROD):
        for ii in range(K):
            storage_prod[i][ii] = -1
        print("Storage inicial", storage_prod[i][:], "index", index[i].value)

    non_empty = [Semaphore(0) for i in range(NPROD)]
    empty = [BoundedSemaphore(K) for i in range(NPROD)]
    mutex = [Lock() for i in range(NPROD)]

    prodlst = [Process(target=producer,
                       name=f'prod_{i}',
                       args=(storage_prod[i], index[i], empty[i], non_empty[i], mutex[i]))
               for i in range(NPROD)]

    conslst = [Process(target=consumer,
                       name=f"cons_{i}",
                       args=(storage_prod, storage_cons, index, empty, non_empty, mutex))
               for i in range(NCONS)]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()


if __name__ == '__main__':
    main()















