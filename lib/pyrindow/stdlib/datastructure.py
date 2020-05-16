# datastructure

def DictReplaceRecursive(distination, extract):
    """replaces to merge 'extract' into 'distination'"""
    for key in extract:
        if key in distination:
            if isinstance(distination[key], dict) and isinstance(extract[key], dict):
                DictReplaceRecursive(distination[key], extract[key])
            elif isinstance(distination[key], list) and isinstance(extract[key], list):
            	distination[key].extend(extract[key])
            elif distination[key] == extract[key]:
                pass # same leaf value
            else:
            	distination[key] = extract[key]
        else:
            distination[key] = extract[key]
    return distination
