# Définir les classes dans le module dynamique
module_code = """
from typing import Any, List

class Executor:

    # Classes pour les objets injectés
    class Principal:
        def __init__(self, id: str, roles: List[str] = None, tenant_id: str = None, 
                    domain_id: str = None, subscription_status: str = None, **kwargs: Any):
            self.id = id
            self.roles = roles or []
            self.tenant_id = tenant_id
            self.domain_id = domain_id
            self.subscription_status = subscription_status
            self.extra = kwargs

        def has_role(self, role: str) -> bool:
            return role in self.roles if self.roles else False

    class Resource:
        def __init__(self, type: str, id: str, **kwargs: Any):
            self.type = type
            self.id = id
            self.extra = kwargs

        def is_type(self, resource_type: str) -> bool:
            return self.type == resource_type

    class Context:
        def __init__(self, context_type: str = None, context_id: str = None, **kwargs: Any):
            self.context_type = context_type
            self.context_id = context_id
            self.extra = kwargs
            
    def __init__(
        self,
        principal: Principal,
        resource: Resource,
        context: Context
    ):
        self.principal = principal
        self.resource = resource
        self.context = context

    def __call__(self):
        return self.rule(self.principal, self.resource, self.context)



"""