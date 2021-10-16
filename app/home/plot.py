import random
from jinja2 import Template
import pandas as pd
import numpy as np
import networkx as nx
from collections import Counter
def buildGraph(node,Graph):
  G = nx.read_gpickle("graph.gpickle")
  done=[]
  linkWith=list(G.neighbors(node))[:7]
  Graph.append({"name":node,"value":15,"linkWith":linkWith })
  
  linkWith1=[]
  notlist=[]
  for x in linkWith:
    children=[]
    if x not in done:
      ch=list(G.neighbors(x))
      #print("@@@@@@@@@@@",x,ch)
      i=0
      for y in ch:
        if y in linkWith:
          linkWith1.append(y)
        elif y in notlist:
          continue
        elif y !=node :
          i+=1
          notlist.append(y)
          children.append({"name":y,"value":5})
          if i>7:
            break
      Graph.append({"name":x,"value":10,"linkWith":linkWith1,"children":children  })
      done.append(x)



def clevel(G,nodes,recommended,Graph):
  linkWith=[]
  done=[]
  a = set(recommended)
  for node in nodes:
    b=set(G.neighbors(node))
    common=a & b
    if(common):
      linkWith=list(common)  
    
    Graph.append({"name":node,"value":15,"linkWith":linkWith })
    
    linkWith=[]
    notlist=[]
    for x in common:
      children=[]
      if x not in done:
        ch=list(G.neighbors(x))
        #print("@@@@@@@@@@@",x,ch)
        i=0
        for y in ch:
          if y in common:
            linkWith.append(y)
          elif y in notlist:
            continue
          elif y !=node :
            i+=1
            notlist.append(y)
            children.append({"name":y,"value":5})
            if i>7:
              break
        Graph.append({"name":x,"value":10,"linkWith":linkWith,"children":children  })
        done.append(x)
    
def getRecommendations(ilist,dont,flatJlist):

  G = nx.read_gpickle("graph.gpickle")
  alreadyRecommend=[]
  for r in ilist:
    if r!="None":
      alreadyRecommend.append(r)

  #alreadyRecommend.extend(skills)
  #print(alreadyRecommend)
  
  temp={}
  temp1={}
  #flatJlist = [j for sub in jlist for j in sub]
  counter = Counter(flatJlist)

  klist=counter.keys()
  for node in alreadyRecommend:
      l1=list(G.neighbors(node))
      for e in l1:
          if e in temp:
              temp[e]+=1
          else:
              temp[e]=1
          if e in klist:
            temp1[e]=counter[e]
          
      
  recommend=list(dict(sorted(temp.items(), key=lambda item: item[1],reverse=True)).keys())
  for thing in dont:
    if thing in recommend: recommend.remove(thing)
  recommend=recommend[:5]

  crecommend=list(dict(sorted(temp1.items(), key=lambda item: item[1],reverse=True)).keys())
  for thing in dont:
    if thing in crecommend: crecommend.remove(thing)
  #l=recommend.copy()
  Graph1=[]
  Graph=[]
  clevel(G,alreadyRecommend,recommend,Graph)
  clevel(G,alreadyRecommend,crecommend,Graph1)
  
  #print(Graph)

  return recommend,Graph,crecommend,Graph1
