from verse.core import Component


class CLI(Component):
    component: Component

    def __init__(self, component: Component, **kwargs):
        self.component = component
        super().__init__(**kwargs)
