import json
from typing import List

class ObjEvent:
    taskId = ''
    taskPriority = ''
    taskName = ''
    processId = ''
    domain = ''
    businessKey = ''
    owner = ''
    internalBusinessKey = ''
    processInstanceId = ''
    processVariables=[]
    bodyRaw={}
    awsRegion=''
    def __init__(self):
        self.files = []
        self.processVariables = []
        self.bodyRaw = {}

def getObjEvent(event) -> List[ObjEvent]: 
    objReturn = []
    myList = list(event['Records'])
    for elem in myList:
        objEvent = ObjEvent()
        objMsg = json.loads(elem["body"])
        objEvent.awsRegion = elem["awsRegion"]
        objEvent.bodyRaw = objMsg

        objEvent.taskId = objMsg["taskId"]
        if "Priority" in objMsg:
            objEvent.taskPriority = objMsg["Priority"]
        elif "taskPriority" in objMsg:
            objEvent.taskPriority = objMsg["taskPriority"]
        elif "priority" in objMsg:
            objEvent.taskPriority = objMsg["priority"]
        else:
            objEvent.taskPriority = "-1"
        objEvent.taskName = objMsg["taskName"]
        objEvent.processId = objMsg["processId"]
        if "processInstanceId" in objMsg:
            objEvent.processInstanceId = objMsg["processInstanceId"]
        objEvent.domain = objMsg["domain"]
        objEvent.businessKey = objMsg["businessKey"]
        processVariables = objMsg["processVariables"]        
        objEvent.processVariables = processVariables
        #objEvent.owner = processVariables["owner"]
        objEvent.internalBusinessKey = processVariables["internalBusinessKey"]
        objReturn.append(objEvent)

    return objReturn

