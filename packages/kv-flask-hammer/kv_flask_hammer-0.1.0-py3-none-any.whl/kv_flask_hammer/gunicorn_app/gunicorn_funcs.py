import typing as t
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics


def child_exit(server, worker):
    # multiprocess.mark_process_dead(worker.pid)
    GunicornPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)


def get_when_ready_func(
    workers_count: int, metrics_enabled: bool, metrics_bind_ip: str, metrics_bind_port: str
) -> t.Callable:

    def when_ready(server):
        server.log.info(f"Gunicorn: Server is ready. Spawning {workers_count} workers")

        if not metrics_enabled:
            server.log.info(f"Gunicorn: Skipping Prometheus Metrics server as 'FLASK_HAMMER_METRICS_ENABLED' is False")
            return

        server.log.info(
            f"Gunicorn: Starting HTTP Prometheus Metrics server when ready on: {metrics_bind_ip}:{metrics_bind_port}"
        )
        GunicornPrometheusMetrics.start_http_server_when_ready(port=metrics_bind_port, host=metrics_bind_ip)

    return when_ready


def post_fork(server, worker):
    server.log.info("Gunicorn: Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("Gunicorn: Forked child, re-executing.")


def get_worker_int_func(callbacks: list[t.Callable]):
    def worker_int(worker):
        worker.log.info("Gunicorn: Worker received INT or QUIT signal")

        ## get traceback info
        import threading, sys, traceback

        id2name = {th.ident: th.name for th in threading.enumerate()}
        code = []
        for threadId, stack in sys._current_frames().items():
            code.append("\n# Thread: %s(%d)" % (id2name.get(threadId, ""), threadId))
            for filename, lineno, name, line in traceback.extract_stack(stack):
                code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
                if line:
                    code.append("  %s" % (line.strip()))
        worker.log.debug("\n".join(code))

        for cb in callbacks:
            cb()

    return worker_int


def get_worker_abort_func(callbacks: list[t.Callable]):
    def worker_abort(worker):
        worker.log.info("Gunicorn: Worker received SIGABRT signal")
        for cb in callbacks:
            cb()

    return worker_abort
