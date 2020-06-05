import csv
import sqlite3
import json
import requests

from tqdm import tqdm

# DATA MODEL
#
# +--------+       +--------+       +-------------+
# | Region |-1---*-| County |-1---*-| City        |
# +--------+       +--------+       +-------------+
# | code   |       | code   |       | code_insee  |
# | name   |       | name   |       | code_postal |
# +--------+       +--------+       | name        |
#                                   | population  |
#                                   | area        |
#                                   +-------------+

DB_NAME = 'truc.db'

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    region_table = """CREATE TABLE IF NOT EXISTS Region (
        code INTEGER PRIMARY KEY,
	    name TEXT NOT NULL);"""
    county_table = """CREATE TABLE IF NOT EXISTS County (
        code TEXT PRIMARY KEY,
	    name TEXT NOT NULL);"""
    city_table = """CREATE TABLE IF NOT EXISTS City (
        code_insee TEXT PRIMARY KEY,
        code_postal INTEGER NOT NULL,
	    name TEXT NOT NULL,
        population FLOAT NOT NULL,
        area FLOAT NOT NULL);"""
    conn = connect_db()
    conn.execute(region_table)
    conn.execute(county_table)
    conn.execute(city_table)
    conn.close()

def fill_up_db():
    conn = connect_db()
    csv_data = csv.reader(open('data/original_data.csv'), delimiter=';')
    next(csv_data) # skip first line (columns titles)
    for row in tqdm(csv_data, total=36742):
        region_code, region_name = row[-1], row[4]
        region_req = '''INSERT INTO Region (code, name) VALUES ({}, "{}")'''.format(region_code, region_name)
        try:
            conn.execute(region_req)
        except Exception as e:
            pass
        county_code, county_name = row[-2], row[3]
        county_req = 'INSERT INTO County (code, name) VALUES ("{}", "{}")'.format(county_code, county_name)
        try:
            conn.execute(county_req)
        except Exception as e:
            pass
        code_insee, code_postal, city_name, population, area = row[0], row[1], row[2], row[8], row[7]
        city_req = 'INSERT INTO City (code_insee, code_postal, name, population, area) VALUES ("{}", {}, "{}", {}, {})'.format(code_insee, code_postal, city_name, population, area)
        conn.execute(city_req)
        conn.commit()
    conn.close()

def get_data(cursor):
    reps = cursor.fetchall()
    if not reps: return list()
    res = list()
    for row in reps:
        data = dict()
        for k, a in zip(row.keys(), list(row)):
            data[k] = a
        res.append(data)
    return res

def get_county_codes(region_code):
    data = dict()
    with open('data/reg_to_dep.json') as jf:
        data = json.load(jf)
    return data.get(region_code, list())

def get_coordinates(region):
    rep = requests.get('https://nominatim.openstreetmap.org/search?country=France&state={}&format=json'.format(region))
    return rep.json()

def get_regions(conn, limit, offset=0):
    cursor = conn.execute('''SELECT * FROM Region LIMIT {} OFFSET {}'''.format(limit, offset))
    regions = get_data(cursor)
    res = list()
    for r in regions:
        county_codes = str(get_county_codes(str(r['code']))).replace('[','(').replace(']',')')
        cursor2 = conn.execute('''SELECT SUM(population) AS POPULATION, SUM(area) AS AREA, SUBSTR(code_insee, 0, 3) AS DEP FROM City WHERE DEP IN {}'''.format(county_codes))
        tmp_res = get_data(cursor2)
        coordinates = get_coordinates(r['name'])
        if len(coordinates) < 1: coordinates = [{'lat':-1,'lon':-1}]
        res.append({
            'code': r['code'],
            'name': r['name'],
            'totalPopulation': tmp_res[0]['POPULATION'],
            'totalArea': tmp_res[0]['AREA'],
            'lat': coordinates[0]['lat'],
            'lon': coordinates[0]['lon']
        })
    return res
