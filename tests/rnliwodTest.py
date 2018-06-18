from common.component.linker.rnliwod import RNLIWOD

if __name__ == "__main__":
    linker = RNLIWOD('./../data/LC-QuAD/relnliodLogs', dataset_path='./../data/LC-QuAD/linked_3200.json')

    print linker.link_relations('Which comic characters are painted by Bill Finger?')
