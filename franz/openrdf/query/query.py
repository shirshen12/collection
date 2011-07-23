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

from ..exceptions import IllegalOptionException, QueryMissingFeatureException
from . import commonlogic
from .dataset import ALL_CONTEXTS, Dataset
from .queryresult import GraphQueryResult, TupleQueryResult
from ..repository.jdbcresultset import JDBCQueryResultSet
import datetime

class QueryLanguage:
    registered_languages = []
    SPARQL = None
    PROLOG = None
    COMMON_LOGIC = None
    def __init__(self, name):
        self.name = name
        QueryLanguage.registered_languages.append(self)
        
    def __str__(self): return self.name
    
    def getName(self): return self.name

    @staticmethod
    def values(): return QueryLanguage.registered_languages[:]
    
    @staticmethod
    def valueOf(name): 
        for ql in QueryLanguage.registered_languages:
            if ql.name.lower() == name.lower():
                return ql
        return None
    
QueryLanguage.SPARQL = QueryLanguage('SPARQL')
QueryLanguage.PROLOG = QueryLanguage('PROLOG')
QueryLanguage.COMMON_LOGIC = QueryLanguage('COMMON_LOGIC')

#############################################################################
##
#############################################################################

TRACE_QUERY = False

def trace_it(*messages):
    if TRACE_QUERY:
        print(' '.join([str(m) for m in messages]))

class Query(object):
    """
    A query on a {@link Repository} that can be formulated in one of the
    supported query languages (for example SeRQL or SPARQL). It allows one to
    predefine bindings in the query to be able to reuse the same query with
    different bindings.
    """
    def __init__(self, queryLanguage, queryString, baseURI=None):
        self.queryLanguage = queryLanguage
        self.queryString = queryString
        self.baseURI = baseURI
        self.dataset = None
        self.includeInferred = False
        self.bindings = {}
        self.connection = None
        self.checkVariables = False
        ## CommonLogic parameters:
        self.preferred_execution_language = None
        self.actual_execution_language = None
        self.subject_comes_first = False

    @staticmethod
    def set_trace_query(setting):
        global TRACE_QUERY
        TRACE_QUERY = setting

    def setBinding(self, name, value):
        """
        Binds the specified variable to the supplied value. Any value that was
        previously bound to the specified value will be overwritten.
        """
        if isinstance(value, str):
            value = self._get_connection().createLiteral(value)
        self.bindings[name] = value
        
    def setBindings(self, dict):
        if not dict: return
        for key, value in dict.iteritems():
            self.setBinding(key, value)

    def removeBinding(self, name):
        """ 
        Removes a previously set binding on the supplied variable. Calling this
        method with an unbound variable name has no effect.
        """
        self.bindings.popitem(name, None)

    def getBindings(self):
        """
        Retrieves the bindings that have been set on this query. 
        """ 
        return self.bindings

    def setDataset(self, dataset):
        """
        Specifies the dataset against which to evaluate a query, overriding any
        dataset that is specified in the query itself. 
        """ 
        self.dataset = dataset
     
    def getDataset(self):
        """
        Gets the dataset that has been set.
        """ 
        return self.dataset
    
    def setContexts(self, contexts):
        """
        Assert a set of contexts (named graphs) that filter all triples.
        """
        if not contexts: return
        ds = Dataset()
        for cxt in contexts:
            if isinstance(cxt, str): cxt = self._get_connection().createURI(cxt)
            ds.addNamedGraph(cxt)
        self.setDataset(ds)
     
    def setIncludeInferred(self, includeInferred):
        """
        Determine whether evaluation results of this query should include inferred
        statements (if any inferred statements are present in the repository). The
        default setting is 'true'. 
        """ 
        self.includeInferred = includeInferred

    def getIncludeInferred(self):
        """
        Returns whether or not this query will return inferred statements (if any
        are present in the repository). 
        """ 
        return self.includeInferred
    
    def setCheckVariables(self, setting):
        """
        If true, the presence of variables in the select clause not referenced in a triple
        are flagged.
        """
        self.checkVariables = setting
    
    def setConnection(self, connection):
        """
        Internal call to embed the connection into the query.
        """
        self.connection = connection
        
    def _get_connection(self):
        return self.connection
    
    TEMPORARY_ENUMERATION_RESOURCE = 'http://www.franz.com#TeMpOrArYeNuMeRaTiOn'
    
    def count_temporaries(self, message):
        conn = self._get_connection()
        result = conn.getStatements(conn.createURI(Query.TEMPORARY_ENUMERATION_RESOURCE), None, None, None)
        trace_it(message + "^^^^^Found {0} temporary quads".format(len(result.string_tuples)))
    
    def insert_temporary_enumerations(self, temporary_enumerations, insert_or_retract, contexts):
        """
        Enormous hack to circumvent AG's (SPARQL's) lack of a membership operator.
        """
        if not temporary_enumerations: return
        conn = self._get_connection()
        context = conn.createURI(contexts[0]) if contexts else conn.createURI(Query.TEMPORARY_ENUMERATION_RESOURCE)
        quads = []
        for tempRelationURI, enumeratedValues in temporary_enumerations.iteritems():
            for v in enumeratedValues:
                if v and v[0] == '"':
                    if v[len(v) - 1] == '"':
                        v = v[1:-1]
                    val = conn.createLiteral(v)
                else:
                    val = conn.createURI(v)
                quads.append((conn.createURI(Query.TEMPORARY_ENUMERATION_RESOURCE), conn.createURI(tempRelationURI), val, context))
        self.count_temporaries("BEFORE " + insert_or_retract + "  " + str(len(quads)) + " coming")
        if insert_or_retract == 'INSERT':
            if quads:
                t = quads[0]
                trace_it("INSERT QUAD", (str(t[0]), str(t[1]), str(t[2]), str(t[3])))
            conn.addTriples(quads)
        else:
            if quads:
                t = quads[0]
                trace_it("RETRACT QUAD", (str(t[0]), str(t[1]), str(t[2]), str(t[3])))
            conn.removeQuads(quads)
        self.count_temporaries("AFTER " + insert_or_retract)
    
    def evaluate_generic_query(self, accept=None):
        """
        Evaluate a SPARQL or PROLOG or COMMON_LOGIC query, which may be a 'select', 'construct', 'describe'
        or 'ask' query (in the SPARQL case).  Return an appropriate response.
        """
        ##if self.dataset and self.dataset.getDefaultGraphs() and not self.dataset.getDefaultGraphs() == ALL_CONTEXTS:
        ##    raise UnimplementedMethodException("Query datasets not yet implemented for default graphs.")
        conn = self._get_connection()
        namedContexts = conn._contexts_to_ntriple_contexts(
                        self.dataset.getNamedGraphs() if self.dataset else None)
        regularContexts = conn._contexts_to_ntriple_contexts(
                self.dataset.getDefaultGraphs() if self.dataset else ALL_CONTEXTS)
        bindings = None
        if self.bindings:
            bindings = {}
            for vbl, val in self.bindings.items():
                bindings[vbl] = conn._convert_term_to_mini_term(val)
        trace_it("NAMED CONTEXTS", namedContexts, "BINDINGS", bindings)                          
        mini = conn._get_mini_repository()
        if self.queryLanguage == QueryLanguage.SPARQL:  
            query = splicePrefixesIntoQuery(self.queryString, conn)
            response = mini.evalSparqlQuery(query, context=regularContexts, namedContext=namedContexts, 
                                            infer=self.includeInferred, bindings=bindings,
                                            checkVariables=self.checkVariables, accept=accept)
        elif self.queryLanguage == QueryLanguage.PROLOG:
            if namedContexts:
                raise QueryMissingFeatureException("Prolog queries do not support the datasets (named graphs) option.")
            query = expandPrologQueryPrefixes(self.queryString, conn)
            response = mini.evalPrologQuery(query, infer=self.includeInferred, accept=accept)
        elif self.queryLanguage == QueryLanguage.COMMON_LOGIC:
            query, contexts, auxiliary_input_bindings, temporary_enumerations, lang, exception = commonlogic.translate_common_logic_query(self.queryString,
                                    preferred_language=self.preferred_execution_language, contexts=namedContexts)
            if contexts and not namedContexts:
                namedContexts = ["<{0}>".format(uri.getURI()) for uri in commonlogic.contexts_to_uris(contexts, conn)]
            if auxiliary_input_bindings:
                bindings = bindings or {}
                for vbl, val in auxiliary_input_bindings.items():
                    print "AUX", vbl, " VAL", val
                    bindings[vbl] = val
            self.actual_execution_language = lang ## for debugging
            if lang == 'SPARQL':
                trace_it("         SPARQL QUERY", query)                
                trace_it("   BINDINGS ", bindings, "  NAMED CONTEXTS", namedContexts)
                query = splicePrefixesIntoQuery(query, conn)
                try:
                    self.insert_temporary_enumerations(temporary_enumerations, 'INSERT', namedContexts)
                    MINITIMER = datetime.datetime.now()
                    response = mini.evalSparqlQuery(query, context=regularContexts, namedContext=namedContexts, 
                                                infer=self.includeInferred, bindings=bindings, planner='identity')
                    trace_it("mini elapsed time  " +  str(datetime.datetime.now() - MINITIMER))
                finally:                
                    self.insert_temporary_enumerations(temporary_enumerations, 'RETRACT', namedContexts)            
            elif lang == 'PROLOG':
                query = expandPrologQueryPrefixes(query, conn)
                trace_it("         PROLOG QUERY", query)
                response = mini.evalPrologQuery(query, infer=self.includeInferred)
            else:
                raise exception
        return response

    @staticmethod
    def _check_language(queryLanguage):
        if queryLanguage == 'SPARQL': return QueryLanguage.SPARQL
        elif queryLanguage == 'PROLOG': return QueryLanguage.PROLOG
        elif queryLanguage == 'COMMON_LOGIC': return QueryLanguage.COMMON_LOGIC        
        if not queryLanguage in [QueryLanguage.SPARQL, QueryLanguage.PROLOG, QueryLanguage.COMMON_LOGIC]:
            raise IllegalOptionException("Can't evaluate the query language '%s'.  Options are: SPARQL, PROLOG, and COMMON_LOGIC."
                                         % queryLanguage)
        return queryLanguage
            
  

#############################################################################
##
#############################################################################

def splicePrefixesIntoQuery(query, connection):
    """
    Add build-in and registered prefixes to 'query' when needed.
    """
    lcQuery = query.lower()
    referenced = []
    for prefix, ns in connection.getNamespaces().iteritems():
        if lcQuery.find(prefix) >= 0 and lcQuery.find("prefix %s" % prefix) < 0:
            referenced.append((prefix, ns))
    for ref in referenced:
        query = "PREFIX %s: <%s> %s" % (ref[0], ref[1], query)
    return query

def helpExpandPrologQueryPrefixes(query, connection, startPos):
    """
    Convert qnames in 'query' that match prefixes with declared namespaces into full URIs.
    """
    if startPos >= len(query): return query
    lcQuery = query.lower()
    bangPos = lcQuery[startPos:].find('!')
    if bangPos >= 0:
        bangPos = bangPos + startPos
        startingAtBang = lcQuery[bangPos:]
        if len(startingAtBang) > 1 and startingAtBang[1] == '<':
            ## found a fully-qualified namespace; skip past it
            endPos = startingAtBang.find('>')
            if endPos < 0: return query ## query is illegal, but that's not our problem
            return helpExpandPrologQueryPrefixes(query, connection, bangPos + endPos + 1)
        colonPos = startingAtBang.find(':')
        if colonPos >= 0:
            colonPos = bangPos + colonPos
            prefix = lcQuery[bangPos + 1:colonPos]
            ns = connection.getNamespace(prefix)
            if ns:
                for i, c in enumerate(lcQuery[colonPos + 1:]):
                    if not (c.isalnum() or c in ['_', '.', '-']): break
                endPos = colonPos + i + 1 if i else len(query) + 1
                localName = query[colonPos + 1: endPos]
                query = query[:bangPos + 1] + ("<%s%s>" % (ns, localName)) + query[endPos:]
                return helpExpandPrologQueryPrefixes(query, connection, endPos)
    return query

def expandPrologQueryPrefixes(query, connection):
    """
    Convert qnames in 'query' that match prefixes with declared namespaces into full URIs.
    This assumes that legal chars in local names are alphanumerics and underscore and period.
    """
    query = helpExpandPrologQueryPrefixes(query, connection, 0)
    #print "AFTER EXPANSION", query
    return query

class TupleQuery(Query):
    def __init__(self, queryLanguage, queryString, baseURI=None):
        queryLanguage = Query._check_language(queryLanguage)
        super(TupleQuery, self).__init__(queryLanguage, queryString, baseURI=baseURI)
        self.connection = None
        
    def evaluate(self, jdbc=False):
        """
        Execute the embedded query against the RDF store.  Return
        an iterator that produces for each step a tuple of values
        (resources and literals) corresponding to the variables
        or expressions in a 'select' clause (or its equivalent).
        If 'jdbc', returns a JDBC-style iterator that miminizes the
        overhead of creating response objects.         
        """
        response = self.evaluate_generic_query()
        if jdbc:
            return JDBCQueryResultSet(response['values'], column_names = response['names'])
        else:
            return TupleQueryResult(response['names'], response['values'])

class GraphQuery(Query):
    
    def evaluate(self):
        """
        Execute the embedded query against the RDF store.  Return
        a graph.
        """
        response = self.evaluate_generic_query()
        return GraphQueryResult(response)

class BooleanQuery(Query):
    
    def evaluate(self):
        """
        Execute the embedded query against the RDF store.  Return
        True or False
        """
        return self.evaluate_generic_query()


