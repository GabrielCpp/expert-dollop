class FlowRunner:
    def __init__(self):
        self.steps = []

    def step(self, func: callable):
        self.steps.append(func)
        return self

    def extend(self, runner: "FlowRunner"):
        self.steps.extend(runner.steps)

    async def run(self, *args):
        params = args

        for step in self.steps:
            new_params = await step(*params)

            if isinstance(new_params, tuple):
                params = new_params
            else:
                params = []
