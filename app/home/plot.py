import json

from sqlalchemy.sql.schema import RETAIN_SCHEMA
from bokeh.embed import json_item
from flask import Flask
import random
import csv
from jinja2 import Template
import pandas as pd
import numpy as np
import networkx as nx
from holoviews.element.graphs import layout_nodes
import holoviews as hv
import networkx as nx
from bokeh.resources import CDN
from holoviews import opts
from holoviews.operation.datashader import datashade, bundle_graph
# from bokeh.plotting import figure
# from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges , LabelSet

# from bokeh.transform import linear_cmap
hv.extension("bokeh")

def createlevel(l,uG,G,curNode):
  if l==3:
    #colors[curNode]=5
    return
  #if l==2:
    #colors[curNode]=10
  #if l==1:
    #colors[curNode]=50
  li=list(G.neighbors(curNode))
  random.shuffle(li)
  i=0
  for e in li:
    uG.add_edge(curNode,e)
    if(l==1 and i<5):
      createlevel(l+1,uG,G,e)
      i+=1

# def getUserGraph(G,colors):
#   uG=nx.Graph()
#   #TODO
#   userid=""
#   user='SAL5079'
#   filename="EmployeeActivity.csv"
#   # Open a csv reader called DictReader
#   df = pd.read_csv('CSVs\EmployeeDataset.csv', converters={'skills':pd.eval})
#   user=df[df.username==user]
#   #TODO break skills in the 2 list
#   skills=user.skills.tolist()[0]
#   alreadyRecommend=[]
#   alreadyRecommend.extend(skills)
#   #ls[0]=skills
#   for node in alreadyRecommend:
#     createlevel(1,uG,G,node,colors)
#   return uG
# def clevel(li,r1,r2,r3,r4,Gbig,Graph):
#   linkWith=[]
#   if r1 in li:
#     linkWith.append(r1)
#     li.remove(r1)
#   if r2 in li:
#     linkWith.append(r2)
#     li.remove(r2)
#   if r3 in li:
#     linkWith.append(r3)
#     li.remove(r3)
#   if r4 in li:
#     linkWith.append(r4)
#     li.remove(r4)
#   children=[]
#   for x in li:
#     children.append({"name":x,"value":7})
#   Graph.append({"name":r1,"value":20,"linkWith":linkWith,"children":children  })

# def GraphG1(r1,r2,r3,r4,r5):
#   Graph=[]
#   Gbig = nx.read_gpickle("graph.gpickle") 
  
#   if r1!="None":
#     li=list(Gbig.neighbors(r1))
#     clevel(li,r2,r3,r4,r5,Gbig,Graph)
#   if r2!="None":
#     li=list(Gbig.neighbors(r2))
#     clevel(li,r1,r3,r4,r5,Gbig,Graph)
#   if r3!="None":
#     li=list(Gbig.neighbors(r3))
#     clevel(li,r2,r1,r4,r5,Gbig,Graph)
#   if r4!="None":
#     li=list(Gbig.neighbors(r4))
#     clevel(li,r2,r3,r1,r5,Gbig,Graph)
#   if r5!="None":
#     li=list(Gbig.neighbors(r5))
#     clevel(li,r2,r3,r4,r1,Gbig,Graph)
#   print(Graph)
#   return Graph
def clevel(G,nodes,recommended,Graph):
  linkWith=[]
  done=[]
  a = set(recommended)
  for node in nodes:
    b=set(G.neighbors(node))
    common=a & b
    if(common):
      linkWith=list(common)  
    
    Graph.append({"name":node,"value":20,"linkWith":linkWith })
    children=[]
    linkWith=[]
    i=0
    for x in common:
      if x not in done:
        for y in G.neighbors(x):
          if y in common:
            linkWith.append(y)
          elif y !=node :
            i+=1
            children.append({"name":y,"value":5})
            if i>7:
              break
        Graph.append({"name":x,"value":10,"linkWith":linkWith,"children":children  })
        done.append(x)
    
def getRecommendations(r1,r2,r3,r4,r5):

  G = nx.read_gpickle("graph.gpickle")
  alreadyRecommend=[]
  if r1!="None":
    alreadyRecommend.append(r1)
  if r2!="None":
    alreadyRecommend.append(r2)
  if r3!="None":
    alreadyRecommend.append(r3)
  if r4!="None":
    alreadyRecommend.append(r4)
  if r5!="None":
    alreadyRecommend.append(r5)
  #alreadyRecommend.extend(skills)
  #print(alreadyRecommend)
  Graph=[]
  temp={}
  for node in alreadyRecommend:
      l1=list(G.neighbors(node))
      for e in l1:
          if e in temp:
              temp[e]+=1
          else:
              temp[e]=1
  recommend=list(dict(sorted(temp.items(), key=lambda item: item[1],reverse=True)).keys())[:5]
  l=recommend.copy()
  clevel(G,alreadyRecommend,recommend,Graph)
  print(Graph)
  
  return l,Graph

# def GraphG(r1,r2,r3,r4,r5):
#     print("here")
    

#     Gbig = nx.read_gpickle("graph.gpickle")
#     uG=nx.Graph()
#     alreadyRecommend=[]
#     if r1!="None":
#       alreadyRecommend.append(r1)
#     if r2!="None":
#       alreadyRecommend.append(r2)
#     if r3!="None":
#       alreadyRecommend.append(r3)
#     if r4!="None":
#       alreadyRecommend.append(r4)
#     if r5!="None":
#       alreadyRecommend.append(r5)
#     for node in alreadyRecommend:
#       createlevel(1,uG,Gbig,node)
#     return uG


# def make_plot(G):
#     print(G)
#     kwargs = dict(width=800, height=800, xaxis=None, yaxis=None)
#     opts.defaults(opts.Nodes(**kwargs), opts.Graph(**kwargs))
#     simple_graph = hv.Graph.from_networkx(G, nx.layout.fruchterman_reingold_layout)
#     simple_graph.opts(node_size=10, edge_line_width=1,node_color='circle', node_line_color='gray')
#     print(type(simple_graph))
    
#     bundled = bundle_graph(simple_graph)
#     #opts.Graph(node_size='size' )
#     (datashade(bundled, normalization='linear', width=800, height=800) * bundled.nodes).opts(opts.Nodes(color='circle', size=10, width=1000))
#     p = hv.render(bundled, backend='bokeh')

#     return p


# page = Template("""
# <head>
#   {{ recomm }}
#   {{ resources }}
# </head>
# <body>
# {% extends "layouts/base.html" %} {% block title %} Page Blank {% endblock %}

# <!-- Specific CSS goes HERE -->
# {% block stylesheets %}{% endblock stylesheets %} {% block content %}

# <div class="pcoded-content">
#     <div class="pcoded-inner-content">
#         <!-- [ breadcrumb ] start -->
#         <div class="page-header">
#             <div class="page-block">
#                 <div class="row align-items-center">
#                     <div class="col-md-12">
#                         <div class="page-header-title">
#                             <h5 class="m-b-10">Sample Page</h5>
#                         </div>
#                         <ul class="breadcrumb">
#                             <li class="breadcrumb-item"><a href="/"><i class="feather icon-home"></i></a></li>
#                             <li class="breadcrumb-item"><a href="javascript:">Sample Page</a></li>
#                         </ul>
#                     </div>
#                 </div>
#             </div>
#         </div>
#         <!-- [ breadcrumb ] end -->
#         <div class="main-body">
#             <div class="page-wrapper">
#                 <!-- [ Main Content ] start -->
#                 <div class="row">
#                     <div class="col-sm-12">
#                         <div class="card">
#                             <div class="card-header">
#                                 <h5>Analyse your current skillset to find the next</h5>
#                             </div>
#                             <div class="card-block">
#                                 <p>This section allows our intelligent systems to use the skills set that you posses and recommend you the next one that you should take up to enhance your current skillset and be an overall better employ
#                                 <br>
#                                 <br>
#                                 below are our recommendations, for a more transparent understanding you can also look the brain graph being rendered below

#                                 </p>
#                                 {% for option in recomm %}
#                                 {{option}} <br>
#                                 {% endfor %}
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#                 <!-- [ Main Content ] end -->
#                   <div id="myplot"></div>
#   <div id="myplot2"></div>
#   <script>
#   fetch('/plot')
#     .then(function(response) { return response.json(); })
#     .then(function(item) { Bokeh.embed.embed_item(item); })
#   </script>

#             </div>
#         </div>
#     </div>
# </div>
# {% endblock content %}

# <!-- Specific Page JS goes HERE  -->
# {% block javascripts %}{% endblock javascripts %}
# </body>
# """)