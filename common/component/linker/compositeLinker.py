class CompositeLinker:
    def __init__(self, entity_linker, relation_liner):
        self.entity_linker = entity_linker
        self.relation_liner = relation_liner

    def link_entities(self, question, chunks=None):
        return self.entity_linker.link_entities(question, chunks)

    def link_relations(self, question, chunks=None):
        return self.relation_liner.link_relations(question, chunks)

    def link_entities_relations(self, question, chunks=None):
        return {"relations": self.link_relations(question, chunks),
                "entities": self.link_entities(question, chunks)}
