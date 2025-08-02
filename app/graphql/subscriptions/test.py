import strawberry


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def name(self) -> str:
        return "hard265"
