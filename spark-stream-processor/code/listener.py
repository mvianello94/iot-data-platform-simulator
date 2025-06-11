import logging

from pyspark.sql.streaming import StreamingQueryListener

logger = logging.getLogger("IoTStreamProcessor")


class StreamingListener(StreamingQueryListener):
    def onQueryStarted(self, event):
        logger.debug(f"Query started: {event.id}")

    def onQueryProgress(self, event):
        logger.debug(f"Query made progress: {event.progress.json}")

    def onQueryTerminated(self, event):
        logger.debug(
            f"Query {event.id} ended. Reason: {event.exceptionMessage or 'Normal termination.'}"
        )
