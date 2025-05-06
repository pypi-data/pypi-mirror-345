from helpers import parseAttributes


class DccMathml:
    def __init__(self, content, id: None, refId: None, refType: None) -> None:
        self.content = content
        self.id = id
        self.refId = refId
        self.refType = refType

def parseDccMathml(jsonDict):
    dccMathmlArgs = parseAttributes(jsonDict=jsonDict)
    dccMathmlArgs['content'] = jsonDict['$']

    return DccMathml(**dccMathmlArgs)
