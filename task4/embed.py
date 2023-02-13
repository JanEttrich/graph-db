import argparse
from embeddings import generateEmbedding

parser = argparse.ArgumentParser()
parser.add_argument('-time', type=int, default=50,
                    help="Timestep for which the embedding is generated", choices=range(50,10000,50))
parser.add_argument('-jtypes', type=str, default="str(list(range(1, 8)))",
                    help="Specifies the junction types to be included")
parser.add_argument('-strat', type=str, default='md',
                    help="The strategy to use, can be 'md' (most dominant) or 'ld' (least dominant)", choices=['md', 'ld'])
parser.add_argument('-limit', default=10**8, type=int,
                    help="Limit the number of loops included in the analysis, by default all loops will be included")

if __name__ == '__main__':
    params = parser.parse_args()
    jtypes = [int(x) for x in params.jtypes.strip('[]').split(",")]

    print("Generating embeddings...")
    generateEmbedding(params.time, jtypes, params.strat ,params.limit)
    print("Embeddings generated!")
