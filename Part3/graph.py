class Graph_Node:
    def __init__(self, graph_info=None, normal_pars=None, normal_chils=None, ser_pars=None, ser_chils=None, con_pars=None, con_chils=None):
        self.graph_info = graph_info if graph_info is not None else []
        
        self.normal_pars = normal_pars if normal_pars is not None else []
        self.normal_chils = normal_chils if normal_chils is not None else []
        
        self.con_pars = con_pars if con_pars is not None else []
        self.con_chils = con_chils if con_chils is not None else []
        
        self.ser_pars = ser_pars if ser_pars is not None else []
        self.ser_chils = ser_chils if ser_chils is not None else []
        
        self.check_executed_chils= False
        self.check_executed_self = False
        
        self.weight = 0
        
        self.check_visited = False
        self.check_scheduled = False
        
    
    def ready_check(self):
        if self.check_executed_chils:
            return True
        executed = all(child.check_executed_self for child in self.normal_chils + self.con_chils)
        scheduled = all(child.check_scheduled for child in self.ser_chils)
        self.check_executed_chils= executed & scheduled
        return self.check_executed_chils