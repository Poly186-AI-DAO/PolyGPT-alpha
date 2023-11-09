import asyncio
import inspect
# Import PolyLogger instead of logging
from poly_logger import PolyLogger

# Create a logger instance from PolyLogger
logger = PolyLogger(__name__)

class PolyObservable:

    def __init__(self):
        self._observers = {}
        self._async_observers = {}
        self._done_observers = set()

    def add_observer(self, observer, event='default'):
        # Use logger instance to log messages
        if event not in self._observers:
            self._observers[event] = []
            self._async_observers[event] = []

        if inspect.iscoroutinefunction(observer) or inspect.isasyncgenfunction(observer):
            if observer not in self._async_observers[event]:
                self._async_observers[event].append(observer)
                logger.info(f"Async observer {observer} added for event '{event}'")
        else:
            if observer not in self._observers[event]:
                self._observers[event].append(observer)
                logger.info(f"Observer {observer} added for event '{event}'")

        logger.info(f"Finished adding observer {observer} for event '{event}'")

    def remove_observer(self, observer, event='default'):
        # Use logger instance to log messages
        try:
            if observer in self._observers[event]:
                self._observers[event].remove(observer)
                logger.info(f"Observer {observer} removed from event '{event}'")
            elif observer in self._async_observers[event]:
                self._async_observers[event].remove(observer)
                logger.info(f"Async observer {observer} removed from event '{event}'")

            if observer in self._done_observers:
                self._done_observers.remove(observer)
        except (ValueError, KeyError) as e:
            logger.warning(f"Error removing observer {observer} for event '{event}': {e}")

    async def notify_observers_async(self, event='default', data=None):
        # Use logger instance to log messages
        for observer in self._observers.get(event, []):
            if observer in self._done_observers:
                continue
            try:
                observer(event, data)
            except Exception as e:
                logger.error(f"Error notifying observer {observer} for event '{event}': {e}")

        # Notify asynchronous observers concurrently
        await self._notify_async_observers(event, data)

    async def _notify_async_observers(self, event, data):
        tasks = [self._run_async_observer(observer, event, data)
                 for observer in self._async_observers.get(event, [])]
        await asyncio.gather(*tasks)

    async def _run_async_observer(self, observer, event, data):
        # Use logger instance to log messages
        if observer in self._done_observers:
            return
        try:
            if inspect.iscoroutinefunction(observer):
                await observer(event, data)
            elif inspect.isasyncgenfunction(observer):
                async_gen = observer(event, data)
                try:
                    next_item = await async_gen.asend(None)
                    if next_item is not None:
                        logger.info(f"Received {next_item} from observer {observer} for event '{event}'")
                except StopAsyncIteration:
                    self._done_observers.add(observer)
        except Exception as e:
            logger.error(f"Error notifying async observer {observer} for event '{event}': {e}")
