
#coding=utf-8
import json
    
class NTNode:
    def __init__(self, start, end):
        if start < 0: raise IndexError('negative node start: %d' % start)
        if start >= end: raise ValueError('empty node: [%d, %d)' % (start, end))
        self.start = start
        self.end = end
    def toDict(self):
        return {'NTNode': True, 'start': self.start, 'end': self.end}
    def isIn(self, pos):
        return (pos >= self.start) and (pos < self.end)
    def isStart(self, pos):
        return pos == self.start
    def isEnd(self, pos):
        return pos == self.end-1
    def isInner(self, pos):
        return (pos > self.start) and (pos < self.end-1)
#     @property
#     def start(self):
#         return self.start
#     @property
#     def end(self):
#         return self.end
    def length(self):
        return self.end-self.start
    def name(self):
        return u'[node%d-%d]'%(self.start, self.end)
    def description(self):
        print('\t'.join(['%s:%s' % item for item in self.__dict__.items()]))

class NTEdge:
    def __init__(self, start, end, length):
        self.start = start
        self.end = end
        self.length = length
#     @property
#     def start(self):
#         return self.start
#     @property
#     def end(self):
#         return self.end
#     @property
#     def length(self):
#         return self.length
    def toDict(self):
        return {'NTEdge' : True, 'start': self.start, 'end': self.end, 'length': self.length}
    def description(self):
        print('\t'.join(['%s:%s' % item for item in self.__dict__.items()]))

class NTCGraph(NTNode):
    def __init__(self, start, end, text):
        NTNode.__init__(self, start, end)
        self.text = text
        self.nodes =[]
#         self.nodes = [NTNode(start, end)]
        self.edges = []
        self.space = u'　'
        self.chDl = u'║'
    def toDict(self):
        return {'NTCGraph' : True, 'start' : self.start, 'end' : self.end, 
                'text': self.text, 'nodes': self.nodes, 'edges': self.edges}
    def text(self):
        return self.text
    def __findNodeIndex(self, pos):
        for i in range(len(self.nodes)):
            if self.nodes[i].isIn(pos):
                return (i, pos-self.nodes[i].start)
        raise IndexError('%d: out of the range of sentence' % pos)
    def __addEdge(self, start, end, length, bidirection=False):
        #check duplicated edges!
        self.edges.append(NTEdge(start, end, length))
        if bidirection:
            assert(length == 0)
            self.edges.append(NTEdge(end, start, length))
    
    def split(self, pos, direction=0):
        '''
        split node on pos into two nodes:   pos-1 | pos 
        pos: position
        direction: direct of edge. if None: no edge, 1: forward <---, 2: backward--->, 0: both<--->
        '''
        nodeIdx, offset = self.__findNodeIndex(pos)
        if offset == 0:
            raise IndexError('split at the beginning of node: %d' % pos)
        if isinstance(self.nodes[nodeIdx], NTCGraph):
            self.nodes[nodeIdx].split(pos, direction)
        else:
            newnode = NTNode(pos, self.nodes[nodeIdx].end)
            self.nodes[nodeIdx].end = pos
            self.nodes.insert(nodeIdx+1, newnode) #after nodeIdx
            
            if direction != None:
                if (direction == 1):
                    self.__addEdge(start = pos, end = pos-1, length = 0)
                else:
                    self.__addEdge(start = pos-1, end = pos, length = 0, 
                                   bidirection = False if direction == 2 else True)

    def setRelation(self, start, end, length, direction=0):
        '''
        direction : 0,1: | start(beginning of node)
                    2: start(end of node) |
        '''
        if not self.isIn(start) or not self.isIn(end):
            raise IndexError('out of index: (%d, %d)' % (start, end))
        if (start == end):
            raise ValueError('add edge with equal start and end: %d' % start)
        if length < 0:
            raise ValueError('negative length of naming part: %d' % length)
        
        snodei, _ = self.__findNodeIndex(start)
        enodei, _ = self.__findNodeIndex(end)
        if isinstance(self.nodes[snodei], NTCGraph):
            if isinstance(self.nodes[enodei], NTCGraph):
                if snodei != enodei:
                    raise ValueError('failed to add edge between enclosed-clauses')
                else:
                    self.nodes[snodei].setRelation(start, end, length, direction)
                    return
            else:
                if self.nodes[snodei].isInner(start):
                    raise ValueError('edge start from inner of enclosed-clause')
        else:
            if isinstance(self.nodes[enodei], NTCGraph):
                if self.nodes[enodei].isInner(end):
                    raise ValueError('edge into enclosed-clause')
            elif self.nodes[snodei].isInner(start):
                self.split(start+1 if direction==2 else start, direction=None)
        self.__addEdge(start, end, length, True if direction == 0 else False)
        
    def addSubgraph(self, start, end):
        if (start < self.start) or (end > self.end) or (end-start >= self.end-self.start):
            raise ValueError('addSubgraph: subgraph should be sub of parent')
        snodei, soffset = self.__findNodeIndex(start)
        enodei, _ = self.__findNodeIndex(end-1)
        if snodei != enodei:
            raise ValueError('addSubgraph: cannot enclose two or more nodes')
        if self.nodes[snodei].isStart(start) and self.nodes[enodei].isEnd(end):
            raise ValueError('addSubgraph: node is already in list')
        if isinstance(self.nodes[snodei], NTCGraph):
            self.nodes[snodei].addSubgraph(start, end)
        else:
            if soffset == 0:
                self.nodes[snodei].start = end
                self.nodes.insert(snodei, NTCGraph(start, end, self.text))
            elif end < self.nodes[snodei].end:
                #node/subgraph/node
                newnode = NTNode(self.nodes[snodei].start, start)
                sg = NTCGraph(start, end, self.text)
                self.nodes[snodei].start = end
                self.nodes.insert(snodei, sg)
                self.nodes.insert(snodei, newnode)
            else:
                self.nodes[snodei].end = start
                self.nodes.insert(snodei+1, NTCGraph(start, end, self.text))
    
    def getDepends(self):
        dps = {}
        for ni in range(len(self.nodes)):
            dps[ni] = ([], []) #forward and backward
        for ei in range(len(self.edges)):
            edge = self.edges[ei]
            snodei, _ = self.__findNodeIndex(edge.start)
            enodei, _ = self.__findNodeIndex(edge.end)
           
            assert snodei != enodei
            assert not self.nodes[snodei].isInner(edge.start)
#             assert not (self.nodes[snodei].isEnd(edge.start) and self.nodes[enodei].isEnd(edge.end))
            #snodei --> enodei
            if (self.nodes[snodei].isStart(edge.start)):
                dps[snodei][0].append(ei)
            else:
                dps[snodei][1].append(ei)
        return dps
    
    def toNTClauses(self):
        '''
        transfer graph to NTClauses
        '''
        dps = self.getDepends()
        visited = [False] * len(self.nodes)

        def __expandNode(ni):
            '''
            expand node to clauses
            '''
            def __traverseForward(ei, suffix):
                '''
                dps: depends between nodes
                ei: edge index
                suffix: suffix in unicode list
                return: list of unicode list
                '''
                edge = self.edges[ei]
                nodei, _ = self.__findNodeIndex(edge.end)
                if edge.length > 0:
                    assert(not isinstance(self.nodes[nodei], NTCGraph))
                    suffix = list(self.text[edge.end-edge.length+1 : edge.end+1])+suffix
                    return [suffix]
                else:
                    if isinstance(self.nodes[nodei], NTCGraph):
                        suffix = list(self.nodes[nodei].name())+suffix
                    else:
                        suffix = list(self.text[self.nodes[nodei].start : edge.end+1])+suffix
                    ret = []
                    for e in dps[nodei][0]:
                        ret.extend(__traverseForward(e, suffix))
                    if len(ret) == 0:
                        return [suffix]
                    else:
                        return ret
                
            def __traverseBackward(ei, prefix):
                '''
                dps: depends between nodes
                ei: edge index
                suffix: suffix in unicode list
                return: list of unicode list
                '''
                edge = self.edges[ei]
                assert (edge.length == 0)
                nodei, offset = self.__findNodeIndex(edge.end)
                if (offset == 0): visited[nodei] = True
                if isinstance(self.nodes[nodei], NTCGraph):
                    prefix.extend(list(self.nodes[nodei].name()))
                else:
                    prefix.extend(list(self.text[edge.end : self.nodes[nodei].end]))
                ret = []
                for e in dps[nodei][1]:
                    ret.extend(__traverseBackward(e, prefix))
                if len(ret) == 0:
                    return [prefix]
                else:
                    return ret
    
            if isinstance(self.nodes[ni], NTCGraph):
                ret = [list(self.nodes[ni].name()+u':[')]
                ret.extend(self.nodes[ni].toNTClauses())
                ret.append(list(u']'))
                return ret
    
            if visited[ni]: return []
            visited[ni] = True
                
            pre = []
            for ei in dps[ni][0]:
                pre.extend(__traverseForward(ei, []))
            post = []
            for ei in dps[ni][1]:
                post.extend(__traverseBackward(ei, []))
            ret = []
            text = list(self.text[self.nodes[ni].start:self.nodes[ni].end])
            if len(pre) > 0:
                if len(post) > 0:
                    for preT in pre:
                        for postT in post:
                            ret.append(preT+text+postT)
                else:
                    ret = [preT+text for preT in pre]
            elif len(post) > 0:
                ret = [text+postT for postT in post]
            else:
                return [text]
            return ret

        clauses = []
        for ni in range(len(self.nodes)):
            for ltxt in __expandNode(ni):
                clause = u''.join(ltxt)
                clauses.append(clause)
        return clauses
    
    def toIndentedString(self):
        '''
        transfer graph to indented string
        '''
        dps = self.getDepends()
        
        def indentedPos(ni):
            if (len(dps[ni][0]) == 0):
                return 0
            else:
                mdis = self.end-self.start
                mlen = -1
                for ei in dps[ni][0]:
                    edge = self.edges[ei]
                    nodei, offset = self.__findNodeIndex(edge.end)
                    if (abs(edge.end-edge.start) < mdis): 
                        mlen = offset+indentedPos(nodei)+1
                        mdis = abs(edge.end-edge.start)
                return mlen
            
        def partDepend(ni):
            if (len(dps[ni][0]) == 0):
                return None
            else:
                for ei in dps[ni][0]:
                    edge = self.edges[ei]
                    _, offset = self.__findNodeIndex(edge.end)
                    if ((edge.length > 0) and (edge.length < offset+1)):
                        assert(len(dps[ni][0]) == 1)
                        return edge.length
                return None
        
        clauses = []    
        for ni in range(len(self.nodes)):
            ip = indentedPos(ni)
            if isinstance(self.nodes[ni], NTCGraph):
                cs = [self.nodes[ni].name()+u':[']
                cs.extend(self.nodes[ni].toIndentedString())
                cs.append(u']')
                clauses.extend([self.space*ip+s for s in cs])
            else:
                dl = partDepend(ni)
                if (dl):
                    clause = u''.join([self.space]*(ip-dl-1)+[self.chDl]+[self.space]*dl+
                                      list(self.text[self.nodes[ni].start:self.nodes[ni].end]))
                else:    
                    clause = u''.join([self.space]*ip+
                                      list(self.text[self.nodes[ni].start:self.nodes[ni].end]))
                clauses.append(clause)
        return clauses
    
    def toJSONs(self):
        class NTCGraphEncoder(json.JSONEncoder):  
            def default(self, obj):  
                if isinstance(obj, NTCGraph) or isinstance(obj, NTNode) or isinstance(obj, NTEdge):
                    return obj.toDict()
                return json.JSONEncoder.default(self, obj)
        return json.dumps(self, cls=NTCGraphEncoder)
    
    @classmethod
    def fromJSONs(cls, sjson):
        def dict2nts(d):
            if 'NTCGraph' in d:
                g = NTCGraph(d['start'], d['end'], d['text'])
                del g.nodes
                g.nodes = d['nodes']
                del g.edges
                g.edges = d['edges']
                return g
            elif 'NTNode' in d:
                return NTNode(d['start'], d['end'])
            elif 'NTEdge' in d:
                return NTEdge(d['start'], d['end'], d['length'])
            else:
                return d
        return json.loads(sjson, object_hook = dict2nts)
    
    def action(self, sjson_action):
        '''
        action---: name, parameters
            split: pos; [direction = None, no edge], 1: forward <---, 2: backward--->, 0: both<--->
            setRelation: start, end, length, direct: 0,1: | start(beginning of node)  2: start(end of node) |
            addSubgraph: start, end
        '''
        act = json.loads(sjson_action)
        if act['name'] == 'split':
            direct = None if not 'direction' in act else act['direction']
            self.split(act['pos'], direct)
        elif act['name'] == 'setRelation':
            self.setRelation(act['start'], act['end'], act['length'], act['direction'])
        elif act['name'] == 'addSubgraph':
            self.addSubgraph(act['start'], act['end'])
        else:
            #unknown action
            pass
    
    def description(self):
        print(self.text[self.start:self.end])
        print('nodes: %d' % len(self.nodes))
        for node in self.nodes:
            node.description()
        print('edges: %d' % len(self.edges))
        for edge in self.edges:
            edge.description()
        

