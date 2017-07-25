# Classe traduisant les instructions en actions
import os
import shutil
import time
from copy import deepcopy

from XML.settings import fstodictionary
from db import Handler as mydb
from genericbackend import Backend
from parser import Parser as xml


class Vospace(Backend):


    # Get the service's protocols/views/properties list
    def getVOSpaceSettings(self, meta):
        retour = {}
        coll = mydb().connexion()
        curseur = coll.find({'name': 'vo'+meta})
        if curseur:
            for documents in curseur:
                for keys, values in documents.items():
                    if keys == "metadata":
                        for k, v in values.items():
                            retour[k] = v
        return xml().xml_generator(meta, retour)

    # Get the node data
    def getNode(self, target, parent, ancestor):
        # Return the node's representation
        node = {
            'children': [],
            'properties': {},
            'accepts': {},
            'provides': {},
            'busy': '',
        }
        try:
                meta = mydb().getNode(target, parent, ancestor)
                if meta == {}:
                    return False
                else:
                    node['busy'] = meta['busy']
                    node['path'] = deepcopy(meta['path'])
                    node['properties'] = deepcopy(meta['properties'])
                    node['accepts'] = deepcopy(meta['accepts'])
                    node['provides'] = deepcopy(meta['provides'])
                    # If the parent is not empty, it is added to
                    # the ancestor list to find the subnodes
                    if parent != '':
                        ancestor.append(parent)
                    cursor = mydb().getChildrenNode(target, ancestor)
                    for items in cursor:
                        node['children'].append(items)
                    return xml().xml_generator("get",node)
        except Exception as e:
            return e


    def createNode(self, dictionary):
        start_time = time.time()
        # Create node
        # _path, target = os.path.split(dictionary['path'])
        # _, parent = os.path.split(_path)
        if dictionary['ancestor'] == ['']:
            # MongoDB ancestor field will not work if
            # ancestor = ['']
            ancestor = []
        else:
            ancestor = dictionary['ancestor']
        if not mydb().getNode(dictionary['cible'], dictionary['parent'], ancestor):
            try:
                os.makedirs(dictionary['path'])
            except OSError as e:
                return 'Directory creation failed. Error %s' % e

            if os.path.exists(dictionary['path']):
                mydb().insertDB(fstodictionary(dictionary['path']))
                self.setNode(dictionary['cible'], dictionary['parent'], ancestor, dictionary['properties'])
                print("%s seconds" % (time.time() - start_time))

        else:
            return "FileExistsError"

    def setNode(self, target, parent, ancestor, properties):
        # _path, target = os.path.split(path)
        # _, parent = os.path.split(_path)
        if ancestor == ['']:
            # MongoDB ancestor field will not work if
            # ancestor = ['']
            ancestor = []
        readOnly = mydb().getNode(target, parent, ancestor)
        if readOnly:
            #properties
            validator = {}
            for keys, values in readOnly['properties'].items():
                for k, v in values.items():
                    validator[k] = v
            # newProp = set(properties)
            # oldProp = set(validator)
            propDict = mydb().getPropertiesDict()
            for key in set(properties).intersection(set(validator)):
                propDict[key] = deepcopy(properties[key])
                if readOnly['properties'][key]['readonly'] not in ["true", "True"]:
                    mydb().updateMeta(target, parent, ancestor, key, propDict[key])


    def copyNode(self, targetPath, locationPath):
        # Copy the node and the subnodes
        # self.loc = locationPath
        # temp = {}
        # try:
        #     cursor = mydb().getNode(targetPath)
        #     for items in cursor:
        #         for keys, values in items.items():
        #             temp[keys] = values
        # except:
        #     pass
        # try:
        #     shutil.copytree(targetPath, self.loc)
        #     if temp:
        #         temp['path'] = self.loc
        #         temp['node'] = os.path.basename(self.loc)
        #         temp['properties']['mtime'] = {
        #             "mtime": "Modified "+datetime.fromtimestamp(os.path.getmtime(targetPath)).strftime(
        #                 "%Y-%m-%d %H:%M:%S"), "readOnly" : "True"}
        #         temp['properties']['ctime'] = {
        #             "ctime": "MetaData modified "+datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "readOnly" : "True"}
        #         temp['properties']['btime'] = {
        #             "btime": "Creation date "+datetime.fromtimestamp(os.path.getctime(targetPath)).strftime(
        #                 "%Y-%m-%d %H:%M:%S"), "readOnly" : "True"}
        #         mydb().insertDB(temp)
        # except shutil.Error as e:
        #     print('Directory not copied. Error: %s' % e)
        #     # Copy at the same path
        # except OSError as e:
        #     print('Directory not copied. Error: %s' % e)
        #     # Copy failed
        pass

    def moveNode(self, targetPath, locationPath):
        # Move the node and the subnodes
        pass

    def deleteNode(self, targetPath):
        # Delete the node and the subnodes
        path, target = os.path.split(targetPath)
        _, parent = os.path.split(path)
        if not _:
            # MongoDB ancestor field will not work if
            # ancestor = ['']
            ancestor = []
        else:
            ancestor = _.split(os.sep)
        if "nodes" in ancestor:
            ancestor.remove("nodes")
        if os.path.exists(targetPath):
            if mydb().connexion().delete_one({'node': target, 'parent': parent, 'ancestor': ancestor}):
                if parent:
                    ancestor.append(parent)
                if mydb().connexion().delete_many({'parent': target, 'ancestor': ancestor}):
                    if os.path.isdir(targetPath):
                        shutil.rmtree(targetPath)
                    elif os.path.isfile(targetPath):
                        os.remove(targetPath)
        else:
            return "FileNotFound"

    def pushToVoSpace(self, targetPath, **kwargs):
        # Execute a push to VOSpace
        pass

    def pushFromVoSpace(self, targetPath, **kwargs):
        # Execute a push from VOSpace
        pass

    def pullFromVoSpace(self, targetPath, **kwargs):
        # Execute a pull from VOSpace
        pass

    def pullToVoSpace(self, targetPath, endpointUri):
        # Execute a pull to VOSpace
        pass


# a = Vospace()
# print(mydb().nodeExistsChecker(os.path.basename("./VOTest/VOSpace/nodes/myresult1")))
# a.startup()
# # print(a.getEndpoint("./VOTest/VOSpace/nodes/myresult1"))
# # for k,v in a.getNode("./VOTest/VOSpace/nodes/myresult1")['properties']['type'].items():
# #     print(v)
# # a.createNode("./VOTest/VOSpace/nodes/myresult5", "ContainerNode")
# # print(a.nodeExistsChecker(os.path.basename("./VOTest/VOSpace/nodes/myresult4")))

# a.setNode("myresult1/BBBBB",{'language': ['français', 'False'], 'title': ['test de création', 'False'], 'description': ['FooBarTotoTiti', 'False']})
# # print(a.copyNode("./VOTest/VOSpace/nodes/myresult1", "./VOTest/copy/myresult1"))
# mydb().setViews("./VOTest/VOSpace/nodes/myresult1",{'anyview' : 'ivo://ivoa.net/vospace/core#anyview', 'fits' : 'ivo://ivoa.net/vospace/core#fits' },
#                                                      {'default' : 'ivo://ivoa.net/vospace/core#defaultview', 'fits' :  'ivo://ivoa.net/vospace/core#fits' })

# pprint(mydb().getMeta("./VOTest/copy/myresult1"))
# a.deleteNode("./VOTest/copy/myresult2/metamyresult2")
# print(os.path.exists("./VOTest/copy/myresult2/metamyresult2"))