import requests
from enum import Enum
import tempfile
import base64
import json
from sirio.utility import *
import contextlib
import os


class TypeValue(Enum):
    string = 1
    date = 2
    numeric = 3

class Object:
    id = None
    extension = ""
    name = ""
    key = ""
    base64 = ""
    partIndex = 0
    params = []
    file = None
    fileName = None
    multipartMode = True
    contentType = ''
    def __init__(self, key, name, id=None, extension='', params: list = [], partIndex=-1, multipartMode=True ):
        self.id = id
        self.name = name
        self.extension = extension
        self.key = key
        self.params = params
        self.partIndex = partIndex
        self.multipartMode = multipartMode

    def createByBase64(self, base64_string):
        """
        Crea file a partire da un bytearray codificato in Base64.

        :param base64_string: Stringa contenente i dati codificati in Base64.
        """
        file_data = base64.b64decode(base64_string)
        fileName = f"{self.name}.{self.extension}"
        temp_file_path = os.path.join(tempfile.gettempdir(), fileName)
        with open(temp_file_path, 'wb') as temp_file:
            #Converte la stringa base64 in byteArray
            temp_file.write(file_data)

        self.fileName = temp_file.name
        self.contentType = getContentTypeFromName(fileName)
        


    def createByStream(self, file_stream):
        """
        Crea file a partire da uno stream.

        :param file_stream: Stream del file.
        """
        # Crea un file temporaneo con il nome e l'estensione specificati
        fileName = f"{self.name}.{self.extension}"
        temp_file_path = os.path.join(tempfile.gettempdir(), fileName)

        # Scrivi il contenuto dello stream nel file temporaneo
        with open(temp_file_path, 'wb') as temp_file:
            file_stream.seek(0)  # Assicura che lo stream sia alla posizione iniziale
            temp_file.write(file_stream.read())

        self.fileName = temp_file.name
        self.contentType = getContentTypeFromName(fileName)

    def createByJson(self, str_son):
        """
        Crea file a partire da un json.

        :param str_son: json del file.
        """
        ENCODING = 'utf-8'
        self.extension = 'json'
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8') as json_file:
            json.dump(str_son, json_file, ensure_ascii=False, indent=4)
            json_file.flush()  
        self.fileName = json_file.name
        self.contentType = 'application/json'
        """
        if not self.multipartMode:
            with open(json_file.name, 'rb') as json_file:
                encoded = base64.b64encode(json_file.read())
            self.base64 = encoded.decode(ENCODING)
        else:
            with open(json_file.name, 'rb') as json_file:
                self.file = json_file
        """
class BusinessObject:
    jsonComplete = {}
    businessObject = {}
    businessKey =  ""
    subject = ""
    description = ""
    owner = ""
    internalBusinessKey = ""
    priority = ""
    urlGetBO = ""
    urlComplete = ""
    objects = []
    STATISTICS = 'statistics'
    GENAI = 'sirio-gen-ai'
    REF = 'sirio-ref'
    OUTPUT_TASK = 'outputTask'
    def __init__(self, businessKey: str, urlGetBO: str = None, urlComplete: str = None):
        self.jsonComplete = {"businessKey": businessKey}
        self.objects = []
        self.data = {}
        self.urlGetBO = urlGetBO
        self.urlComplete = urlComplete
        if self.urlGetBO is not None:
            try:
                response = requests.get(urlGetBO.replace('{businessKey}', businessKey))
                if response.status_code == 200:
                    self.businessObject = response.json()
                    self.description = self.businessObject['description']
                    self.subject = self.businessObject['subject']
                    self.owner = self.businessObject['owner']
                    self.priority = self.businessObject['priority']
                    self.internalBusinessKey = self.businessObject['internalBusinessKey']
                else:
                    self = None
            except Exception as ex:
                self.businessObject = self.jsonComplete
                raise Exception('Eccezione nel recupero del businessObject: {}'.format(ex))
    
    def getListIdInBind(self, bind:str):
        keys_list = []
        if existsJsonPath(self.businessObject,['data',bind]):# 'data' in self.businessObject['data'] and bind in self.businessObject['data'] and id in self.businessObject['data'][bind] and 'value' in self.businessObject['data'][bind][id] and 'value' in self.businessObject['data'][bind][id]['value']:
                keys_list = list(self.businessObject['data'][bind].keys())
        return keys_list    

    def getValue(self, bind:str, id:str):
        valReturn = None
        try:
            if existsJsonPath(self.businessObject,['data',bind, id, 'value', 'value']):# 'data' in self.businessObject['data'] and bind in self.businessObject['data'] and id in self.businessObject['data'][bind] and 'value' in self.businessObject['data'][bind][id] and 'value' in self.businessObject['data'][bind][id]['value']:
                valReturn = self.businessObject['data'][bind][id]['value']['value']
        except Exception as ex:
            print("Eccezione su getValue [{}][{}] - {}".format(bind, id, ex))
        return valReturn
    
    def setValue(self, bind: str, id: str, value, typeValue=TypeValue.string, descriprion=''):
        if 'data' not in self.jsonComplete:
            self.jsonComplete['data'] = {}
        if bind not in self.jsonComplete['data']:
            self.jsonComplete['data'][bind] = {}
        if id not in self.jsonComplete['data'][bind]:
            self.jsonComplete['data'][bind][id] =  {"dataType": typeValue.name,  "description": descriprion,   "value": {"value": value }, "extendedValue": [] }
        elif self.jsonComplete['data'][bind][id]['value']['value'] != value:
            self.jsonComplete['data'][bind][id]['value']['value'] = value

        if 'data' not in self.businessObject:
            self.businessObject['data'] = {}
        if bind not in self.businessObject['data']:
            self.businessObject['data'][bind] = {}
        if id not in self.businessObject['data'][bind]:
            self.businessObject['data'][bind][id] = {"dataType": typeValue.name,  "description": descriprion,   "value": {"value": value }, "extendedValue": [] }
        elif self.businessObject['data'][bind][id]['value']['value'] != value:
            self.businessObject['data'][bind][id]['value']['value'] = value

    def setReference(self, bind: str, id: str, value):
        self.setExtendedValue(bind=bind, id=id, key=self.REF, value=value)

    def setPropostaAI(self, bind: str, id: str, value):
        self.setExtendedValue(bind=bind, id=id, key=self.GENAI, value=value)

    def addPropostaAI(self, bind: str, id: str, value):
        tempExt = self.getExtendedValue(bind=bind, id=id)
        if tempExt is None:
            tempExt = {'proposte':[]}
        tempExt['proposte'].append(value)
        self.setExtendedValue(bind=bind, id=id, key=self.GENAI, value=tempExt)


    def setExtendedValue(self, bind: str, id: str, key: str, value):
        if self.getValue(bind=bin, id=id) is None:
            self.setValue(bind=bind, id=id, value='')
        
        found = False
        for item in self.jsonComplete['data'][bind][id]['extendedValue']:
            if item["key"] == key:
                item["value"]['value'] = value
                found = True
                break
        if not found:
            self.jsonComplete['data'][bind][id]['extendedValue'].append({"key": key, "value": {"value":value}})
        

        found = False
        for item in self.businessObject['data'][bind][id]['extendedValue']:
            if item["key"] == key:
                item["value"]['value'] = value
                found = True
                break
        if not found:
            self.businessObject['data'][bind][id]['extendedValue'].append({"key": key, "value": {"value":value}})

    def getReference(self, bind:str, id:str):
        return self.getExtendedValue(bind=bind, id=id, key=self.REF)
    

    def getPropostaAI(self, bind:str, id:str):
        return self.getExtendedValue(bind=bind, id=id, key=self.GENAI)


    def getExtendedValue(self, bind:str, id:str, key:str):
        valReturn = None
        try:
            if existsJsonPath(self.businessObject,['data',bind, id, 'extendedValue']) and any(item["key"] == key for item in self.businessObject['data'][bind][id]['extendedValue']):# 'data' in self.businessObject['data'] and bind in self.businessObject['data'] and id in self.businessObject['data'][bind] and 'value' in self.businessObject['data'][bind][id] and 'value' in self.businessObject['data'][bind][id]['value']:
                element = next((item for item in self.businessObject['data'][bind][id]['extendedValue'] if item["key"] == key), None)
                valReturn = element['value']['value']
        except Exception as ex:
            print("Eccezione su getValue [{}][{}] - {}".format(bind, id, ex))
        return valReturn
    
    def setStatistics(self, obj):
        self.setOutputTask(self.STATISTICS, obj)

    def resetStatistics(self):
        self.setOutputTask(self.STATISTICS, {})
    
    def setValueStatistics(self, id: str, value):
        if self.getOutputTask(self.STATISTICS) == '':
            self.setOutputTask(self.STATISTICS, {})
        obj = self.getOutputTask(self.STATISTICS)
        obj[id] = value
        self.setStatistics(obj)

    def deleteValueStatistics(self, id: str):
        if self.getOutputTask(self.STATISTICS) != '':
            obj = self.getOutputTask(self.STATISTICS)
            if existsJsonPath(obj,[id]):
                obj.pop(id)
                self.setStatistics(obj)

    def getOutputTask(self, id:str):
        valReturn = ''
        try:
            if existsJsonPath(self.businessObject,[self.OUTPUT_TASK,id]):
                valReturn = self.businessObject[self.OUTPUT_TASK][id]
        except Exception as ex:
            print("Eccezione su getOutputTask [{}] - {}".format(id, ex))
        return valReturn
    
    def deleteOutputTask(self, id:str):
        try:
            if existsJsonPath(self.businessObject,[self.OUTPUT_TASK,id]):
                self.businessObject[self.OUTPUT_TASK].pop(id)
            if existsJsonPath(self.jsonComplete,[self.OUTPUT_TASK,id]):
                self.jsonComplete[self.OUTPUT_TASK].pop(id)
        except Exception as ex:
            print("Eccezione su deleteOutputTask [{}] - {}".format(id, ex))
        
    
    def setOutputTask(self, id: str, value):
        if self.OUTPUT_TASK not in self.jsonComplete:
            self.jsonComplete[self.OUTPUT_TASK] = {}
        if id not in self.jsonComplete[self.OUTPUT_TASK]:
            self.jsonComplete[self.OUTPUT_TASK][id] =  value
        elif self.jsonComplete[self.OUTPUT_TASK][id] != value:
            self.jsonComplete[self.OUTPUT_TASK][id] = value

        if self.OUTPUT_TASK not in self.businessObject:
            self.businessObject[self.OUTPUT_TASK] = {}
        if id not in self.businessObject[self.OUTPUT_TASK]:
            self.businessObject[self.OUTPUT_TASK][id] = value
        elif self.businessObject[self.OUTPUT_TASK][id] != value:
            self.businessObject[self.OUTPUT_TASK][id] = value


    def getObject(self, key: str):
        objectsReturn = []
        #object = None
        try:
            if existsJsonPath(self.businessObject,['objects']):
                objList = self.businessObject['objects']
                if objList is not None:
                    objects = list(objList)
                    if objects is not None:
                        for obj in objects:
                            if obj['key'] == key:
                                objectsReturn.append(obj)
        except Exception as ex:
            print("Eccezione su getObject - {}".format(ex))
        return objectsReturn
    
    def uploadObject(self, object: Object):
        self.objects.append(object)
        

    def complete(self, domain, taskId, priority=None, owner=None):
        if self.urlComplete is not None:
            dto = self.jsonComplete #_to_json(self.jsonComplete)
            #Preparo gli object
            objSend = []
            with contextlib.ExitStack() as stack:
                if len(self.objects) > 0:
                    if 'objects' not in self.jsonComplete:
                        self.jsonComplete['objects'] = []
                    
                    for index, obj in enumerate(self.objects):
                        if obj.multipartMode:
                            jsonObj = {
                                "id" : obj.id,
                                "extension" : obj.extension,
                                "name" : obj.name,
                                "key" : obj.key,
                                "base64" : obj.base64,
                                "partIndex":index,
                                "params" : obj.params
                            }
                            self.objects[index].file = stack.enter_context(open(obj.fileName, 'rb'))
                        else:
                                jsonObj = {
                                "id" : obj.id,
                                "extension" : obj.extension,
                                "name" : obj.name,
                                "key" : obj.key,
                                "base64" : obj.base64,
                                "params" : obj.parmas
                            }
                                #'dto': (json, 'application/json')
                        self.jsonComplete['objects'].append(jsonObj)
                json_file = stack.enter_context(tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8'))
                #json.dump(json_string, json_file, ensure_ascii=False, indent=4)
                #json_file.flush() 
                files = []
                payload = ('dto',(None, json.dumps(dto), 'application/json'))
                files.append(payload)
                for index, obj in enumerate(self.objects):
                    if obj.multipartMode:
                        files.append(('files',('{}.{}'.format(obj.name,obj.extension), obj.file, obj.contentType)))
                responseComplete = requests.post(self.urlComplete.replace('{domain}', domain).replace('{taskId}', taskId), files=files)
            return responseComplete

def _to_json(obj):
    return json.dumps(obj, indent=4, default=lambda obj: obj.__dict__)



