#!/usr/bin/python

import os
import sys, getopt
import marshal
from ast import parse
from .AstPySum import AstPySum
from os.path import join, abspath, splitext, realpath
from xml.dom.minidom import Document
import pickle

def IsInExpList (py, PyFile, ExpList):
    #default
    if PyFile.find ("test") != -1:
        return True

    if ExpList == None:
        return False
    if py in ExpList:
        return True
    for exp in ExpList:
        Hd = exp[0:2]
        if Hd != "-D":
            continue
        if PyFile.find (exp[2:]) != -1:
            return True
    return False

def _AddChildNode (Doc, Parent, Child, Value=None):
    CNode = Doc.createElement(Child)
    Parent.appendChild(CNode)
    if Value != None:
        Val = Doc.createTextNode(Value)
        CNode.appendChild(Val)
    return CNode
    

def GenPySummary (PyDir, ExpList=None):
    doc  = Document()  
    Root = _AddChildNode (doc, doc, "py_summary")

    SrcApiList = {}
    FuncDefList = {}
    BranchNum = 0

    FileId    = 1
    
    PyDirs = os.walk(PyDir) 
    for Path, Dirs, Pys in PyDirs:
        for py in Pys:
            _, Ext = os.path.splitext(py)
            if Ext != ".py":
                continue
         
            PyFile = os.path.join(Path, py)
            if IsInExpList (py, PyFile, ExpList) == True:
                continue

            with open(PyFile) as PyF:
                print ("#visit " + PyFile)
                Ast = parse(PyF.read(), PyFile, 'exec')
                Visitor= AstPySum()
                Visitor.visit(Ast)
 
                # function definition retrieve
                FuncDef = Visitor.FuncDef

                # add childnode file
                FileNode = _AddChildNode (doc, Root, "file")
                FileNode.setAttribute ("name", py)
                FileNode.setAttribute ("id", str(FileId))
                FileId += 1

                for FuncName, Def in FuncDef.items ():
                    BrVals = Def.GetBrVar ()

                    if len (Def.BBNo) == 0:
                        continue

                    if Def.Sline == 0:
                        continue
                        
                    if Def.Eline == 0:
                        Def.Eline = Def.BBNo[-1]    
                    
                    FuncNode = _AddChildNode (doc, FileNode, "function")
                    FuncNode.setAttribute ("class", Def.Cls)
                    FuncNode.setAttribute ("name",  Def.Name)
                    FuncNode.setAttribute ("sline", str(Def.Sline))
                    FuncNode.setAttribute ("eline", str(Def.Eline))
                    FuncNode.setAttribute ("brval", BrVals)
                    FuncNode.setAttribute ("bbs", " ".join(Def.BBNo))

                    BranchNum += len (Def.BBNo) + 1

    Root.setAttribute ("branchs", str(BranchNum))
    
    # write to xml
    PySum = PyDir+"/py_summary.xml"
    print ("Write -> " + PySum)
    f = open(PySum, "w")
    f.write(doc.toprettyxml(indent="  "))
    f.close()

