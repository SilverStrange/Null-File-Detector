from functools import partial
from multiprocessing import Process
import multiprocessing as mp
import sys
import os


def read_in_chunks(file_object, chunk_size=4 * 1024 * 1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def do_work(in_queue, out_queue, null_char):

    while True:
        null = 0
        item = in_queue.get()
        # process
        for byte in item:
            if byte == null_char:
                null = null + 1
        out_queue.put(null)
        in_queue.task_done()


def scan(name, work_queue, result_queue):

    # produce data
    with open(name, 'rb') as f:
        for i in read_in_chunks(f):
            work_queue.put(i)

    work_queue.join()

    # get the results
    null_count = sum([result_queue.get()
                      for i in range(result_queue.qsize())])

    return null_count


def create_workers(work_queue, result_queue, null_char=b'\x00'):

    num_workers = mp.cpu_count()

    # start workers
    worker_list = []
    for i in range(num_workers):
        t = Process(target=do_work, args=(work_queue, result_queue, null_char))
        worker_list.append(t)
        t.daemon = True
        t.start()

    return worker_list

def scan_target(path, files, directories):

    if not os.path.isdir(path):
        files.append(path)
        return files, directories

    for entry in os.listdir(path):
        if os.path.isdir(entry):
            directories.append(entry)
        else:
            files.append(entry)

    return files, directories
