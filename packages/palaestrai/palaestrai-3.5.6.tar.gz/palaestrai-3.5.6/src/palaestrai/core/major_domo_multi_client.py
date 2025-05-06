import asyncio
from . import MajorDomoClient


async def send_and_wait(client: MajorDomoClient, service, request):
    return [service, await client.send(service, request)]


class MajorDomoMultiClient:
    def __init__(self, services: int, broker_uri: str):
        self.broker_uri = broker_uri
        self.client = MajorDomoClient(broker_uri)
        self.clients = [MajorDomoClient(broker_uri) for _ in range(services)]

    async def send_async(self, service_requests: dict):
        assert len(self.clients) >= len(
            service_requests
        ), "got too many services for number of clients"
        messages = [
            send_and_wait(self.clients[idx], service, request)
            for idx, (service, request) in enumerate(service_requests)
        ]
        return dict(await asyncio.gather(*messages))

    async def send(self, service, request):
        return await self.client.send(service, request)
