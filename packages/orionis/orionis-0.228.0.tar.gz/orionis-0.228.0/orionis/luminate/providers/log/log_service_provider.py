from orionis.luminate.contracts.services.config.config_service import IConfigService
from orionis.luminate.contracts.services.log.log_service import ILogguerService
from orionis.luminate.providers.service_provider import ServiceProvider
from orionis.luminate.services.config.config_service import ConfigService
from orionis.luminate.services.log.log_service import LogguerService

class LogServiceProvider(ServiceProvider):

    def register(self) -> None:
        """
        Registers services or bindings into the given container.
        """
        if not self.app.bound(IConfigService):
            self.app.scoped(IConfigService, ConfigService)

        self.app.singleton(ILogguerService, LogguerService)

    async def boot(self) -> None:
        """
        Boot the service provider.

        This method is intended to be overridden by subclasses to perform
        any necessary bootstrapping or initialization tasks.
        """
        await self.app.make(ILogguerService)