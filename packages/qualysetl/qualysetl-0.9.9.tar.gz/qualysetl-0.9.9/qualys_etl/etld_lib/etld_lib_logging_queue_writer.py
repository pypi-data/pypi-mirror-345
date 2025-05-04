#!/usr/bin/env python3
import multiprocessing
import sys
import tempfile
import os
import time
import signal
from pathlib import Path
import traceback

class QueueWriter:
    def __init__(self, queue):
        self.queue = queue

    def write(self, message):
        if message != '\n':
            self.queue.put(message)

    def flush(self):
        self.queue.put('FLUSH')

def listener(queue, log_file_path):
    with open(log_file_path, 'a', newline='', encoding='utf-8') as log_file:
        while True:
            message = queue.get()
            if message == 'STOP':
                break
            if message == 'FLUSH':
                log_file.flush()
            elif message.startswith('SIGNAL:'):
                sys.stderr.write(f"{message}\n")
                sys.stderr.flush()
            else:
                log_file.write(message)
                log_file.flush()

def signal_handler(signum, frame, queue):
    # Convert the signal number to a human-readable string, e.g., 'SIGINT'
    signal_name = signal.Signals(signum).name
    queue.put(f'SIGNAL: Received {signal_name}')

def setup_signal_handlers(queue):
    # Register the signal handler for SIGINT and SIGTERM
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: signal_handler(signum, frame, queue))


def main():
    log_queue = multiprocessing.Queue()
    with tempfile.NamedTemporaryFile(delete=False) as temp_log_file:
        log_file_path = temp_log_file.name

    print(f"LOGFILE: {log_file_path}")
    listener_proc = multiprocessing.Process(target=listener, args=(log_queue, log_file_path))
    listener_proc.start()

    setup_signal_handlers(log_queue)
    sys.stdout = QueueWriter(log_queue)
    sys.stderr = QueueWriter(log_queue)

    try:
        while True:
            user_input = input("Enter something (or Ctrl+C to exit): ") + "\n"
            print(f"LOGGING: {user_input}")
    except KeyboardInterrupt:
        print("Caught a KeyboardInterrupt, performing cleanup...", file=sys.__stderr__)
    except Exception as e:
        print(f"Caught Exception {e}...", file=sys.__stderr__)
        traceback.print_exc(file=sys.__stderr__)
    finally:
        print("Performing cleanup...", file=sys.__stderr__)
        log_queue.put('STOP')
        listener_proc.join()
        exit


if __name__ == "__main__":
    main()