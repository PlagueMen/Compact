#def numCPUs():
#    if not hasattr(os, "sysconf"):
#        raise RuntimeError("No sysconf detected.")
#    return os.sysconf("SC_NPROCESSORS_ONLN")
#workers = numCPUs() * 2 + 1
workers = 3
bind = "127.0.0.1:5000"
backlog = 2048
#worker_class = "sync"
worker_class = "gevent"
debug = True
#daemon = True
pidfile = "gunicorn.pid"
logfile = "gunicorn.log"
