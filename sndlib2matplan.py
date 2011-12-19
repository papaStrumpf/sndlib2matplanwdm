#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""sndlib to MatPlanWD XML file converter

Copyright (C) <2011> Robert Vežnaver <robert.veznaver@fer.hr>
Released under the GNU General Public License.

This utility converts a sndlib network model XML file 
to a MatPlanWDM XML network model file.

Sndlib files are available from:
http://sndlib.zib.de/

MatPlanWDM is available from:
http://www.ait.upct.es/~ppavon/matplanwdm/

"""

import sys
import math
from xml.etree import ElementTree as ET

def calcGeoDistance(lat1=0, lon1=0, lat2=0, lon2=0):
    """Python implementation of the Haversine formula

    Copyright (C) <2009> Bartek Górny <bartek@gorny.edu.pl>
    Released under the GNU General Public License.

    This module implements the Haversin formula for calculating
    the distance between two points on a sphere.
    http://en.wikipedia.org/wiki/Haversine_formula
    
    """
    start_long = math.radians(lon1)
    start_latt = math.radians(lat1)
    end_long = math.radians(lon2)
    end_latt = math.radians(lat2)
    d_latt = end_latt - start_latt
    d_long = end_long - start_long
    a = math.sin(d_latt/2)**2 + \
        math.cos(start_latt) * math.cos(end_latt) * math.sin(d_long/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371 * c

def getCityList(tree, namespace=""):
    """Extracts the city name, longitude & latitude
    
    Needs an ElementTree instance and namespace.
    Returns a list of dicts with the above info.
    
    """
    nodeList = tree.findall\
        ("{0}networkStructure/{0}nodes/{0}node".format(namespace))
   
    (cityList, x, y) = (list(), 0, 0)
    for node in nodeList:
        name = node.attrib["id"]
        for coordinates in node:
            for element in coordinates:
                if element.tag == "{0}x".format(namespace):
                    x = element.text
                if element.tag == "{0}y".format(namespace):
                    y = element.text
        cityList.append({"name":name, "x":x, "y":y})
    return cityList

def getLinkList(tree, namespace=""):
    """Extracts the link origin and destination
    
    Needs an ElementTree instance and namespace.
    Returns a list of dicts with the above info.
    
    """
    linkListXML = tree.findall\
        ("{0}networkStructure/{0}links/{0}link".format(namespace))
   
    (linkList, x, y) = (list(), 0, 0)
    for link in linkListXML:
        for element in link:
            if element.tag == "{0}source".format(namespace):
                source = element.text
            if element.tag == "{0}target".format(namespace):
                target = element.text
        linkList.append({"source":source, "target":target})
    return linkList

def main():   
    # read in XML from file
    fp = open(sys.argv[1],"r")
    tree = ET.parse(fp)
    fp.close

    # extract namespace from the root element
    namespace = tree.getroot().tag
    namespace = namespace[namespace.find("{"):namespace.find("}")+1]
  
    # write out header
    print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    print "<!DOCTYPE network SYSTEM \"../dtd/vtDesign.dtd\">"
    print "<network author=\"\" date=\"\" description=\"\" "\
        + "flowGeneratorFile=\"\" flowGeneratorParametersString=\"\" "\
        + "multihourPlanning=\"false\" title=\""\
        + str(sys.argv[1][:-4]) + "\" "\
        + "planningAlgorithmFile=\"\" "\
        + "planningAlgorithmParametersString=\"\" trafficMatrixFile=\"\">"
    print "\t<layer id=\"physicalTopology\">"

    # extract city list and write out
    cityList = getCityList(tree,namespace)
    for counter, city in enumerate(cityList):
        print "\t\t<node id=\""\
            + str(counter+1)\
            + "\" nodeLevel=\"1\" nodeName=\""\
            + city["name"]\
            + "\" nodePopulation=\"#POP#\" nodeTimezone=\"1\" xCoord=\""\
            + city["x"]\
            + "\" yCoord=\""\
            + city["y"]\
            + "\">"
        if counter <= ((len(cityList)-1)/2):
            print "\t\t\t<eoTransmitter number=\"10\"/>"
            print "\t\t\t<oeReceiver number=\"10\"/>"
        else:
            print "\t\t\t<eoTransmitter number=\"10000\"/>"
            print "\t\t\t<oeReceiver number=\"10000\"/>"
        print "\t\t\t<wc number=\"0\"/>"
        print "\t\t</node>"

    # extract link list and write out
    linkList = getLinkList(tree,namespace)
    for counter, link in enumerate(linkList):
        # find source and target city index in list
        try:
            source = next(cnt for cnt, city in enumerate(cityList)\
                if link["source"] in city["name"])
        except StopIteration:
            print >> sys.stderr, link["source"] + " not found in city list!"
        try:
            target = next(cnt for cnt, city in enumerate(cityList)\
                if link["target"] in city["name"])
        except StopIteration:
            print >> sys.stderr, link["target"] + " not found in city list!"
        # write out
        print "\t\t<fibre id=\""\
            + str(counter+1)\
            + "\" origNodeId=\""\
            + str(source+1)\
            + "\" destNodeId=\""\
            + str(target+1)\
            + "\" linkLengthInKm=\""\
            + str(int(calcGeoDistance(\
                float(cityList[source]["y"]),\
                float(cityList[source]["x"]),\
                float(cityList[target]["y"]),\
                float(cityList[target]["x"]))))\
            + "\" numberWavelengths=\"40\" />"

    # write out footer
    print "\t\t<levelInformationMatrix>"
    print "\t\t\t<factor idDest=\"1\" idOrig=\"1\" value=\"1\"/>"
    print "\t\t</levelInformationMatrix>"
    print "\t\t<lightpathCapacity value=\"40\"/>"
    print "\t</layer>"
    print "</network>"

if __name__ == "__main__":
    main()

