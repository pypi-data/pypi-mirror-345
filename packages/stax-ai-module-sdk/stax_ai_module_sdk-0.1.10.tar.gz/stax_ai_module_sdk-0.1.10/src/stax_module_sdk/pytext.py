# See LICENSE.md file in project root directory
import re
from typing import Dict
from .helpers import getValueByKey, getConfigByLabel

def renderPyText(doc: Dict, body: str):
    out = body
    
    # Link to document
    link = "https://my.stax.ai/stack/" + (str(doc["stack"]) if doc["stack"] else "unclassified") + "/document/" + str(doc["_id"])
    
    # Field value extractor
    def field(key):
        return getValueByKey(doc["metadata"], key)
    
    for m in re.finditer(r"\{(.*?)\}", body, re.MULTILINE | re.DOTALL):
        for g in range(0, len(m.groups())):
            pattern = m.group(g)
            try:
                value = str(eval(pattern[1:-1]))
            except Exception as e:
                raise Exception("Failed to evaluate expression: " + pattern + " - " + str(e))
                
            out = out.replace(pattern, value)
    
    return out