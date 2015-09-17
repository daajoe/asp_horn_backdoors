# We use the signal handler for long running condor jobs to save
# output and stop the solver
def signal_handler(signal, frame):
    logging.warning('Received external Interrupt signal. Solvers will stop and save data')
    logging.warning('Exiting.')
    exit(0)

import signal
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
