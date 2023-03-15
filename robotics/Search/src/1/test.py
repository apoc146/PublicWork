class RRT_Node:
    def __init__(self, conf):
        self.conf=conf
        self.parent=None
        self.children=[]

    def set_parent(self, parent):
        self.parent=parent

    def add_child(self, child):
        self.children.append(child)

    def get_parent(self):
        return self.parent

    def get_config(self):
        return self.conf


def foo(index):
    return l[index]

if __name__ == "__main__":
    n1=RRT_Node(1)
    n2=RRT_Node(2)
    n3=RRT_Node(3)
    n4=RRT_Node(4)
    n1.set_parent(n2)
    n2.set_parent(n3)
    n3.set_parent(n4)
    n4.set_parent(None)

    l=list([n1,n2,n3,n4])
    node=foo(2)

    print(node.conf)
    print("\nabc->")
    node.conf=100
    print([x.conf for x in l])
