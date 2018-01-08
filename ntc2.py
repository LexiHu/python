import re
from ntcVisualize_2 import NTCGraph
from ntcVisualize_2 import NTNode
from ntcVisualize_2 import NTEdge
def de_BJ(line):
    line=line.encode('utf-8').decode('utf-8-sig')
    BJ=['╠','‖','↑','『','』','【','】']  # 未将""作为特殊标记删除
    for i in BJ:
        if(i in line):
            line=line.replace(i,'')
    if(('“' in line )and ('”' not in line)):
        line=line.replace('“','')
    if(('“' not in line )and ('”' in line)):
        line=line.replace('”','')
    if(('‘' in line )and ('’' not in line)):
        line=line.replace('‘','')
    if(('‘' not in line )and ('’' in line)):
        line=line.replace('’','')
    return line.strip()
def num_KG(line):
    if(re.search(r'^[\s]+', line)):
        return(len(re.search(r'[\s]+', line).group()))
    else:
        return(0)         
def if_FB_begin_bj(line):
        bj=''
        bo=False
        if('【' in line):
            bo=True
            bj='【'
        elif('“' in line and '”' not in line):
            bo=True
            bj='“'
        elif('‘' in line and '’' not in line):
            bo=True
            bj='‘'
        return bo,bj
def if_FB_end_bj(line):
        bj=''
        bo=False
        if('】' in line):
            bo=True
            bj='】'
        elif('“' not in line and '”'  in line):
            bo=True
            bj='”'
        elif('‘' not in line and '’'  in line):
            bo=True
            bj='’'
        return bo,bj             

def create_head_edge(i,lines,v):
    def creat_e_QZ(offset,lines,qz):
        v=offset
        bo=True
        bo1=False
        BJ=['『','』' ,'╠','】','”']
        for line in reversed(lines):
            line=line.encode('utf-8').decode('utf-8-sig')
            v=v-len(de_BJ(line))
            if('‖' in line):
                line=line.replace('‖',' ')
            if(num_KG(line)<num_KG(qz)):    
                lenth=num_KG(qz)-num_KG(line)
                if(bo1==True):
                    lenth=lenth-1
                Boo=[bj in line[:num_KG(qz)] for bj in BJ]
                if(any(Boo)):
                    lenth=lenth-Boo.count(True) 
                end=v+lenth-1   
                if(end<v):
                    if(num_KG(line)==0 and num_KG(qz)==1):
                        bo=False
                        break
                    else:
                        bo1=True
                        continue
                else:
                    break
        if(lenth==len(line.rstrip())-1):#找到的前置边为汇流边,end指向的是标点
            end+=1
        return bo,end        
    def creat_e_XZ(offset,lines,xz):
        v=offset
        lenth=num_KG(xz.replace('‖',' '))-num_KG(xz)-1
        end=-1
        for i,line in enumerate(reversed(lines)):
            line=line.encode('utf-8').decode('utf-8-sig')
            v=v-len(de_BJ(line))
            if('‖' in line):
                line=line.replace('‖',' ')
            if(num_KG(line)<=num_KG(xz) or num_KG(line)==num_KG(xz)+1):
                end=v+num_KG(xz.replace('‖',' '))-num_KG(line)-1
                break
            if(i>20):
                break
        if(end==-1): raise
        return end,lenth   
    def creat_e_HZ(offset,lines,hz):
        v=offset
        for line in lines:
            line=line.encode('utf-8').decode('utf-8-sig')
            if(num_KG(line)<=num_KG(hz)):
                if('╠' in line):
                    v=v+len(de_BJ(line))
                    continue
                if(num_KG(hz)!=0):
                    HZ=line[:hz.index('╠')+1].strip()
                    lenth=len(HZ)
                    end=v+lenth-1
                else:
                    end=v
                break
            v=v+len(de_BJ(line))
        return end
    line=lines[i].encode('utf-8').decode('utf-8-sig')
    end=-1
    lenth=-1
    bo,bj=if_FB_begin_bj(line)
    if('‖' in line and line.strip().index('‖')==0):
        lines_=lines[:i]
        end,lenth=creat_e_XZ(v, lines_,line)
    elif('╠' in line and line.strip().index('╠' )==0):
        lines_=lines[i+1:]
        end=creat_e_HZ(v+len(de_BJ(line)),lines_,line)
        lenth=0
    elif(bo==True and line.strip().index(bj)==0 and num_KG(line)>0):
        if(i>0):
            line_=lines[i-1].encode('utf-8').decode('utf-8-sig')
            if(num_KG(line)==len(line_.rstrip())-1):
                end=v-1
                lenth=0
    elif(num_KG(line)>0):
        lines_=lines[:i]   
        if(creat_e_QZ(v,lines_,line)[0]==True):
            end=creat_e_QZ(v,lines[:i],line)[1]
            lenth=0
    return end,lenth
def create_tail_edge(i,lines,v):
    def If_line_from_HLD(lines,i):
        if('『' in lines[i] or '』' in lines[i] ):
            return True
        else:
            m=-1
            n=-1
            bo=False
            k=0
            for j,line in enumerate(lines[i+1:]):
                if('『' in line):
                    m=j
                if('』' in line):
                    n=j
                if(n!=-1 and m==-1):
                    bo=True
                    break
                if(m!=-1 and n==1):
                    break    
                if(k>99):
                    if(m==-1 and n==-1):
                        break
                k=k+1
        if(bo==True and '』' not in lines[i]):
            if(num_KG(lines[i+1])==len(lines[i].rstrip())-1):
                bo=False
        return bo   
    def creat_e_HL(offset,lines,hl):
        v=offset
        end=-1
        for i,line in enumerate(lines):
            line=line.encode('utf-8').decode('utf-8-sig')
            bo,bj=if_FB_begin_bj(line)
            if(i==0 and bo==True and line.strip().index(bj)==0):
                end=v
                break
            elif(len(hl.rstrip())-1<=num_KG(line)):
                if('╠' in line and line.lstrip().index('╠')==0):
                    v=v+len(de_BJ(line))
                    continue
                else:
                    end=v
                    break
                if(i>3):
                    break    
            v=v+len(de_BJ(line))
#         if(end==-1):raise
        return end
    def creat_e_HLD(offset,lines,hl):
        v=offset
        bo=True#汇流段最后一个line，部分不需要建边
        if('』' in hl):
            if(hl.index('』')!=len(hl.rstrip())-2):
                end=0
                bo=False
            else:
                end=v
        else:
            for line in lines:
                line=line.encode('utf-8').decode('utf-8-sig')
                if('』' in line):
                    if(line.index('』')!=len(line.rstrip())-2):
                        end=v+line.strip().index('』')
                    else:
                        end=v+len(de_BJ(line))
                    break
                v=v+len(de_BJ(line))
        return bo,end
    lines_=lines[i+1:] 
    line=lines[i].encode('utf-8').decode('utf-8-sig')  
    end=-1             
    if(If_line_from_HLD(lines, i)):
        b1,_=creat_e_HLD(v+len(de_BJ(line)), lines_, line)
        if(b1==True):
            _,end=creat_e_HLD(v+len(de_BJ(line)), lines_, line)
    elif(i<len(lines)-1):
        line_2=lines[i+1].encode('utf-8').decode('utf-8-sig')
        if((len(line.rstrip())-1)<=num_KG(line_2)):                               
            end=creat_e_HL(v+len(de_BJ(line)),lines[i+1:],line)
    return end                                    

def create_g(lines,text,v=0):
    def add_node_or_subg(line):
        '''
               判断line加顶点、子图
               返回值    kind 
            None: 子图（结束）                      line】
               1：加顶点                                  line
               2：加子图（开始）                 【line
               3：左顶点 +右子图 (开始)    line1【line2
               4：左子图（结束）+顶点          line1】line2
        '''  
        bo1,bj1=if_FB_begin_bj(line)
        bo2,bj2=if_FB_end_bj(line)
        bj_index=-1
        if(bo1==True and bo2==True): raise  
        if(bo1==False and bo2==False):
            kind=1
        elif(bo1==True):
            if(line.lstrip().index(bj1)==0):
                kind=2
            else:
                kind=3
            bj_index=line.index(bj1)
        elif(bo2==True):
            line_=line[line.index(bj2)+1:]
            if(len(de_BJ(line_))!=0):
                kind=4
            else:
                kind=None
            bj_index=line.index(bj2)
        return kind,bj_index
    def add_edge_head_or_tail(line):        
        '''判断line建头边、尾边
        0：都要
        1：只加头边
        2：只加尾边
        None:不加
        '''
        kind,_=add_node_or_subg(line)
        if(kind==1):
            if('⊕' in line):
                edge_kind=None
            else:
                edge_kind=0
        elif(kind==2 or kind==3):
            edge_kind=1
        else:
            edge_kind=2
        return edge_kind
    def find_FBD_end(lines,bj_):
        if(bj_=='【'):
            bj=('【','】')
        elif(bj_=='‘'):
            bj=('‘','’')
        else:
            bj=('“','”')
        i_list=[]
        end=0
        for i,line in enumerate(lines):
            if(bj[0] in line):
                for _ in range(line.count(bj[0])):
                    i_list.append(bj[0])
            if(bj[1] in line):
                for _ in range(line.count(bj[1])):
                    i_list.append(bj[1])
                if(i_list.count(bj[0])<=i_list.count(bj[1])):
                    end=i
                    break
        assert end!=0
        return end    
    def find_FBD_content(lines,bj):
        result=[]
        if(bj=='【'):
            bj_='】'
        elif(bj=='‘'):
            bj_='’'
        else:
            bj_='”'
        for i,line in enumerate(lines):
            line=line.encode('utf-8').decode('utf-8-sig')
            if(i==0):
                j=line.index(bj)
            if(i==(len(lines)-1)):
                k=len(line)-line[::-1].index(bj_)-1
                line_=line[j+1:k]
            else:
                line_=line[j+1:]
            result.append(line_)
        return result 
    #---------------（子）图的初始化----------------------
    
    sub_text=''.join([de_BJ(line) for line in lines])
    g=NTCGraph(v,v+len(sub_text),text)
    #----------------维护nodes，edges两个列表-------------
    skip_to=-1
    If_skip=False
    for i,line in enumerate(lines):
        line=line.encode('utf-8').decode('utf-8-sig')
        if(len(line.strip())==0 ):
            continue
        if(If_skip==True):
            if( i<skip_to-1):
                v=v+len(de_BJ(line))
                continue
            else:
                skip_to=-1
                If_skip=False   
        #------------顶点或子图的创建----------------
#         print(v,line)
        kind,bj_index=add_node_or_subg(line)
        if(kind==1):#顶点
            g.nodes.append(NTNode(v,v+len(de_BJ(line))))
        elif(kind==2 or kind==3):
            start=v
            if(kind==3):#左顶点+右子图（开始）
                end=v+len(de_BJ(line[:bj_index]))
                g.nodes.append(NTNode(v,end))
                g.edges.append(NTEdge(end-1,end,0))
                g.edges.append(NTEdge(end,end-1,0))
                start=end
            skip_to=i+find_FBD_end(lines[i:],line[bj_index])+1
            lines_=find_FBD_content(lines[i:skip_to],line[bj_index])
            subg=create_g(lines_,text,start)
            g.nodes.append(subg)
            If_skip=True     
        elif(kind==4):#左子图（结束）+右顶点
            start=v+len(de_BJ(line[:bj_index]))
            end=v+len(de_BJ(line))
            g.nodes.append(NTNode(start,end))
            g.edges.append(NTEdge(start-1,start,0))
            g.edges.append(NTEdge(start,start-1,0))
        #--------------边的创建-------------------------
        edge_kind=add_edge_head_or_tail(line)
        if(edge_kind==0 or edge_kind==1):#头边
            end,lenth=create_head_edge(i,lines,v)
            if(end!=-1 and lenth!=-1):
                g.edges.append(NTEdge(v,end,lenth))
        if(edge_kind==0 or edge_kind==2):#尾边
            start=v+len(de_BJ(line))-1
            end=create_tail_edge(i,lines,v)
            if(end!=-1):
                g.edges.append(NTEdge(start,end,0))  
        v=v+len(de_BJ(line))
    return g  
def main():      
    f=open('D:\\test\\xs_clear.txt','r+',encoding='utf-8')   
    f1=open('D:\\test\\NTClauses.txt','r+',encoding='utf-8') 
    f2=open('D:\\test\\IndentedString.txt','r+',encoding='utf-8') 
    lines=f.readlines()
    text=''.join([de_BJ(line) for line in lines])
    g=create_g(lines,text)            
    g.description()    
    f1.writelines([line+'\n'for line in g.toNTClauses()])  
    f2.writelines([line+'\n'for line in g.toIndentedString()]) 
   
     
#     for clause in g.toNTClauses():
#         print(clause)
#     print('----------------------------------------------------------------')
#     for clause in g.toIndentedString():
#         print(clause)   
                 
if(__name__ =='__main__'):
    main() 