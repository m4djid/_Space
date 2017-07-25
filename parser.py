# Classe traitant les fichiers ET XML ET les reponses du service

import os
import xml.dom.minidom as dom_
import xml.etree.ElementTree as ET


class Parser(object):

    attribut_direction = ""
    url_fichier = ""
    vu = ""
    distant = {}
    RACINE = "./VOTest"

    def xml_parser(self, xml):
        xmltodict = {
            "accepts": [],
            "provides": [],
            "capabilities": [],
        }

        root = ET.fromstring(xml)

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
                xmltodict['path'] = uri + "/" + cible
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
                                else:
                                    xmltodict['properties'][ind][1] = _
                        if k == "uri":
                            ind = v[v.rfind("#"):][1:]
                            if not _:
                                _ = "False"
                            xmltodict['properties'][ind] = [subchildrens.text, _]

        return xmltodict

    # def var_assign(self, node, string, idx):
    #     global url_fichier, attribut_direction, vu
    #     index = idx - 1
    #     if string == "targET":
    #         self.url_fichier = node[index].text
    #     elif string == "direction":
    #         self.attribut_direction = node[index].text
    #     elif string == "view":
    #         self.vu = node[index].attrib
    #
    # def xml_tag_reader(self, root):
    #     retour = {}
    #     global distant
    #     i = 1
    #     for index, childs in enumerate(root.iter()):
    #         self.var_assign(root, childs.tag[38:], index)
    #         for subchild in childs:
    #             if "endpoint" in subchild.tag:
    #                 self.distant[subchild.tag[38:] + str(i)] = {"destination": subchild.text}
    #                 i += 1
    #         if len(childs.attrib) != 0 and len(childs.tag) != 0:
    #             tag = childs.tag[38:]
    #             att = childs.attrib
    #             retour[tag] = att
    #     return retour

    # def protocol_parser(self, dictionary):
    #     if "protocol" in dictionary:
    #         if "ivo://ivoa.net/vospace/core#httpgET" in dictionary["protocol"].values():
    #             return "ivo://ivoa.net/vospace/core#httpgET"
    #         elif "ivo://ivoa.net/vospace/core#httppost" in dictionary["protocol"].values():
    #             return "ivo://ivoa.net/vospace/core#httppost"
    #         elif "ivo://ivoa.net/vospace/core#httpput" in dictionary["protocol"].values():
    #             return "ivo://ivoa.net/vospace/core#httpput"
    #         elif "ivo://ivoa.net/vospace/core#httpdelETe" in dictionary["protocol"].values():
    #             return "ivo://ivoa.net/vospace/core#httpdelETe"

    # Format XML Response
    def xml_formateur(self, element):
        chaine_originale = ET.tostring(element)
        reparsed = dom_.parseString(chaine_originale)
        return reparsed.toprettyxml(indent="    ")

    # Generate XML Response
    def xml_generator(self, action, node):
        PREFIX = "vos:"
        SUFFIX = ":vos"
        VOSNODE = 'vos:node'
        VOSTRANSFER = 'vos:transfer'
        VOSTARGET = 'vos:targET'
        VOSDIRECT = 'vos:direction'
        VOSPROT = 'vos:protocol'
        VOSENDPOINT = 'vos:endpoint'
        XMLNS = 'xmnls'
        XMLNSVOS = 'xmlns:vos'
        XMLNSW3C = 'xmlns:xs'
        W3C_URI = "http://www.w3.org/2001/XMLSchema-instance"
        VOSPACE_URI = "http://www.ivoa.net/xml/VOSpace/v2.1"
        CORE_uri = "ivo://ivoa.net/vospace/core#"
        URI_V = "uri"
        # Generate GETProtocols, GETViews or GETProperties XML
        if action in ["protocols", "views", "properties"]:
            temp = node
            top = ET.Element(PREFIX + action)
            top.set(XMLNSVOS, VOSPACE_URI)
            top.set(XMLNSW3C, W3C_URI)

            accept = ET.SubElement(top, PREFIX + "accepts")
            for keys, values in temp["accepts"].items():
                accept_ = ET.SubElement(accept, PREFIX+action[:1])
                accept_.set(URI_V, values)

            provide = ET.SubElement(top, PREFIX + "provides")
            for keys, values in temp["provides"].items():
                provide_ = ET.SubElement(provide, PREFIX+action[:len(action)-1])
                provide_.set(URI_V, values)

            if action == 'properties':
                contain = ET.SubElement(top, PREFIX + "contains")
                for keys, values in temp["contains"].items():
                    contain_ = ET.SubElement(contain, PREFIX+"property")
                    contain_.set(URI_V, values)

            return self.xml_formateur(top)

        # Generate GETNode XML
        elif action is "get":
            if node:
                temp = node
                top = ET.Element(PREFIX + 'node')
                top.set(XMLNSVOS, VOSPACE_URI)
                top.set(XMLNSW3C, W3C_URI)
                top.set(URI_V, "vos://example.com!"+temp['path'][0:])
                for k, v in temp['properties']['type'].items():
                    if k != "readonly":
                        top.set("xs:type", PREFIX + v)
                top.set("Busy", temp['busy'])
                properties = ET.SubElement(top, PREFIX + 'properties')
                if temp['properties']:
                    for keys, values in temp['properties'].items():
                        for k, v in values.items():
                            if keys is not "type":
                                if values[k] != '' and k != "readonly":
                                        prop = ET.SubElement(properties, PREFIX + 'property')
                                        prop.set(URI_V, CORE_uri+k)
                                        prop.set("readOnly", values['readonly'])
                                        prop.text = v
                else:
                    prop = ET.SubElement(properties, PREFIX + 'property')
                acceptViews = ET.SubElement(top, PREFIX + 'accept')
                if temp['accepts']:
                    for keys, values in temp['accepts'].items():
                        if values is not '':
                            accept_ = ET.SubElement(acceptViews, PREFIX + 'view')
                            accept_.set(URI_V, values)
                else:
                    accept_ = ET.SubElement(acceptViews, PREFIX + 'view')
                provideViews = ET.SubElement(top, PREFIX + 'provide')
                if temp['provides']:
                    for keys, values in temp['provides'].items():
                        if values is not '':
                            provide_ = ET.SubElement(provideViews, PREFIX + 'view')
                            provide_.set(URI_V, values)
                else:
                    provide_ = ET.SubElement(provideViews, PREFIX + 'view')
                capabilities = ET.SubElement(top, PREFIX + 'capabilities')

                children = ET.SubElement(top, PREFIX + 'nodes')
                for childrens in temp['children']:
                    child = ET.SubElement(children, PREFIX + 'node')
                    child.set(URI_V, "vos://example.com!"+childrens['path'][0:])
                    child.set("xs:type", childrens['properties']['type']['type'])
                    child.set("Busy", childrens['busy'])

                    childrenproperties = ET.SubElement(child, PREFIX + 'properties')
                    if childrens['properties']:
                        for keys, values in childrens['properties'].items():
                            for k, v in values.items():
                                if keys not in ["ctime", "type"]:
                                    if values[k] != '' and k != "readonly":
                                            chilprop = ET.SubElement(childrenproperties, PREFIX + 'property')
                                            chilprop.set(URI_V, CORE_uri+k)
                                            chilprop.set("readOnly", values['readonly'])
                                            chilprop.text = v
                    else:
                        chilprop = ET.SubElement(properties, PREFIX + 'property')

                return self.xml_formateur(top)

# a = Parser()
# b = a.xml_parser("""<?xml version="1.0" encoding="UTF-8"?>
# <vos:node xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
#     xmlns:vos="http://www.ivoa.net/xml/VOSpace/v2.1" xs:type="vos:ContainerNode" uri="vos://example.com!nodes/myresult1/BBBBB">
#   <vos:properties>
#   	<vos:property uri="ivo://ivoa.net/vospace/core#title" readOnly="False">test de création</vos:property>
#   	<vos:property uri="ivo://ivoa.net/vospace/core#language">français</vos:property>
#   	<vos:property uri="ivo://ivoa.net/vospace/core#description">FooBarTotoTiti</vos:property>
#   </vos:properties>
#   <vos:accepts/>
#   <vos:provides/>
#   <vos:capabilities/>
#   <vos:nodes/>
# </vos:node>""")
# print(b)