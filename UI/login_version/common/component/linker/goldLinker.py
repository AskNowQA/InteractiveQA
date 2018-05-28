from common.container.linkeditem import LinkedItem
from common.utility.utils import Utils


class GoldLinker:
    def __init__(self):
        pass

    def do(self, qapair, force_gold=False, top=5):
        entities = []
        relations = []
        for u in qapair.sparql.uris:
            if not (u.is_entity() or u.is_ontology()):
                continue
            question = qapair.question.text
            mentions = Utils.find_mentions(question, [u])
            surface = ""
            if len(mentions) > 0:
                surface = question[mentions[0]["start"]:mentions[0]["end"]]

            linked_item = LinkedItem(surface, [u])
            if u.is_entity():
                entities.append(linked_item)
            if u.is_ontology():
                relations.append(linked_item)

        return entities, relations
