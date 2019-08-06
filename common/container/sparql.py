class SPARQL:
    def __init__(self, raw_query, parser):
        self.raw_query = raw_query
        self.query, self.supported, self.uris = parser(raw_query)
        self.where_clause, self.where_clause_template = self.__extrat_where()

    def __extrat_where(self):
        WHERE = "WHERE" if "WHERE" in self.query else "where"
        sparql_query = self.query.strip(" {};\t")
        where_idx = sparql_query.find(WHERE)
        last_bracket_idx = sparql_query.rfind('}')
        if last_bracket_idx == -1:
            last_bracket_idx = len(sparql_query)
        where_clause_raw = sparql_query[where_idx + len(WHERE):last_bracket_idx].strip(" {}")
        where_clause_raw = [item.strip(" .") for item in where_clause_raw.split(" ")]
        where_clause_raw = [item for item in where_clause_raw if item != ""]
        buffer = []
        where_clause = []
        for item in where_clause_raw:
            buffer.append(item)
            if len(buffer) == 3:
                where_clause.append(buffer)
                buffer = []
        if len(buffer) > 0:
            where_clause.append(buffer)

        where_clause_template = " ".join([" ".join(item) for item in where_clause])
        for uri in set(self.uris):
            where_clause_template = where_clause_template.replace(uri.uri, uri.uri_type)

        return where_clause, where_clause_template

    def query_features(self):
        features = {"boolean": ["ask "],
                    "count": ["count("],
                    "filter": ["filter("],
                    "comparison": ["<= ", ">= ", " < ", " > "],
                    "sort": ["order by"],
                    "aggregate": ["max(", "min("]
                    }

        output = set()
        if self.where_clause_template.count(" ") > 3:
            output.add("compound")
        else:
            output.add("single")
        generic_uris = set()
        for uri in self.uris:
            if uri.is_generic():
                generic_uris.add(uri)
                if len(generic_uris) > 1:
                    output.add("multivar")
                    break
        if len(generic_uris) <= 1:
            output.add("singlevar")
        raw_query = self.raw_query.lower()
        for feature in features:
            for constraint in features[feature]:
                if constraint in raw_query:
                    output.add(feature)
        return output

    def equals(self, other, ignore_property_ontology_space=False, ignore_type=False):
        if isinstance(other, SPARQL):
            mapping = {}
            if (not ignore_type) and len(self.where_clause) != len(other.where_clause):
                return False
            if (("ask " in self.raw_query.lower()) != ("ask " in other.raw_query.lower())) or (
                    ("count(" in self.raw_query.lower()) != ("count(" in other.raw_query.lower())):
                return False
            total_match = 0
            for line in self.where_clause:
                found = False
                for other_line in other.where_clause:
                    match = 0
                    mapping_buffer = mapping.copy()
                    if len(line) == len(other_line):
                        for i in range(len(line)):
                            if line[i].startswith("?") and other_line[i].startswith("?"):
                                if line[i] not in mapping_buffer:
                                    mapping_buffer[line[i]] = other_line[i]
                                    match += 1
                                else:
                                    match += mapping_buffer[line[i]] == other_line[i]
                            elif line[i] == other_line[i]:
                                match += 1
                            elif ignore_property_ontology_space:
                                if '/' in line[i] and '/' in other_line[i]:
                                    match += line[i][line[i].rindex('/'):] == other_line[i][other_line[i].rindex('/'):]
                    if match == len(line):
                        found = True
                        total_match += 1
                        mapping = mapping_buffer
                        break
                if not ignore_type and not found:
                    return False
            if not ignore_type:
                return True
            return total_match * 1.0 / len(self.where_clause)
        else:
            return False

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return self.query.encode("ascii", "ignore")
