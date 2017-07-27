import os
from datetime import datetime
from functools import wraps
from flask import Flask, request, Response, render_template, make_response
from flask_restplus import Api, Resource
import settings
from voparser import Parser
from vospace import Vospace

app = Flask(__name__)

api = Api(app, version='1.0', title='CDS VOSpace',
    description='Prototype de VOSpace')
app.config.SWAGGER_UI_LANGUAGES = ['en', 'fr']
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'


if app.debug is not True:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('templates/errors.html', maxBytes=1024 * 1024 * 100, backupCount=200)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("<br><br><table><tr><td><font color=\"red\">"
                                  " %(asctime)s- %(name)s - %(levelname)s - %(message)s</font><tr></table><br>")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

def check_auth(username, password):
    # Test account
    user = ['iyapici' , 'myresult1', 'taplib', 'm']
    mdp = ['cds', 'b']
    if username in user and password in mdp:
        return username and password
    # return username == 'iyapici' and password == 'cds'

def authenticate():
    # 401 return for identification
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

def er_log (path, message, data):
    _data = data.decode("utf-8")
    line_prepender("templates/errors.html",
        "<br><br><table><tr><td><font color=\"red\">" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')+
                   "  ERROR on " + path + " [PUT] </td><td> XML mal formé : "+ message +
                   "</font></td></tr></table><br><textarea rows=\"8\" cols=\"100\" style=\"border:none;\">" + _data +"</textarea><br>")

    return "500 xml mal formé data : "+ _data

# @app.route('/', methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
# def api_root():
#     if request.method == 'GET':
#         return "VOSpace"
#
#
# @app.route("/nodes", strict_slashes=False)
# def api_landing():
#     return make_response(render_template('nodes.html'), 200)


@api.route('/nodes/<path:path>', strict_slashes=False)
class MyResource(Resource):
    @requires_auth
    @api.response(200, "Représentation de la node")
    @api.response(404, "Node non trouvée")
    def get(self,path):
        _path, target = os.path.split(path)
        _, parent = os.path.split(_path)
        if _:
            ancestor = _.split(os.sep)
        else:
            ancestor = []
        node = Vospace().getNode(target, parent, ancestor)
        if node == False:
            return make_response(render_template("404.html"), 404)
        else:
            return Response(node, mimetype='text/xml')

    # @api.doc(params={'XML' : 'XML de modification de la node'})
    # @api.doc('Modifie les metadonnées d\'une node')
    # @api.response(200, "Node modifiée")
    # @api.response(404, "Node non trouvée")
    # @requires_auth
    # def post(self, path):
    #     xmltodict = Parser().xml_parser(request.data.decode("utf-8"))
    #     Vospace().setNode(xmltodict['cible'], xmltodict['parent'], xmltodict['ancestor'], xmltodict['properties'])
    #     node = Vospace().getNode(xmltodict['cible'], xmltodict['parent'], xmltodict['ancestor'])
    #     return Response(node, status=200, mimetype='text/xml')
    #
    @api.doc(params={'XML': 'XML de création de la node'})
    @api.doc('Création d\'une node')
    @api.response(201, "Représentation de la node créée")
    @api.response(500, "Erreur interne")
    @requires_auth
    def put(self, path):
        xmltodict = Parser().xml_parser(request.data.decode("utf-8"))
        if isinstance(xmltodict, dict):
            Vospace().createNode(xmltodict)
            node = Vospace().getNode(xmltodict['cible'], xmltodict['parent'], xmltodict['ancestor'])
            return Response(node, status=201, mimetype='text/xml')
        else:
            a = er_log(path=path, message=xmltodict, data=request.data)
            print("*")
            return Response(a, status=500)

    @api.doc("Suppréssion d'une node")
    @api.response(204, "Node deleted \n")
    @requires_auth
    def delete(self, path):
        return Response(Vospace().deleteNode("nodes/"+path), status=204, mimetype='text/xml')

@api.route('/nodes/<string:account>/', strict_slashes=False)
class MyAccount(Resource):
        @api.doc(params={'XML': 'XML de modification de la node'})
        @api.doc('Modifie les metadonnées d\'une node')
        @api.response(200, "Node modifiée")
        @api.response(404, "Node non trouvée")
        @requires_auth
        def post(self, account):
            xmltodict = Parser().xml_parser(request.data.decode("utf-8"))
            Vospace().setNode(xmltodict['cible'], xmltodict['parent'], xmltodict['ancestor'], xmltodict['properties'])
            node = Vospace().getNode(xmltodict['cible'], xmltodict['parent'], xmltodict['ancestor'])
            return Response(node, status=200, mimetype='text/xml')
        # @api.doc(params={'XML': 'XML de création de la node'})
        # @api.doc('Création d\'une node')
        # @api.response(201, "Représentation de la node créée")
        # @api.response(500, "Erreur interne")
        # @requires_auth
        # def put(self, account):
        #     xmltodict = Parser().xml_parser(request.data.decode("utf-8"))
        #     print("file : ", request.stream)
        #     print(xmltodict)
        #     Vospace().createNode(xmltodict)
        #     node = Vospace().getNode(xmltodict['cible'], xmltodict['parent'], xmltodict['ancestor'])
        #     return Response(node, status=201, mimetype='text/xml')



# @app.route("/nodes/iyapici",  strict_slashes=False, methods=['GET', 'POST', 'PUT'])
# @requires_auth
# def api_yapilanding():
#     if request.method == 'GET':
#         retour = Vospace().getNode("iyapici")
#         if retour:
#             return Response(retour, status=200, content_type='text/xml')
#         else:
#             return make_response(render_template('404.html'), 404)
#     if request.method == 'POST':
#         xmltodict = Parser().xml_parser(request.data.decode("utf-8"))
#         Vospace().setNode(xmltodict['path'] + "/" + xmltodict['cible'], xmltodict['properties'])
#         return Response(Vospace().getNode(xmltodict['cible'], xmltodict['parent'], xmltodict['ancestor']), content_type='text/xml')
#
#     if request.method == 'PUT':
#         xmltodict = Parser().xml_parser(request.data.decode("utf-8"))
#         Vospace().createNode(xmltodict)
#         return Response(Vospace().getNode(xmltodict['cible'], xmltodict['parent'], xmltodict['ancestor']), content_type='text/xml')


# @app.route("/nodes/iyapici/<path:varargs>", strict_slashes=False, methods=['GET', 'DELETE'])
# @requires_auth
# def api_yapici(varargs):
#     if request.method == 'GET':
#         retour = Vospace().getNode("iyapici/"+varargs)
#         if retour:
#             return Response(retour, status=200, content_type='text/xml')
#         else:
#             return make_response(render_template('404.html'), 404)
#
#     # if request.method == 'POST':
#     #     xmltodict = Parser().xml_parser(request.data.decode("utf-8"))
#     #     Vospace().setNode(xmltodict['path']+"/"+xmltodict['cible'], xmltodict['properties'])
#     #     return Response(Vospace().getNode(xmltodict['cible']), content_type='text/xml')
#     #
#     # if request.method == 'PUT':
#     #     xmltodict = Parser().xml_parser(request.data.decode("utf-8"))
#     #     Vospace().createNode(xmltodict)
#     #     return Response(Vospace().getNode(xmltodict['cible']), content_type='text/xml')
#
#     if request.method == 'DELETE':
#         Vospace().deleteNode("nodes/iyapici/"+varargs)
#         return Response(None, status=204, content_type='text/xml')



@api.route("/protocols", strict_slashes=False)
class Protocol(Resource):
    def get(self):
        body = Vospace().getVOSpaceSettings("protocols")
        if body:
            return Response(body, status='200', content_type='text/xml')
        else:
            make_response(render_template("404.html"), 404)


@api.route("/views", strict_slashes=False)
class _View(Resource):
    def get(self):
        body = Vospace().getVOSpaceSettings("views")
        if body:
            return Response(body, status='200', content_type='text/xml')
        else:
            make_response(render_template("404.html"), 404)


@api.route("/properties", strict_slashes=False)
class Properties(Resource):
    def get(self):
        body = Vospace().getVOSpaceSettings("properties")
        if body:
            return Response(body, status='200', content_type='text/xml')
        else:
            make_response(render_template("404.html"), 404)

@app.route("/errors", strict_slashes=False)
def api_error():
    return make_response(render_template("errors.html"))


if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=8080, debug=True)