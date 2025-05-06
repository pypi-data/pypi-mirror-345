# See LICENSE.md file in project root directory
import json
from retry_requests import retry, RSession
from .helpers import getConfigByLabel

class Stax:
    def __init__(self, module_id:str, module_key:str, team_id:str=None, document:str=None, api_url:str="https://api.stax.ai"):
        # Construct API header
        self.headers = {
            'Module': module_id,
            'Authorization': 'Bearer ' + module_key,
            'Team': team_id
        }

        self.document_id = document
        self.api_url = api_url

        # Create retry requests session
        self.sess = retry(RSession(timeout=30), retries=3)


    def getDocument(self, presigned:bool=True, document:str=None):
        '''
        Get document metadata.
        '''
        document_id = document if document else self.document_id
        if not document_id:
            raise Exception("No document ID specified")

        # Construct endpoint
        endpoint = '/document/get?docId=' + document_id
        if presigned:
            endpoint += '&presigned=true'

        res = self.get(endpoint)
        return res['doc']


    def downloadDocument(self, document:str=None, path:str=None):
        '''
        Download raw document.
        If path is not specified, this function returns the binary data.
        '''
        document_id = document if document else self.document_id
        if not document_id:
            raise Exception("No document ID specified")

        res = self.get('/document/download?docId=' + document_id, raw=True)
        if path is None:
            return res
        
        with open(path, 'wb') as f:
            f.write(res.content)


    def downloadPage(self, key:str=None, document:str=None, path:str=None):
        '''
        Download a single document page - make sure you pass the page key.
        If path is not specified, this function returns the binary data.
        '''
        document_id = document if document else self.document_id
        if not key:
            raise Exception("Missing page key")
        if not document_id:
            raise Exception("No document ID specified")

        res = self.get('/document/downloadPage?docId=' + document_id + '&pagePath=' + key, raw=True)
        if path is None:
            return res
        
        with open(path, 'wb') as f:
            f.write(res.content)

    
    def updateDocument(self, diff={}, document:str=None, args={}):
        '''
        Update a document with a provided diff of changes.
        '''
        document_id = document if document else self.document_id
        if not document_id:
            raise Exception("No document ID specified")
        
        self.post('/document/update', {
            "docId": document_id,
            "docDiff": diff,
            **args
        }, raw=True)


    def downloadConfigFile(self, config:'list[dict]'=[], label:str=None, path:str=None):
        '''
        Download config file by label
        '''
        if not label:
            raise Exception("Missing configuration label")

        src = getConfigByLabel(config, label)
        if not src:
            raise Exception("Configuration parameter does not exist.")

        # TODO - download


    def get(self, endpoint:str, raw:bool=False):
        '''
        Make a GET request from the Stax.ai API.
        Set 'raw' to True to return raw API response.
        '''
        res = self.sess.get(self.api_url + endpoint, headers=self.headers)
        return res if raw else self._handle_response_(res)


    def post(self, endpoint:str, data={}, raw:bool=False):
        '''
        Make a POST request to the Stax.ai API with provided JSON data.
        Set 'raw' to True to return raw API response.
        '''
        res = self.sess.post(self.api_url + endpoint, json=data, headers=self.headers)
        return res if raw else self._handle_response_(res)


    def _handle_response_(self, res):
        if res.status_code != 200:
            raise Exception("Failed to communicate with Stax.ai API")

        data = res.json()
        if not data['success']:
            try:
                err = json.dumps(data)
            except Exception as e:
                raise Exception("API Parse Error:" + str(e) + "\n" + res.content.decode('utf-8'))
            
            raise Exception("API Error:" + err)
        
        return data
