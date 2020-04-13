# Interactive QA (IQA)
IQA is an interactive framework to construct SPARQL Query from a natural language question.

While IQA interactive schema is generally able be implemented using an arbitrary semantic question answering pipeline, this repository provides a concrete realization of IQA using following external components:
1. [MDP-Parser](https://github.com/AskNowQA/DeepShallowParsingQA): that acts as the shallow parser to extract the mentions of entity and relations from the input question.
1. [EARL](https://github.com/AskNowQA/EARL) is a entity/relation linker that provides a list of candidate linked item for each entity/relation mention from the previous step. A demo version is available at http://earldemo.sda.tech/ .
1. [SQG](https://github.com/AskNowQA/SQG) is a query building component that produces a list of candidate queries given the candidate linked items and the input question. It alo has a ranking mechanism to arrange the candidate queries in respect to their structural similarity to the input question.


## Getting Started
* Please install [Python 3.7](https://www.python.org/downloads/) and the required packages as listed in [here](https://github.com/AskNowQA/InteractiveQA/blob/master/requirements.txt).
* Please follow the documentation of the aforementioned components to get them running.   
* Update the config.py to point the web service of the components.
* run `python scripts/service/backend.py --base_path .` .
* run `python UI/app.py --base_path . --port 5001` .
* Now you can navigate to http://localhost:5001/ and check out the web based user interface. 



## Data
Please find all required data at: tiny.cc/IQAData

## License
This program is subject to the terms of the General Public License (GPL), Version 3.0. 
