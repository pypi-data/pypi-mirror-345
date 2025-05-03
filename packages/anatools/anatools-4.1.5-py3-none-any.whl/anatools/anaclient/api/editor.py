"""
Channels API calls.
"""

def createRemoteDevelopment(self, organizationId=None, channelId=None, channelVersion=None, instanceType=None, verbose=False):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createRemoteDevelopment",
            "variables": {
                "organizationId": organizationId,
                "channelId": channelId,
                "channelVersion": channelVersion,
                "instanceType": instanceType
            },
            "query": """mutation
                createRemoteDevelopment($organizationId: String, $channelId: String!, $channelVersion: String, $instanceType: String) {
                    createRemoteDevelopment(organizationId: $organizationId, channelId: $channelId, channelVersion: $channelVersion, instanceType: $instanceType) {
                        organizationId
                        channelId
                        editorUrl
                        editorSessionId
                        instanceType
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "createRemoteDevelopment")

def deleteRemoteDevelopment(self, editorSessionId, organizationId=None, verbose=False):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteRemoteDevelopment",
            "variables": {
                "organizationId": organizationId,
                "editorSessionId": editorSessionId,
            },
            "query": """mutation
                deleteRemoteDevelopment($organizationId: String, $editorSessionId: String!) {
                    deleteRemoteDevelopment(organizationId: $organizationId, editorSessionId: $editorSessionId) {
                        organizationId
                        editorSessionId
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "deleteRemoteDevelopment")

def listRemoteDevelopment(self, organizationId=None, verbose=False):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "listRemoteDevelopment",
            "variables": {
                "organizationId": organizationId
            },
            "query": """query
                listRemoteDevelopment($organizationId: String) {
                    listRemoteDevelopment(organizationId: $organizationId) {
                        organizationId
                        organization
                        channel
                        channelId
                        editorUrl
                        editorSessionId
                        instanceType
                        sshPort
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "listRemoteDevelopment")

def stopRemoteDevelopment(self, editorSessionId, organizationId=None, verbose=False):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "stopRemoteDevelopment",
            "variables": {
                "organizationId": organizationId,
                "editorSessionId": editorSessionId,
            },
            "query": """mutation
                stopRemoteDevelopment($organizationId: String, $editorSessionId: String!) {
                    stopRemoteDevelopment(organizationId: $organizationId, editorSessionId: $editorSessionId) {
                        organizationId
                        editorSessionId
                        editorUrl
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "stopRemoteDevelopment")

def startRemoteDevelopment(self, editorSessionId, organizationId=None, verbose=False):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "startRemoteDevelopment",
            "variables": {
                "organizationId": organizationId,
                "editorSessionId": editorSessionId,
            },
            "query": """mutation
                startRemoteDevelopment($organizationId: String, $editorSessionId: String!) {
                    startRemoteDevelopment(organizationId: $organizationId, editorSessionId: $editorSessionId) {
                        organizationId
                        editorSessionId
                        editorUrl
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "startRemoteDevelopment")


def createSSHKey(self, name, key):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "createSSHKey",
            "variables": {
                "name": name,
                "key": key
            },
            "query": """mutation
                createSSHKey($name: String!, $key: String!) {
                    createSSHKey(name: $name, key: $key)
                }"""})
    return self.errorhandler(response, "createSSHKey")


def deleteSSHKey(self, name):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "deleteSSHKey",
            "variables": {
                "name": name
            },
            "query": """mutation
                deleteSSHKey($name: String!) {
                    deleteSSHKey(name: $name)
                }"""})
    return self.errorhandler(response, "deleteSSHKey")


def getSSHKeys(self):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "getSSHKeys",
            "variables": {},
            "query": """query
                getSSHKeys {
                    getSSHKeys {
                        name
                        key
                        createdAt
                    }
                }"""})
    return self.errorhandler(response, "getSSHKeys")