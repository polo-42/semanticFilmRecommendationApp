from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
import functools

class filmGraph():
    
    def __init__(self) -> None:
        self.graph = Graph()
        self.graph.parse('appFilm/db/data.ttl')
        self.graph.close()

        self.dbpedia = Graph("SPARQLStore")
        self.dbpedia.open("http://dbpedia.org/sparql")

        request = filmGraph.GETCATEGORIES
        result = self.dbpedia.query(request)
        self.genres = {
            genre['uri']: {
                'uri': genre['uri'].split("/")[-1], 
                'name': genre['label']
            } for genre in result 
        }

    def isExisting(self, user: dict) -> bool:
         request = filmGraph.GETUSER.format(user=user)

         user = self.graph.query(request)
         return True if (len(user) >= 1) else False
    
    def createUser(self, user: dict) -> None:
        request = filmGraph.CREATEUSER.format(user=user)

        self.graph.update(request)
        self.save()
    
    def save(self) -> None:
        self.graph.serialize(destination="db/data.ttl")
        self.graph = Graph()
        self.graph.parse('appFilm/db/data.ttl')
        self.graph.close()
    
    def getFilms(self, genres):
        films = []

        if len(genres) <= 1 :
            limit = 10
        elif len(genres) <= 3 :
            limit = 5
        else :
            limit = 2
        
        for genre in genres:
            request = filmGraph.GETFILMS.format(genre=genre,limit=limit)
            result = self.dbpedia.query(request)
            for film in result:
                films.append({
                    'uri': film['uri'],
                    'title': film['title'],
                    'description': film['description'],
                    'genre': self.genres[genre]['name']
                })
        return films

    def getGenres(self):
        return self.genres.values()
    
    def getMoreInformations(self, uriFilm):
        request = filmGraph.GETMOREINFORMATIONS.format(uriFilm=uriFilm)
        result = self.dbpedia.query(request)
        film = {}
        for f in result:
            film = {
                'title': f['name'],
                'description': f['description'],
                'directors': self.getMoreInformationsOnDirectors(uriFilm),
                'actors': self.getMoreInformationsOnActors(uriFilm)
            }
        return film

    def getMoreInformationsOnDirectors(self, uriFilm):
        request = filmGraph.GETDIRECTORS.format(uriFilm=uriFilm)
        result = self.dbpedia.query(request)
        directors = []
        for director in result :
            directors.append({
                'name': director['name']
            })
        return result

    def getMoreInformationsOnActors(self, uriFilm):
        request = filmGraph.GETACTORS.format(uriFilm=uriFilm)
        result = self.dbpedia.query(request)
        actors = []
        for actor in result :
            actors.append({
                'name': actor['name'] if 'name' in actor else actor['actor']
            })
        return result

    def getUserId(self, user):
        request = filmGraph.GETUSER.format(user=user)
        result = self.graph.query(request)
        
        return [u['uri'] for u in result][0]

    def addFavoriteTypes(self, userUri, genresUri):
        favoriteTypes = functools.reduce(
            lambda genre1, genre2: f'{genre1}, {genre2}',
            map(lambda genre : f'dbr:{genre}', genresUri)
        )

        self.removeFavoriteTypes(userUri)

        request = filmGraph.ADDTYPES.format(userUri=userUri,favoriteTypes=favoriteTypes)
        self.graph.update(request)
        self.save()
    
    def removeFavoriteTypes(self, userUri):
        request = filmGraph.DELETETYPES.format(userUri=userUri)
        self.graph.update(request)
        self.save()
    
    def getFavoriteTypes(self, userUri):
        request = filmGraph.GETTYPES.format(userUri=userUri)
        result = self.graph.query(request)
        return [g['genre'] for g in result]

    GETUSER = """
            PREFIX : <http://bda/tp2/paulmulard/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            SELECT DISTINCT ?uri 
            WHERE {{
                ?uri a :User;
                    foaf:firstName '{user[firstname]}';
                    foaf:lastName '{user[lastname]}' .
            }}"""
    
    CREATEUSER = """
            PREFIX : <http://bda/tp2/paulmulard/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            INSERT DATA {{ 

                :{user[id]} a :User;
                    foaf:firstName '{user[firstname]}';
                    foaf:lastName '{user[lastname]}' .
            }}
        """
    
    GETFILMS = """
        SELECT DISTINCT ?uri ?title ?description
        WHERE {{
            ?uri a dbo:Film; 
                rdfs:label ?title;
                dbo:abstract ?description;
                dbo:wikiPageWikiLink <{genre}> .
            FILTER (lang(?description) = 'fr')
            FILTER (lang(?title) = 'fr')
        }} 
        LIMIT {limit}
    """

    GETCATEGORIES = """
        SELECT DISTINCT ?uri ?label
        WHERE {{
            ?uri dct:subject dbc:Film_genres;
                rdfs:label ?label .
            FILTER (lang(?label) = 'fr')
        }}
    """
    GETMOREINFORMATIONS = """
        SELECT ?name ?description
        WHERE {{
            <{uriFilm}> dbo:abstract ?description;
                rdfs:label ?name .
            FILTER (lang(?description) = 'fr')
            FILTER (lang(?name) = 'fr')
        }}
    """

    GETDIRECTORS = """
        SELECT DISTINCT ?name
        WHERE {{
            <{uriFilm}> dbo:director/rdfs:label ?name .
            FILTER (lang(?name) = 'fr')
        }}
    """

    GETACTORS = """
        SELECT DISTINCT ?actor ?name
        WHERE {{
            <{uriFilm}> <http://dbpedia.org/property/starring> ?actor .
            OPTIONAL {{
                ?actor rdfs:label ?name .
                FILTER(lang(?name) = 'fr')
            }}
        }}
    """

    ADDTYPES = """
            PREFIX : <http://bda/tp2/paulmulard/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            INSERT DATA {{ 
                <{userUri}> :favoriteType {favoriteTypes} .
            }}
    """

    GETTYPES = """
            PREFIX : <http://bda/tp2/paulmulard/>
            SELECT ?genre
            WHERE {{
                <{userUri}> :favoriteType ?genre .
            }}
    """

    DELETETYPES = """
        PREFIX : <http://bda/tp2/paulmulard/>
        DELETE {{
            <{userUri}> :favoriteType ?genre .
        }}
        WHERE {{
            <{userUri}> :favoriteType ?genre .
        }}
    """