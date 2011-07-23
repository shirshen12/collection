#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103 

##***** BEGIN LICENSE BLOCK *****
##Version: MPL 1.1
##
##The contents of this file are subject to the Mozilla Public License Version
##1.1 (the "License"); you may not use this file except in compliance with
##the License. You may obtain a copy of the License at
##http:##www.mozilla.org/MPL/
##
##Software distributed under the License is distributed on an "AS IS" basis,
##WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
##for the specific language governing rights and limitations under the
##License.
##
##The Original Code is the AllegroGraph Java Client interface.
##
##The Original Code was written by Franz Inc.
##Copyright (C) 2006 Franz Inc.  All Rights Reserved.
##
##***** END LICENSE BLOCK *****

from __future__ import absolute_import

from .value import Value, BNode, URI
from .literal import Literal, CompoundLiteral, RangeLiteral, GeoCoordinate
from .statement import Statement
from ..vocabulary.xmlschema import XMLSchema

import datetime, traceback

class ValueFactory(object):
    """
    A factory for creating URIs, blank nodes, literals and statements.
    """
    BLANK_NODE_AMOUNT = 10    
    def __init__(self, store):
        self.store = store
        self.store.getConnection().setNamespace("fti", "http://franz.com/ns/allegrograph/2.2/textindex/")
        self.unusedBNodeIds = []
        
    def getUnusedBNodeId(self):
        if not self.unusedBNodeIds:
            ## retrieve a set of bnode ids (they include leading '_:', which we strip off later:
            self.unusedBNodeIds = self.store.mini_repository.getBlankNodes(amount=ValueFactory.BLANK_NODE_AMOUNT)
        return self.unusedBNodeIds.pop()[2:] ## strip off leading '_:'

    def createBNode(self, nodeID=None):
        """
        Creates a new blank node with the given node identifier.
        """
        if not nodeID:
            nodeID = self.getUnusedBNodeId()
        return BNode(nodeID)
    
    @staticmethod
    def _interpret_value(value, datatype):
        """
        If 'self' is not a string, convert it into one, and infer its
        datatype, unless 'datatype' is set (i.e., overrides it).
        """
        if isinstance(value, str):
            return value, datatype
        ## careful: test for 'bool' must precede test for 'int':
        elif isinstance(value, bool):
            return str(value), datatype or XMLSchema.BOOLEAN
        elif isinstance(value, int):
            return str(value), datatype or XMLSchema.INT
        elif isinstance(value, float):
            return str(value), datatype or XMLSchema.FLOAT
        elif isinstance(value, datetime.datetime):
            ## TODO: NEED TO ADD TIMEZONE VALUE??:
            value = value.strftime(Literal.ISO_FORMAT_WITH_T) ## truncate microseconds  
            return value, datatype or XMLSchema.DATETIME
        elif isinstance(value, datetime.time):
            value = value.strftime(Literal.ISO_FORMAT_WITH_T) ## UNTESTED
            return str(value), datatype or XMLSchema.TIME
        elif isinstance(value, datetime.date):
            value = value.strftime(Literal.ISO_FORMAT_WITH_T) ## UNTESTED
            return str(value), datatype or XMLSchema.DATE
        else:
            return str(value), datatype
    
    def createLiteral(self, value, datatype=None, language=None):
        """
        Create a new literal with value 'value'.  'datatype' if supplied,
        should be a URI, in which case 'value' should be a string.
        """
        if isinstance(value, (tuple, list)) and len(value) == 2:
            return self.createRange(value[0], value[1])
        value, datatype = ValueFactory._interpret_value(value, datatype)
        return Literal(value, datatype=datatype, language=language)
        

    def createStatement(self, subject, predicate, _object, context=None):
        """
        Create a new statement with the supplied subject, predicate and object
        and associated context.  Arguments have type Resource, URI, Value, and Resource.
        """
        return Statement(subject, predicate, _object, context=context)
    
    def createURI(self, uri=None, namespace=None, localname=None):
        """
        Creates a new URI from the supplied string-representation(s).
        If two non-keyword arguments are passed, assumes they represent a
        namespace/localname pair.
        """
        if namespace and not localname:
            return URI(namespace=uri, localname=namespace)
        else:
            return URI(uri=uri, namespace=namespace, localname=localname)
    

#############################################################################
## Extension to Sesame API
#############################################################################

    def validateRangeConstant(self, term, predicate):
        """Validate an individual range constant"""
        datatype = term.getDatatype()
        if not datatype:
            raise Exception('Illegal term in range expression "%s" needs to '
                            'have a datatype.' % term.getValue())

        rep = self.store.getConnection().repository
        if datatype not in rep.mapped_datatypes and \
           (not predicate or predicate.getURI() not in rep.mapped_predicates):
            raise Exception('Illegal term in range expression "%s" with '
                            'datatype "%s" does not have a datatype or '
                            'predicate mapping.' %
                             (term.getValue(), datatype))

    def validateCompoundLiteral(self, term, predicate):
        """
        Check to see if range boundaries are mapped.
        TODO: ADD VALIDATION FOR GEO TERMS
        """
        if isinstance(term, RangeLiteral):
            self.validateRangeConstant(term.lowerBound, predicate)
            self.validateRangeConstant(term.upperBound, predicate)
        elif isinstance(term, GeoCoordinate):
            pass
        
    def object_position_term_to_openrdf_term(self, term, predicate=None):
        """
        If 'term' is a string, integer, float, etc, convert it to
        a Literal term.  Otherwise, if its a Value, just pass it through.
        """
        if term is not None:
            if isinstance(term, CompoundLiteral): 
                self.validateCompoundLiteral(term, predicate)
            elif not isinstance(term, Value):
                term = self.createLiteral(term)
        return term
    
    def createRange(self, lowerBound, upperBound):
        """
        Create a compound literal representing a range from 'lowerBound' to 'upperBound'
        """
        lowerBound = self.object_position_term_to_openrdf_term(lowerBound)
        upperBound = self.object_position_term_to_openrdf_term(upperBound)
        return RangeLiteral(lowerBound=lowerBound, upperBound=upperBound)
