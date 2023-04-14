from rdflib import Graph

class filmGraph():
    
    def __init__(self) -> None:
        self.graph = Graph()
        self.graph.parse('appFilm/db/data.ttl')
        self.graph.close()

    def getFilm(self) -> object:
        request = """
            PREFIX : <http://bda/tp2/paulmulard/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?title ?description ?genre ?copyright
            WHERE { 
                ?film a :Film . 
                ?film rdfs:label ?title .
            OPTIONAL {
                ?film rdfs:comment ?description
            }
            OPTIONAL {
                ?film :isOfType ?genre
            }
            OPTIONAL {
                ?film :baseCopyRight ?copyright
            }}"""
        
        return self.graph.query(request)

g = filmGraph()
print([f for f in g.getFilm()])