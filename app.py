from flask import Flask, render_template, request, session
from db.utils import filmGraph
import json

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
graphdb = filmGraph()

@app.route("/")
def index():
    return render_template('connexion.html')

@app.route("/home", methods=['GET','POST'])
def home():
    if request.method == 'POST':
        session['firstname'] = request.form['firstname']
        session['lastname'] = request.form['lastname']
        user = renderuser()
        if not graphdb.isExisting(user):
            user['id'] = (user['firstname']+user['lastname']).replace(' ','')
            graphdb.createUser(user)

        session['iduser'] = graphdb.getUserId(user)
    
    if "genres" in request.args:
        graphdb.addFavoriteTypes(session['iduser'], json.loads(request.args['genres']))

    user = renderuser()
    genres = graphdb.getFavoriteTypes(session['iduser'])
    films = graphdb.getFilms(genres)
    return render_template("home.html",user=user, films=films)

@app.route('/select')
def select():
    user = renderuser()

    typesSelected = [g.split("/")[-1] for g in graphdb.getFavoriteTypes(session['iduser'])]
    genres = graphdb.getGenres()
    for genre in genres :
        if genre['uri'] in typesSelected:
            genre['selected'] = True
        else :
            genre['selected'] = False
    

    return render_template("select.html",user=user, genres=genres)

@app.route('/more')
def more():
    if "film" in request.args:
        film = graphdb.getMoreInformations(request.args['film'])
        return render_template('filmInformations.html',film=film)

    return 'error', 404

def renderuser():
    return {
        'firstname': session['firstname'] if 'firstname' in session else 'John',
        'lastname': session['lastname'] if 'lastname' in session else 'Doe'
    }
    

if __name__=='__main__':
    app.run(debug=True)