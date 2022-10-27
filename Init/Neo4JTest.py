from py2neo import Graph

graph = Graph("bolt://433-34.csse.rose-hulman.edu:7687",
              auth=("neo4j", "neo4j"))

results = graph.run("MATCH(n) return n")

results = graph.run(
    "MATCH (b: Pokemon)-[e*] -> (a) WHERE b.id=10  return a,e")
# print(results)


for e in results:
    # print(b)
    print("  ")
    print(e)
    print("  ")
    # print(a)
    print("  ")
    print("  ")
    print("  ")
