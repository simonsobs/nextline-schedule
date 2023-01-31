__all__ = ['Query', 'Mutation', 'Subscription']
import strawberry

from .mutation import Mutation
from .query import Query


@strawberry.type
class Subscription:
    pass
