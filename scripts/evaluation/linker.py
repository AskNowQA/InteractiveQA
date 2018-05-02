from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.parser.earl import EARL
from common.component.linker.goldLinker import GoldLinker
from common.utility.stats import Stats
from common.utility.utils import Utils
import argparse
from tqdm import tqdm
import logging


class LinkerEvaluator:
    def __init__(self, gold_linker):
        self.gold_linker = gold_linker

    def __compare_list(self, list1, list2):
        miss_match = False
        for item in list1:
            target_uri = item.uris[0]
            found = False
            for e2_item in list2:
                if target_uri in e2_item.uris:
                    found = True
                    break
            if not found:
                miss_match = True
                break
        return miss_match

    def compare(self, qapair, e2, r2):
        e1, r1 = self.gold_linker.do(qapair)
        # double_relation = len(r1) > len(set([p.raw_uri for u in r1 for p in u.uris]))
        if len(e2) == 0:
            return '-no_entity'
        if len(r2) == 0:
            return '-no_relation'

        if len(e2) == 0 and len(r2) == 0:
            return '-no_input'

        if len(e1) != len(e2):
            return '-len_entity'

        if len(r1) != len(r2):
            return '-len_relation'

        e = self.__compare_list(e1, e2)
        r = self.__compare_list(r1, r2)
        if e:
            return '-miss_matched_entity'
        if r:
            return '-miss_matched_relation'

        return "+matched"


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()

    parser = argparse.ArgumentParser(description='Evaluate linker')
    parser.add_argument('--path', help='input dataset', default='../../data/LC-QuAD/linked2843.json', dest='ds_path')
    parser.add_argument('--linker', help='linker output path', default='../../data/LC-QuAD/EARL/output_gold.json',
                        dest='linker_path')
    args = parser.parse_args()

    stats = Stats()
    evaluator = LinkerEvaluator(GoldLinker())
    ds = LC_Qaud_Linked(args.ds_path)
    earl = EARL(args.linker_path)

    for qapair in tqdm(ds.qapairs):
        e2, r2 = earl.do(qapair, force_gold=False, top=100)
        stats.inc(evaluator.compare(qapair, e2, r2))
        stats.inc('total')

    print
    print stats
