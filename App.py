from email import message
from enum import auto
from pickle import FALSE
from pyexpat.errors import messages
#from time import clock_getres
from pymongo import MongoClient
from pyignite import Client
from neo4j import GraphDatabase
import pymongo
import json
from bson import json_util
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
import os
import router
import socket
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)


# MClient is for mongodb
Mclient = MongoClient("mongodb://433-34.csse.rose-hulman.edu:27017")
db = Mclient['pokemon']

# Iclient is for Ignite.
Iclient = Client()
Iclient.connect('433-34.csse.rose-hulman.edu', 10800)

# Nclient is for neo4j
Nclient = GraphDatabase.driver(
    'bolt://433-34.csse.rose-hulman.edu:7687', auth=('neo4j', 'neo4j'))
# with Nclient.session() as session:
#     session.execute_write(
#         function, param1,param2,...)


# Apach Ignite part
# create a attribute number map for storing the sequence of attributes. Key is the attribute name, value is No.
attributeNo = Iclient.get_or_create_cache("attributeNo")
# fill the attributeNo map.
attributeArray = ["id", "name-from", "type_1", "type_2", "species", "height", "weight", "abilities", "training_catch_rate", "training_base_exp", "training_growth_rate",
                  "breeding_gender_male", "breeding_gender_female", "stats_hp", "stats_attack", "stats_defense", "stats_sp_atk", "stats_sp_def", "stats_speed", "stats_total", "img"]
for i in range(len(attributeArray)):
    attributeNo.put(i, attributeArray[i])
# create a map for pokemon. Key is the id (without #) and the value is an array of attributes.
Ipokedex = Iclient.get_or_create_cache("Ipokedex")
INameAndId = Iclient.get_or_create_cache("INameAndId")

#intermediate files pre setting
#generate a json file using dictionaries
def write_to_log(type, fields, fields2):
    timestamp = time.time()
    tp = timestamp
    data_dict = {}
    if fields2 is None:
        data_dict = {"type": type, "fields": fields, "timestamp": timestamp}
    if fields2 is not None:
        data_dict = {"type": type, "fields": fields, "fields2": fields2, "timestamp": timestamp}
    with open("log/" + str(timestamp) + '.json', 'w', encoding='utf-8') as json_file:
        json.dump(data_dict, json_file, ensure_ascii=False, indent=4)
    return timestamp


# read a json log file
def read_log(file_name):
    f = open("log/" + str(file_name), 'r', encoding='utf-8')
    data = json.load(f)
    tp = data['type']
    fields = data['fields']
    timestamp = data['timestamp']
    # print(tp)
    # print(fields)
    # print(timestamp)
    if tp == "update":
        fields2 = data['fields2']
    else:
        fields2 = None
    return tp, fields, fields2, timestamp


# generate a command based on the fields
def parse_command(db, tp, fields, fields2):
    if tp == "insert":
        db.insert_one(fields)
        return "db.insert_one(" + str(fields) + ")"
    if tp == "update":
        db.update_one(fields, {'$set': fields2})
        return "db.update_one(" + str(fields) + "," + "{'$set':" + str(fields2) + "})"
    if tp == "delete":
        #check validation
        #if len(list(db.find({'id': id}))) == 0:
            #print("id not exists")
            #return "id not exists"
        #else:
        db.delete_one(fields)
        return "db.delete_one(" + str(fields) + ")"


def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


class OnMyWatch:
    # Set the directory on watch
    watchDirectory = "."

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(
            event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            # print("Watchdog received modified event - % s." % event.src_path)
            print(event.src_path.split("/")
                  [-2]+"/"+event.src_path.split("/")[-1])


def monitor_host():
    mongo = isOpen("433-34.csse.rose-hulman.edu", 27017)
    ignite = isOpen("433-34.csse.rose-hulman.edu", 10800)
    neo = isOpen("433-34.csse.rose-hulman.edu", 7474)
    p = ""
    if neo:
        p += "neo4j is running | "
    else:
        p += "neo4j is down | "
    if mongo:
        p += "mongo is running | "
    else:
        p += "mongo is down | "
    if ignite:
        p += "ignite is running"
    else:
        p += "ignite is down"
    print(p)
    # change first parameter to allow longer period
    threading.Timer(20, monitor_host).start()
    return mongo





app.config['IMAGE_FOLDER'] = os.path.join('static', 'images')
app.config['CSS_FOLDER'] = os.path.join('static', 'styles')
app.config["SCRIPT_FOLDER"] = os.path.join('static', 'scripts')


@app.route('/favicon.ico', methods=["GET"])
def icon():
    return ''


@app.route('/', methods=["GET"])
@app.route('/index', methods=["GET"])
def indexPage():
    # fail = False
    elep = os.path.join(app.config['IMAGE_FOLDER'], 'elep.png')
    css = os.path.join(app.config['CSS_FOLDER'], 'main.css')
    js = os.path.join(app.config["SCRIPT_FOLDER"], 'main.js')
    return render_template("index.html", logo=elep, style=css, script=js)


@app.route('/login', methods=["GET"])
def login():
    # data = json.loads(request.data.decode(utf-8"))
    username = request.args.get('username')
    password = request.args.get('password')
    print('username: ', username)
    print('password: ', password)
    # TODO: add authentication
    if username == "1":
        return redirect('/main')
    else:
        return "login failed"


@app.route('/main', methods=["GET"])
def mainPage():
    css = os.path.join(app.config['CSS_FOLDER'], 'main.css')
    js = os.path.join(app.config["SCRIPT_FOLDER"], 'main.js')
    print("ismongo333333")
    ismongo = monitor_host()
    print("ismongo1111" )
    if(ismongo):
        print("ismongo2222" )
        Mclient = MongoClient("mongodb://433-34.csse.rose-hulman.edu:27017")
        print("1\n")
        db = Mclient['pokemon']
        testCol = db['pokedex']
        print("2\n")

        path_list = os.listdir('log/')
        print("3\n")

        #path_list.remove('.DS_Store')
        #sort to ensure that all json files are read by time order
        path_list.sort()
        print("4\n")

        #read all files in the folder
        for dir in path_list:
            print("5\n")

            #print(dir)
            with open('log/' + dir) as file:
                tp, fields, fields2, timestamp = read_log(dir)
                cmd = parse_command(testCol,tp,fields,fields2)
                print(cmd)
                #exec(cmd)
                os.remove('log/' + dir)
                res = testCol.find({})
                #testing purposes: print out the data in the database
                print("New Data after restoring a log:")
                for r in res:
                    print(r)
    return render_template("main.html", style=css, script=js)

# detailPage return an array, in the sequence of ["id", "name", "type_1", "type_2", "link", "species", "height", "weight", "abilities", "training_catch_rate", "breeding_gender_male", "breeding_gender_male", "breeding_gender_female", "stats_hp", "stats_attack", "stats_defense", "stats_sp_atk", "stats_sp_def", "stats_speed", "stats_total", "iamgeurl"]


@ app.route('/detail', methods=["GET", "POST"])
def detailPage():
    if (request.method == "GET"):
        id = request.args.get('id')
        output = Ipokedex.get(id)
        if (output != None):
            css = os.path.join(app.config['CSS_FOLDER'], 'main.css')
            js = os.path.join(app.config["SCRIPT_FOLDER"], 'main.js')
            return render_template("detail.html", style=css, script=js, pokemon=output)
        else:
            return redirect('/main')
    else:
        css = os.path.join(app.config['CSS_FOLDER'], 'main.css')
        js = os.path.join(app.config["SCRIPT_FOLDER"], 'main.js')
        return render_template("detail.html", style=css, script=js)


@app.route('/getall', methods=["GET"])
def allPokemon():
    cursor = db.pokedex.find()
    re = {}
    for data in cursor:
        data.pop("_id")
        re[data['id']] = data
    return re

# insert part of data to mongodb and all the data to ignite


@app.route('/Insert/<id>/<name>/<type_1>/<type_2>/<species>/<height>/<weight>/<abilities>/<training_catch_rate>/<training_base_exp>/<training_growth_rate>/<breeding_gender_male>/<breeding_gender_female>/<stats_hp>/<stats_attack>/<stats_defense>/<stats_sp_atk>/<stats_sp_def>/<stats_speed>/<stats_total>/<img>', methods=["GET", "POST"])
# @app.route('/Insert/<id>/<name>', methods=["GET", "POST"])
@app.route('/insert', methods=["POST"])
def insertPokemon(id=0, name="-", type_1="-", type_2="-", species="-", height="0", weight="0", abilities="-", training_catch_rate="0", training_base_exp="0", training_growth_rate="0", breeding_gender_male="0", breeding_gender_female="0", stats_hp="0", stats_attack="0", stats_defense="0", stats_sp_atk="0", stats_sp_def="0", stats_speed="0", stats_total="0", img="-"):
    if request.method == "POST":
        data = request.data
        print(data)
        return data
    if request.method == "GET":
        # Ignite insert
        if Ipokedex.get(id) != None or len(list(db.pokedex.find({'id': id}))):
            print('already exists')
            return 'Insert failed, id already exists'
        else:
            INameAndId.put(name, id)
            Ipokedex.put(id, [name, type_1, type_2, species, height, weight, abilities, training_catch_rate, training_base_exp, training_growth_rate,
                              breeding_gender_male, breeding_gender_female, stats_hp, stats_attack, stats_defense, stats_sp_atk, stats_sp_def, stats_speed, stats_total, img])

            # Mongodb insert
            data = {
                'id': id,
                'name-form': name,
                'type_1': type_1,
                'type_2': type_2,
                'data_species': species,
                'img': img
            }
            db.pokedex.insert_one(data)
            # log = "db.pokedex.insert_one("+str(data)+")"
            # TODO: add log to log file.
            return "insertion added to logs"
            # return json.loads(json_util.dumps(data))
    else:
        return ''

# search for the search page, use mongodb to search


@ app.route('/HomeSearch/<InfoType>/<info>', methods=["GET"])
# if the result is not found, it will return "No such result". If the result is found, it will return the result of the find_one function.
def Search(InfoType, info):
    if InfoType == "type":
        output = db.pokedex.find({"$or": [{"type_1": info}, {"type_2": info}]})
    else:
        output = db.pokedex.find({InfoType: info})
    if (output == None):
        return "No such result. Please search again"
    else:
        re = {}
        for data in output:
            data.pop("_id")
            re[data['id']] = data
        return re


# mongodb and ignite update


@ app.route('/Update/<id>/<name>/<type_1>', methods=["GET", "POST", "PATCH"])
def Update(id="-", name="-", type_1="-", type_2="-", link="-", species="-", height="0", weight="0", abilities="0", training_catch_rate="0", training_base_exp="0", training_growth_rate="0", breeding_gender_male="0", breeding_gender_female="0", stats_hp="0", stats_attack="0", stats_defense="0", stats_sp_atk="0", stats_sp_def="0", stats_speed="0", stats_total="0", img="-"):
    # Mongodb Update
    if (request.method == "GET"):
        if Ipokedex.get(id) == None or len(list(db.pokedex.find({'id': id}))) == 0:
            print("id not exists")
            return "id not exists"
        else:
            tmp = Ipokedex.get(id)[0]
            if INameAndId.get(tmp) == None:
                print("id not exists")
                return "id not exists"
            else:
                db.pokedex.update_one(
                    {"id": id},
                    {"$set": {"name-form": name,
                              "type_1": type_1,
                              "type_2": type_2,
                              "data_species": species,
                              "img": img}
                     }
                )
                # ignite update
                INameAndId.remove_key(tmp)
                Ipokedex.put(id, [name, type_1, type_2, link, species, height, weight, abilities, training_catch_rate, training_base_exp, training_growth_rate,
                                  breeding_gender_male, breeding_gender_female, stats_hp, stats_attack, stats_defense, stats_sp_atk, stats_sp_def, stats_speed, stats_total, img])
                INameAndId.put(name, id)
                print(INameAndId.get(name))
                cursor = db.pokedex.find({'id': id})
                x = {}
                for i in cursor:
                    x.update(i)
                print(x)
                print(Ipokedex.get(id))
                print(INameAndId.get(name))
                return "update succeed"


@ app.route('/Delete/<id>', methods=["DELETE"])
def Del(id=''):
    if request.method == "DELETE":
        print(Ipokedex.get(id))
        if (id == ""):
            return 'id can not be empty'
        else:
            if Ipokedex.get(id) == None:
                print("id not exists")
                    #return "id not exists"
            else:
                name = Ipokedex.get(id)[0]
                print(name)
                if INameAndId.get(name) == None:
                    print("id not exists")
                    #return "id not exists"
                else:
                    # Ignite delete
                    Ipokedex.remove_key(id)
                    INameAndId.remove_key(name)
            ismongo = monitor_host()
            if (not ismongo):
                #write to json, create fields
                write_to_log("delete", {"id":id},None)
                print("write!!!\n")
            if(ismongo):
                Mclient = MongoClient("mongodb://433-34.csse.rose-hulman.edu:27017")
                print("1\n")
                db = Mclient['pokemon']
                testCol = db['pokedex']
                print("2\n")

                path_list = os.listdir('log/')
                print("3\n")

                #path_list.remove('.DS_Store')
                #sort to ensure that all json files are read by time order
                path_list.sort()
                print("4\n")

                #read all files in the folder
                for dir in path_list:
                    print("5\n")

                    #print(dir)
                    with open('log/' + dir) as file:
                        tp, fields, fields2, timestamp = read_log(dir)
                        cmd = parse_command(testCol,tp,fields,fields2)
                        print(cmd)
                        #exec(cmd)
                        os.remove('log/' + dir)
                        res = testCol.find({})
                        #testing purposes: print out the data in the database
                        print("New Data after restoring a log:")
                        for r in res:
                            print(r)




# neo4j detail page next evo check


@app.route('/detail/NEXTEVO/<id>', methods=["GET"])
def getNextEvo(id):
    # get name
    evoNameResult = Nclient.run("MATCH ((n)-[]->(m)) "
                                "WHERE n.id = $id "
                                "return m.name", id=id)
    evoNameArray = []
    for e in evoNameResult:
        evoNameArray.append(e["m.name"])
    # get id
    evoIdResult = Nclient.run("MATCH ((n)-[]->(m)) "
                              "WHERE n.id = $id "
                              "return m.id", id=id)
    evoIdArray = []
    for e in evoIdResult:
        evoIdArray.append(e["m.id"])
    # get img link string
    evoImgResult = Nclient.run("MATCH ((n)-[]->(m)) "
                               "WHERE n.id = $id "
                               "return m.img", id=id)
    evoImgArray = []
    for e in evoImgResult:
        evoImgArray.append(e["m.img"])
    dict = {}
    dict["name"] = evoNameArray
    dict["id"] = evoIdArray
    dict["img"] = evoImgArray
    # print(dict)
    return dict

# get previous Evo


@app.route('/detail/PREVEVO/<id>', methods=["GET"])
def getPrevEvo(id):
    # get name
    evoNameResult = Nclient.run("MATCH ((n)-[]->(m)) "
                                "WHERE m.id = $id "
                                "return n.name", id=id)
    evoNameArray = []
    for e in evoNameResult:
        evoNameArray.append(e["n.name"])
    # get id
    evoIdResult = Nclient.run("MATCH ((n)-[]->(m)) "
                              "WHERE m.id = $id "
                              "return n.id", id=id)
    evoIdArray = []
    for e in evoIdResult:
        evoIdArray.append(e["n.id"])
    # get img link string
    evoImgResult = Nclient.run("MATCH ((n)-[]->(m)) "
                               "WHERE m.id = $id "
                               "return n.img", id=id)
    evoImgArray = []
    for e in evoImgResult:
        evoImgArray.append(e["n.img"])
    dict = {}
    dict["name"] = evoNameArray
    dict["id"] = evoIdArray
    dict["img"] = evoImgArray
   # print(dict)
    return dict

# Function haven't been routed yet: (neo4j create node , relation and delete node with repetition check )


def createNode(name, id, img):
    # check if the node exist:
    oldResult = Nclient.run("MATCH (p:Pokemon { id : $id }) "
                            "return p.id", id=id)
    for e in oldResult:
        if (e["p.id"] != None):
            print(oldResult)
            print("This node already exist")
            return "This node already exist"
    else:
        result = Nclient.run("CREATE (p:Pokemon { name: $name , id : $id, img : $img }) "
                             "RETURN p", name=name, id=id, img=img)
        print(result)
        return "Node created!"


def addEVO(lowId, highId):
    # check if the relationship exist:
    oldResult = Nclient.run("MATCH (low:Pokemon { id : $lowId }) "
                            "MATCH (high:Pokemon {id : $highId }) "
                            "WHERE (low)-[]->(high) "
                            "RETURN low.id", lowId=lowId, highId=highId)
    for e in oldResult:
        if (e["low.id"] != None):
            print("Relation already exists")
            return "Relation already exists"
    else:
        result = Nclient.run("MATCH (low:Pokemon { id : $lowId }) "
                             "MATCH (high:Pokemon {id : $highId }) "
                             "CREATE (low)-[:evolution]->(high)", lowId=lowId, highId=highId)
        print(result)
        print("Relation created")
        return "Relation created"


def deleteNode(id):
    result = Nclient.run("MATCH (p:Pokemon {id : $id}) "
                         "DETACH DELETE p", id=id)
    print(result)
    return "delete success"


if __name__ == "__main__":
    watch = OnMyWatch()
    monitor = threading.Thread(target=monitor_host, args=())
    watch1 = threading.Thread(target = watch.run, args = ())
    monitor.start()
    watch1.start()

    app.run(debug=True)

    
    
