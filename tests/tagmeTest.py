from common.component.linker.tagme import TagMe

if __name__ == "__main__":
    linker = TagMe('./../data/LC-QuAD/tagmeNEDLogs', dataset_path='./../data/LC-QuAD/linked_3200.json')

    print linker.link_entities('Which comic characters are painted by Bill Finger?')
