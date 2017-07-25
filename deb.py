import os
import xml.etree.ElementTree as ET
from copy import deepcopy
from sys import argv

from lxml import etree
from lxml import objectify

from db import Handler as mydb

script, _file = argv


xmltodict = {
    "accepts": [],
    "provides": [],
    "capabilities": [],
}

root = ET.parse(_file).getroot()

for k, v in root.attrib.items():
    if "type" in k:
        xmltodict['properties'] = {'type': [v[v.rfind(":"):][1:], "True"]}
    elif k == "uri":
        uri, cible = os.path.split(v[v.rfind("!"):][1:])
        ancestor, parent = os.path.split(uri)
        if not ancestor:
            # MongoDB ancestor field will not work if
            # ancestor = ['']
            ancestor = []
        else:
            ancestor = ancestor.split(os.sep)
        if "nodes" in ancestor:
            ancestor.remove("nodes")
        xmltodict['cible'] = cible
        xmltodict['parent'] = parent
        xmltodict['path'] = uri+"/"+cible
        xmltodict['ancestor'] = ancestor

for childrens in root:
    if "properties" in childrens.tag:
        ind = ''
        for subchildrens in childrens:
            for k, v in sorted(subchildrens.items()):
                _ = ''
                # Création d'une variable temporaire _ pour stocker la valeur de readonly
                # le dictionnaire pouvant ne pas être dans l'ordre
                if k in ['readonly', 'readOnly']:
                    _ = v
                    if ind != '':
                        if len(xmltodict['properties'][ind]) < 2:
                            xmltodict['properties'][ind].append(_)
                if k == "uri":
                    ind = v[v.rfind("#"):][1:]
                    if not _:
                        _ = "False"
                    xmltodict['properties'][ind] = [subchildrens.text, _]

# Plus de doublon dans readonly, check si meilleure manière de faire

print("Dictionary",xmltodict)

# xmlFileName = _file
# schemaFileName = "schema.xsd"
# schemaDoc = etree.parse(schemaFileName)
# schema = etree.XMLSchema(schemaDoc)
# xmlDoc = etree.parse(xmlFileName)
# if schema.validate(xmlDoc):
#     print ("Valid")
# else:
#     print (schema.error_log)


f = "XML/schema.xsd"
schema = etree.XMLSchema(file=f)
parser = objectify.makeparser(schema = schema)
a = objectify.parse(_file)
if schema.validate(a):
    print ("OK")
else:
    print (schema.error_log)


path = '/book/html/wa/foo/bar/'
print(path[path.find('wa'):])

# #
# # print("-"*100)
# #
# print("2",xmltodict['path'])
# #
print("1","-"*100)
#
# print("cible ", xmltodict['cible'])
#
# #print(Vospace().getNode("myresult1/testdecreation"))
# # print(Vospace().createNode(xmltodict))
# path, target = os.path.split(xmltodict['path'])
# _, _parent = os.path.split(path)
# if not _:
#     _ancestor = []
# else:
#     _ancestor = _.split(os.sep)
# if "nodes" in _ancestor:
#     _ancestor.remove("nodes")
# if _parent == "nodes":
#     parent = ''
# node = {
#     'children': [],
#     'properties': {},
#     'accepts': {},
#     'provides': {},
#     'busy': '',
# }
# meta = mydb().getNode(xmltodict['cible'], parent, ancestor)
# node['busy'] = meta['busy']
# node['path'] = deepcopy(meta['path'])
# node['properties'] = deepcopy(meta['properties'])
# node['accepts'] = deepcopy(meta['accepts'])
# node['provides'] = deepcopy(meta['provides'])
# ancestor.append(parent)
# print(target)
# print(ancestor)
# cursor = mydb().getChildrenNode(target, ancestor)
# for items in cursor:
#     node['children'].append(items)
#
# print("node")
# pprint.pprint(node)

#
#
# print(target,parent,ancestor)
# try:
#     readOnly = mydb().getNode(target, parent, ancestor)
#     if readOnly:
#         #properties
#         validator = {}
#         for keys, values in readOnly['properties'].items():
#             for k, v in values.items():
#                 validator[k] = v
#         newProp = set(xmltodict['properties'])
#         oldProp = set(validator)
#         propDict = mydb().getPropertiesDict()
#         print(newProp.intersection(oldProp))
#         for key in newProp.intersection(oldProp):
#             propDict[key] = deepcopy(xmltodict['properties'][key])
#             if readOnly['properties'][key]['readonly'] not in ["true", "True"]:
#                 print(key, propDict[key])
# except Exception as e:
#     print(e)
# print("children")
# print(node['children'])
print("2","-"*100)
#
# path, target = os.path.split(xmltodict['path'])
# _, parent = os.path.split(path)
# if not _:
#    ancestor = []
# else:
#    ancestor = _.split(os.sep)
# if "nodes" in ancestor:
#     ancestor.remove("nodes")
# if parent == "nodes":
#     parent = ''
#
# print(xmltodict['cible'])
# print(xmltodict['parent'])
# print("ancestor", ancestor)
#
# coll = mydb().connexion()
# curseur = coll.find({
#             'node': target,
#             'parent': parent,
#             'ancestor' : ancestor
#         }, {"_id": 0})
# temp = {}
# for document in curseur:
#     for keys, values in document.items():
#         temp[keys] = values
#
# print(temp)
# print("-"*100)




#
# c = mydb().getChildrenNode(xmltodict['cible'], ancestor)
# for item in c:
#     pprint.pprint(item)

