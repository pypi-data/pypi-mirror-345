
import os
import json






def new_recipe(name):
    os.makedirs('.awcc/recipes')
    with open(f'.awcc/recipes/{name}.json', 'w') as f:
        json.dump({
            'flags': [],
            'needs': []
        }, f)
def recipe_add(name, hashes):
    with open(f'.awcc/recipes/{name}.json','r') as f:
        obj = json.load(f)
    obj['needs'].extend(hashes)
    with open(f'.awcc/recipes/{name}.json', 'w') as f:
        json.dump(obj, f)

def recipe_set_flags(name, hashes):
    pass

