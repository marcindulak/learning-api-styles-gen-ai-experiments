"""
GraphQL schema.
"""
import graphene


class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info):
        return 'Hello, World!'


schema = graphene.Schema(query=Query)
