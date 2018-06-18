from common.interaction.interactionOptions import InteractionOptions


class InteractionManager:
    def __init__(self, pipeline_results, kb, sparql_parser=None, interaction_type=None, strategy=None):
        self.pipeline_results = pipeline_results
        self.kb = kb
        self.strategy = strategy
        self.w = 1
        self.interaction_options = InteractionOptions(self.pipeline_results[2], kb.parse_uri, sparql_parser, kb,
                                                      *interaction_type)
        self.last_option = None

    def get_interaction_option(self):
        if self.interaction_options.has_interaction():
            if self.strategy == 'InformationGain':
                io = self.interaction_options.interaction_with_max_information_gain()
            elif self.strategy == 'OptionGain':
                io = self.interaction_options.interaction_with_max_option_gain(self.w)
            elif self.strategy == 'Probability':
                io = self.interaction_options.interaction_with_max_probability()
            self.last_option = io
            return io, self.interaction_options.query_with_max_probability().query
        return None, None

    def interact(self, answer):
        self.interaction_options.update(self.last_option, answer)
