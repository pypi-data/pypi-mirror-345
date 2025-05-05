from ._component import Component


class MiddlewareComponent(Component):
    component: Component

    def __init__(
        self,
        component: Component | None = None,
        **kwargs,
    ):
        if component:
            self.component = component
        super().__init__(**kwargs)
