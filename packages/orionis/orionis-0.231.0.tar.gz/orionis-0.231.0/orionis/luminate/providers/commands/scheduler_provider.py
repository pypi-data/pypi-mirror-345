from orionis.luminate.contracts.services.commands.schedule_service import IScheduleService
from orionis.luminate.providers.service_provider import ServiceProvider
from orionis.luminate.services.commands.scheduler_service import ScheduleService

class ScheduleServiceProvider(ServiceProvider):

    def register(self) -> None:
        """
        Registers services or bindings into the given container.
        """
        self.app.scoped(IScheduleService, ScheduleService)
