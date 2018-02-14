from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.parser.earl import EARL
from common.component.linker.goldLinker import GoldLinker
from common.utility.stats import Stats
from common.utility.utils import Utils
import argparse
from tqdm import tqdm
import logging


def compare(list1, list2):
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


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    Utils.setup_logging()

    parser = argparse.ArgumentParser(description='Evaluate linker')
    parser.add_argument("--path", help="input dataset", default="../../data/LC-QuAD/linked.json", dest="ds_path")
    parser.add_argument("--linker", help="linker output path", default="../../data/LC-QuAD/EARL/output_nltk.json",
                        dest="linker_path")
    args = parser.parse_args()

    stats = Stats()

    ds = LC_Qaud_Linked(args.ds_path)
    ds.load()
    ds.parse()

    goldLinker = GoldLinker()
    earl = EARL(args.linker_path)

    for qapair in tqdm(ds.qapairs):
        e1, r1 = goldLinker.do(qapair)
        e2, r2 = earl.do(qapair, force_gold=False, top=100)
        if len(e2) == 0:
            stats.inc("earl_no_entity")
        if len(r2) == 0:
            stats.inc("earl_no_relation")

        if len(e2) == 0 and len(r2) == 0:
            stats.inc("earl_no")

        if len(e1) == len(e2):
            stats.inc("len_entity")

        if len(r1) == len(r2):
            stats.inc("len_relation")

        if len(e1) == len(e2) and len(r1) == len(r2):
            stats.inc("len_both")

        e = compare(e1, e2)
        r = compare(r1, r2)
        if not e:
            stats.inc("matched_entity")
        if not r:
            stats.inc("matched_relation")
        if not e and not r:
            stats.inc("matched_both")

        if len(e1) == len(e2) and len(r1) == len(r2) and not e and not r:
            stats.inc("matched_both_and_len")

        stats.inc("total")

    print
    print stats
