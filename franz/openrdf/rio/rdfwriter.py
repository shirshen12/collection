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

from .rdfformat import RDFFormat
from .converter import statement2ntriples

class RDFWriter(object):
    def __init__(self, rdfFormat, filePath=None):
        self.rdf_format = rdfFormat
        self.file_path = filePath
        
    def getRDFFormat(self):
        return self.rdf_format
    
    def getFilePath(self):
        return self.file_path 

            
class NTriplesWriter(RDFWriter):
    """
    Records the format as
    NTriples, and records the 'filePath' where the serialized RDF will
    be output to.  If 'filePath' is None, output is to standard output.
    
    TODO: THERE IS A WRITER PROTOCOL IMPLEMENTED IN RDFXMLWriter THAT ISN'T
    IMPLEMENTED HERE.  CONSIDER ADDING IT (OR NOT).
    """
    def __init__(self, filePath=None):
        super(NTriplesWriter, self).__init__(RDFFormat.NTRIPLES, filePath)
        
    def handleNamespace(self, prefix, name):
        """
        NTriples doesn't use prefixes.
        """
        pass
        
    def export(self, statements):
        """
        Iterator over the statements in 'statements', and write an NTriples 
        representation of each statement to a file, or to standard output.
        """
        if self.file_path:
            file = open(self.file_path, 'w')
            strings = []
            for s in statements:
                strings.append(statement2ntriples(s, None))
            file.writelines(strings)
        else:
            buffer = []
            for s in statements:
                statement2ntriples(s, buffer)
            result = ''.join(buffer)
            print result
            
        
