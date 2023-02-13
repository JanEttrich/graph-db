import cmd
from parser import *
from neo4j import GraphDatabase
import argparse
from embeddings import *
import getpass

uri = "bolt://localhost:7689"

class Neo4jShell(cmd.Cmd):
    def __init__(self, driver):
        super().__init__()
        self.intro = 'Welcome to Neo4j shell. Type help or ? to list commands.\n'
        self.prompt = 'neo4j>'
        self.driver = driver
        self.parser = argparse.ArgumentParser(description="Process embed params")
        self.parser.add_argument('-time', default=50, type=int, choices=range(50,10000,50))
        self.parser.add_argument('-jtypes', default=range(1,8), type=list)
        self.parser.add_argument('-strat', default='md', type=str, choices=['md', 'ld'])
        self.parser.add_argument('-limit', default=100, type=int)

    def do_embed(self, args):
        '''Creates embedding of loops and visualizes result. Configurable params are time, jtypes, strategy and limit: 
        embed -time 50 -jtypes 1234567 -strat ld -limit 100
        '''
        params = self.parser.parse_args(args.split())
        print("Generating embeddings...")
        generateEmbedding(params.time, params.jtypes, params.strat ,params.limit, self.driver)
        print("Embeddings generated!")
        return
     
    def do_query(self, args):
        '''Runs a cypher query on database: query MATCH (e:ELoop) RETURN e.id, e.time, e.jtypes LIMIT 5'''
        res = run_query(args, {}, self.driver)
        print(res)
    
    def do_quit(self, arg):
        'Quits execution'
        return True

if __name__ == '__main__':
    print('Logging into database...')
    user = input('Username: ')
    pw = getpass.getpass('Password: ')
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    # verify connectivity, as connection is only created when processing the first query
    driver.verify_connectivity()
    Neo4jShell(driver).cmdloop()