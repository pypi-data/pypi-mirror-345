import argparse
import queue
from dataclasses import dataclass
import datetime
from typing import Tuple
"""
Usage: python -m colbert.scripts.shirttt_utils --input <ranking files from each shard> --output <file to write> --topn 50 

"""

@dataclass(order=True)
class PrioritizedItem:
    priority: float  # -1 * score
    item: Tuple[int, list] # index, line from output file

class ResultData:
    def __init__(self, qry_list):
        self.cur = 0
        self.ranked_list = qry_list

def create_item(filename, index):
    with open(filename) as fin:
        for i, line in enumerate(fin):
            split = line.split()
            score = float(split[4])*-1
            qid = split[0]
            pitem = PrioritizedItem(score, (index, split))
            yield qid, pitem

def print_message(*s, condition=True, pad=False):
    s = ' '.join([str(x) for x in s])
    msg = "[{}] {}".format(datetime.datetime.now().strftime("%b %d, %H:%M:%S.%f"), s)

    if condition:
        msg = msg if not pad else f'\n{msg}\n'
        print(msg, flush=True)

def combine_shards(args):
    results = {}
    print_message('Begin merge')
    for i, fn in enumerate(args.input):
        query_list = []
        query_id = None
        for qid, item in create_item(fn, i):
            if qid != query_id:
                if query_list:
                    if not qid in results:
                        results[qid] = [None]*len(args.input)
                    results[qid][i] = ResultData(query_list)
                query_id = qid
                query_list = []
            if args.pershard < 0 or len(query_list) < args.pershard:
                query_list.append(item)
        if query_list:
            if not qid in results:
                results[qid] = [None]*len(args.input)
            results[qid][i] = ResultData(query_list)

    print_message('Read data')

    with open(args.output, 'w') as fout:
        for qid, data in results.items():
            pq = queue.PriorityQueue(len(args.input))

            for q_results in data:
                if q_results.ranked_list and q_results.cur < len(q_results.ranked_list):
                    pq.put(q_results.ranked_list[q_results.cur])
                    q_results.cur += 1
            for i in range(args.topn):
                if not pq.empty():
                    # Get the next document
                    top_ranked = pq.get()
                    doc_info = top_ranked.item[1]
                    doc_info[3] = str(i+1)
                    print(' '.join(doc_info), file=fout)
                    #Replace the document from the correct shard
                    idx = top_ranked.item[0]
                    if data[idx] and data[idx].cur < len(data[idx].ranked_list):
                        pq.put(data[idx].ranked_list[data[idx].cur])
                        data[idx].cur += 1
                else:
                    break

    print_message('All done')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='trec files', required=True, nargs='+')
    parser.add_argument('--output', required=True)
    parser.add_argument('--topn', help='number of documents to rank', type=int, required=True)
    parser.add_argument('--pershard', help='number of documents to rank from a shard', type=int, default=-1)

    combine_shards(parser.parse_args())
