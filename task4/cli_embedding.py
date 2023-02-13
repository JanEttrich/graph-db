import cmd
from parser import *
from neo4j import GraphDatabase
import argparse

uri = "bolt://localhost:7689"

class Neo4jShell(cmd.Cmd):
    intro = 'Welcome to Neo4j shell. Type help or ? to list commands.\n'
    prompt = 'neo4j>'
    logged_in = False
    parser = argparse.ArgumentParser(description="Process embed params")
    parser.add_argument('-time', default=50, type=int, choices=range(50,10000,50))
    parser.add_argument('-jtypes', default=range(1,8), type=list)
    parser.add_argument('-strat', default='md', type=str, choices=['md', 'ld'])
    parser.add_argument('-limit', default=100, type=int)

    def do_login(self, arg):
        'Creates connection to and authenticates on database:   login user pass'
        args = arg.split()
        if len(args) == 2:
            self.driver = GraphDatabase.driver(uri, auth=(args[0], args[1]))
            # verify connectivity, as connection is only created when processing the first query
            self.driver.verify_connectivity()
            self.logged_in = True
            print('Successfully connected to database.')
        else:
            print('Username or password not provided!')

    def do_embed(self, args):
        '''Creates embedding of loops and visualizes result. Configurable params are time, jtypes, strategy and limit: 
        embed -time 50 -jtypes 1234567 -strat ld -limit 100
        '''
        if not self.logged_in:
            print('Not logged in to database, login first!')
            return
        params = self.parser.parse_args(args.split())
        ########################################################
        # Zugriff auf params
        time = params.time
        # Hier sollte embedding funktion mit params aufgerufen werden und png erzeugt werden
        ########################################################
        return

    def do_logout(self, arg):
        'Closes connection to database'
        self.driver.close()
        self.logged_in = False
        print('Connection to database closed.')
     
    def do_quit(self, arg):
        'Quits execution'
        return True

if __name__ == '__main__':
    Neo4jShell().cmdloop()