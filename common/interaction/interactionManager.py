from common.interaction.interactionOptions import InteractionOptions


class InteractionManager:
    def __init__(self, pipeline_results, kb, target_query=None, sparql_parser=None, interaction_type=None,
                 strategy=None):
        self.target_query = target_query
        self.pipeline_results = pipeline_results
        self.kb = kb
        self.strategy = strategy
        self.w = 1
        self.interaction_options = InteractionOptions(self.pipeline_results, kb.parse_uri, sparql_parser, kb,
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
        else:
            io = None
        self.last_option = io

        query = self.interaction_options.query_with_max_probability(io)
        if query is not None:
            query = query.query
            if self.last_option is None:
                self.last_option = 'query'
        return io, query

    def interact(self, answer, last_option=None):
        if last_option is None:
            last_option = self.last_option

        if isinstance(last_option, str) and last_option == 'query':
            # TODO: do some bookkeeping
            return False
        else:
            if last_option.type == 'query' and answer:
                return False

            if answer is not None and last_option.type == 'linked':
                # in case the current IO is linked and there are other IOs in the same label,
                # we look into the benchmark to see which of is used to construct the target query
                uri = last_option.value.uris[0].uri
                similar_ios = [io for io in self.interaction_options.ios_of_same_group(last_option) if
                               io.type == 'linked' and uri[uri.rindex('/'):] == io.value.uris[0].uri[
                                                                                io.value.uris[0].uri.rindex('/'):]]
                if self.target_query is not None and uri not in self.target_query.sparql.query:
                    if len(similar_ios) > 0:
                        for io in similar_ios:
                            if io.value.uris[0].uri in self.target_query.sparql.query:
                                last_option = io
                                similar_ios = [io for io in self.interaction_options.ios_of_same_group(last_option)
                                               if io.type == 'linked' and uri[uri.rindex('/'):] == io.value.uris[0].uri[
                                                                                                   io.value.uris[
                                                                                                       0].uri.rindex(
                                                                                                       '/'):]]
                                break
                # remove the IOs with same label, if they their URI isn't used by other IO's
                for io in similar_ios:
                    if io != last_option and io.value.uris[0].uri != last_option.value.uris[0].uri:
                        other_ios = self.interaction_options.get_ios_by_uri(uri)
                        if len(set([g_id for g_id, tio in other_ios])) == 1:
                            self.interaction_options.update(io, False)
            self.interaction_options.update(last_option, answer)
            self.last_option = last_option
            return True
