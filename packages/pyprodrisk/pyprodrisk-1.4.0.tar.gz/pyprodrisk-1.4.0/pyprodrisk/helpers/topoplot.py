import numpy as np

class module_info:

    def __init__(self):
        self.kote_min = 0.0
        self.kote_max = 0.0
        self.vol_max = 0
        self.nom_head = 0
        self.name = 'Module'
        self.stasjon = 'Plant'
        self.MW = 0
        self.qmax = 0
        self.reg_inflow_ser = 'inflow'
        self.unreg_inflow_ser = ''
        self.mean_unreg_inf = 0.0
        self.topo = np.zeros(3)
        self.pump_topo = {}
        #self.pumps_from = 0
        #self.pumps_to = 0
        #self.no_pumps = 0

    dis_to = property(fget = (lambda self: self.topo[0]))
    byp_to = property(fget = (lambda self: self.topo[1]))
    spi_to = property(fget = (lambda self: self.topo[2]))
    n_pumps = property(fget = (lambda self : len(self.pump_topo)))
    has_pump = property(fget = (lambda self : len(self.pump_topo)>0))


def collect_info(ps):  # ps -- ProdriskSession
    mod_dict = {}
    inflows = ps.model.inflowSeries.get_object_names()
    inflow_ids = [ps.model.inflowSeries[name].seriesId.get() for name in inflows]
    for mod in ps.model.module.get_object_names():
        M = ps.model.module[mod]
        mod_info = module_info()
        mod_info.name = mod
        mod_info.stasjon = M.plantName.get()
        mod_info.MW = M.maxProd.get()
        mod_info.qmax = M.maxDischargeConst.get()
        res_curve = M.volHeadCurve.get()
        try:
            mod_info.kote_min = res_curve.values[0]
            mod_info.kote_max = res_curve.values[-1]
        except AttributeError:
            #print(mod, 'has no reservoir curve')
            pass
        mod_info.vol_max = M.rsvMax.get()
        mod_info.nom_head = M.nominalHead.get()
        mod_info.reg_inflow_ser = inflows[inflow_ids.index(M.connectedSeriesId.get())]
        if M.connected_unreg_series_id.get()>0:
            mod_info.unreg_inflow_ser = inflows[inflow_ids.index(M.connected_unreg_series_id.get())]
        mod_info.mean_reg_inf = M.meanRegInflow.get()
        mod_info.topo = M.topology.get()
        mod_dict[M.number.get()] = mod_info
    for pump in ps.model.pump.get_object_names():
        P = ps.model.pump[pump]
        t = P.topology.get()
        mid = t[0]
        mod_dict[mid].pump_topo[P.name.get()] = [t[1],t[2],P.averagePower.get()]

    return mod_dict

class mod_tree:

    def __init__(self, mod_dict):
        self.modules = mod_dict
        self.levels = []
        unassigned = list(mod_dict.keys())
        assigned = [0]

        # make hierachy
        while len(unassigned) > 0:
            new_level = []
            for mid in unassigned:
                M = mod_dict[mid]
                if M.dis_to in assigned and M.byp_to in assigned and M.spi_to in assigned:
                    new_level.append(mid)
            for mid in new_level:
                assigned.append(mid)
                unassigned.remove(mid)
            if len(new_level)>0:
                self.levels.append(new_level)
            else:
                print('Error: invalid topology! Remaining modules:', unassigned)
                break

        for i in range(len(self.levels)):
            self.levels[i].sort()

        self.N_inter = 40
        self.curved_connections = True
        self.a_connection_exists = {'discharge': False, 'bypass': False, 'spillage': False, 'pump': False}
        self.connection_style = {'discharge': '-k', 'bypass': '--b', 'spillage': ':r', 'pump': 'g'}
        self.anchor_offset = {'discharge': [0,0], 'bypass': [0,0], 'spillage': [0,0.05], 'pump': [0.175,0.4]}
        #self.mod_width   = 0.4
        #self.mod_height  = 0.4
        #self.plant_width = 0.2
        #self.plant_height= 0.1

    def all_x(self):
        return np.array([self.coords[mid][0] for mid in self.coords.keys()])

    def all_y(self):
        return np.array([self.coords[mid][1] for mid in self.coords.keys()])

    def print_levels(self):
        for i in np.arange(len(self.levels)-1,-1,-1):
            mods = ''
            for mid in self.levels[i]:
                mods += self.modules[mid].name + '\t'
            print(mods)

    def init_coords(self):
        coords = {}
        for i in range(len(self.levels)):
            y = (i+0.5)*np.ones(len(self.levels[i]))*1.5
            x = 10./len(self.levels[i])*np.linspace(0.5,len(self.levels[i])-0.5,len(self.levels[i]))
            for j in range(len(self.levels[i])):
                mid = self.levels[i][j]
                coords[mid] = [x[j],y[j]]
        coords[0] = [5,0]
        self.coords = coords

    def relax_coords(self):
        import scipy as sci
        def objective(x, xc, y, cy, xbyp, ybyp):
            a = y - cy
            dc = np.sum((x - xc)**2 + a**2)
            dbyp = np.sum((x-xbyp)**2 + (y-ybyp)**2)
            xdist = -0.5*np.sum(np.array([(x-np.roll(x,i))**2/(1+(x-np.roll(x,i))**2) for i in range(len(x))]).flatten())
            return dc + 1.4*xdist + 0.3*dbyp

        for L in range(len(self.levels)):
            level_x = []
            level_y = []
            centerx = []
            centery = []
            bypassx = []
            bypassy = []
            for mid in self.levels[L]:
                level_x.append(self.coords[mid][0])
                level_y.append(self.coords[mid][1])
                centerx.append(self.coords[self.modules[mid].dis_to][0])
                centery.append(self.coords[self.modules[mid].dis_to][1])
                bypassx.append(self.coords[self.modules[mid].byp_to][0])
                bypassy.append(self.coords[self.modules[mid].byp_to][1])
            level_x = np.array(level_x)
            level_y = np.array(level_y)
            centerx = np.array(centerx)
            centery = np.array(centery)
            bypassx = np.array(bypassx)
            bypassy = np.array(bypassy)

            opt_res = sci.optimize.minimize(objective, level_x, args=(centerx, level_y, centery, bypassx, bypassy))
            i = 0
            for mid in self.levels[L]:
                self.coords[mid][0] = opt_res.x[i]
                i = i+1

    def _plot_module(self, mid, ax):
        x = self.coords[mid][0]
        y = self.coords[mid][1]
        fc = 'azure' if self.modules[mid].vol_max>0 else 'white'
        ax.fill([x-0.1,x+0.1,x+0.2,x-0.2],[y,y,y+0.41,y+0.41],edgecolor='b',facecolor=fc,zorder=3)
        if self.modules[mid].MW > 0:
            ax.fill([x-0.05,x+0.05,x+0.05,x-0.05],[y-0.22,y-0.22,y+0,y+0],facecolor='k',zorder=4)
            ax.text(x,y-0.1,'~',horizontalalignment='center',verticalalignment='center',color='w',zorder=5,fontsize=20)
        #if self.modules[mid].has_pump:
        for ip in range(self.modules[mid].n_pumps):
            ax.fill([x+0.15,x+0.2,x+0.2,x+0.15],[ip*0.28+y+0.14,ip*0.28+y+0.14,ip*0.28+y+0.4,ip*0.28+y+0.4],facecolor='g',zorder=6)
            ax.text(x+0.165,ip*0.28+y+0.27,r'$\uparrow$',color='w',verticalalignment='center',horizontalalignment='center',zorder=7,fontsize=18)
        #Place empty text labels
        self.label_ID[mid] = ax.text(x-0.21,y+0.18,"ID",horizontalalignment='center',rotation=-45,verticalalignment='center',color='0.5')
        self.label_inflow[mid] = ax.text(x-0.2,y+0.46,"Inflow",horizontalalignment='left')
        self.label_name[mid] = ax.text(x+0,y+0.25,"Name",horizontalalignment='center')
        self.label_vol[mid] = ax.text(x+0,y+0.05,"Vol",horizontalalignment='center')
        self.label_plant[mid] = ax.text(x-0.06,y-0.16,"Plant",horizontalalignment='right')
        self.label_MW[mid] = ax.text(x-0.06,y-0.34,"Power",horizontalalignment='right')
        self.label_qmax[mid] = ax.text(x-0.06,(y-0.52) if self.modules[mid].MW>0 else y-0.16,"Flow",horizontalalignment='right')
        self.label_pump[mid] = {}
        ip = 0
        for P in self.modules[mid].pump_topo.keys():
            self.label_pump[mid][P] = ax.text(x+0.21,ip*0.4+y+0.27,"Pump",horizontalalignment='left',verticalalignment='center')
            ip += 1

    def populate_selected_labels(self, content:list[str]=['all']):
        import matplotlib.pyplot as plt

        for mid in self.modules.keys():
            if not content: content = ['ID'] #content list is empty, overwrite to show ID nonetheless
            if content==['all']:
                content = ['ID', 'vol', 'name', 'plant', 'MW', 'qmax', 'inflow', 'pump']
            
            if 'ID' in content: 
                self.label_ID[mid].set_text(f'#{mid}')
            else:
                self.label_ID[mid].set_text("")
            if 'vol' in content: 
                self.label_vol[mid].set_text(f'{np.round(self.modules[mid].vol_max,1)} Mm3')
            else:
                self.label_vol[mid].set_text("")
            if 'name' in content: 
                self.label_name[mid].set_text(self.modules[mid].name.strip())
            else:
                self.label_name[mid].set_text("")
            if 'plant' in content and self.modules[mid].MW > 0:
                self.label_plant[mid].set_text(self.modules[mid].stasjon.strip())
            else: self.label_plant[mid].set_text("")
            if 'MW' in content and self.modules[mid].MW > 0:
                self.label_MW[mid].set_text(f'{np.round(self.modules[mid].MW,1)} MW')
            else:
                self.label_MW[mid].set_text("")
            if 'qmax' in content:
                self.label_qmax[mid].set_text(f'{np.round(self.modules[mid].qmax,1)} m3/s')
            else:
                self.label_qmax[mid].set_text("")
            if 'inflow' in content:
                self.label_inflow[mid].set_text(fr'$\downarrow${np.round(self.modules[mid].mean_reg_inf,1)} Mm3 ({self.modules[mid].reg_inflow_ser})')
            else:
                self.label_inflow[mid].set_text('')
            for P in self.label_pump[mid].keys():
                if 'pump' in content:
                    self.label_pump[mid][P].set_text(f'{P}\n{round(self.modules[mid].pump_topo[P][2],1)} MW')
                else:
                    self.label_pump[mid][P].visible = False
        plt.draw()

    def _make_anchors(self, mid1, mid2, Dmin=0.28, ctype='discharge'):
        L1 = 0
        L2 = 0
        off_x = self.anchor_offset[ctype][0]
        off_y = self.anchor_offset[ctype][1]
        for i in range(len(self.levels)):
            if mid1 in self.levels[i]:
                L1 = i
            if mid2 in self.levels[i]:
                L2 = i
        dL = abs(L1-L2)
        anchors_x = [self.coords[mid1][0]+off_x]
        anchors_y = [self.coords[mid1][1]+off_y]
        if dL < 2 or self.curved_connections==False:
            anchors_x.append(self.coords[mid2][0])
            anchors_y.append(self.coords[mid2][1])
            return anchors_x, anchors_y
        for i in max(L1,L2)-1-np.arange(dL-1):
            for mid in self.levels[i]:
                dx = self.coords[mid1][0] - self.coords[mid2][0] + off_x
                dy = self.coords[mid1][1] - self.coords[mid2][1] + off_y
                dx2= self.coords[mid][0] - self.coords[mid2][0]
                dy2= self.coords[mid][1] - self.coords[mid2][1]
                t  =(dy*dy2 + dx*dx2)/(dx**2+dy**2)
                x4 = self.coords[mid2][0] + t*dx
                y4 = self.coords[mid2][1] + t*dy
                dis = np.sqrt((x4 - self.coords[mid][0])**2 + (y4 - self.coords[mid][1])**2)
                if t>0 and t<1 and dis<Dmin:
                    s = (Dmin/(dis+1e-3))*(t*dx - dx2)/dy
                    x5 = self.coords[mid][0] + s*dy
                    y5 = self.coords[mid][1] - s*dx
                    anchors_x.append(x5)
                    anchors_y.append(y5)
        anchors_x.append(self.coords[mid2][0])
        anchors_y.append(self.coords[mid2][1])
        return anchors_x, anchors_y

    def _get_curve(self, anchor_x, anchor_y):
        import scipy as sci
        if len(anchor_x)<3:
            return anchor_x, anchor_y
        t = np.linspace(0,10,len(anchor_x))
        csx = sci.interpolate.CubicSpline(t, anchor_x)
        csy = sci.interpolate.CubicSpline(t, anchor_y)
        t = np.linspace(0,10,self.N_inter)
        return csx(t), csy(t)

    def draw_connection(self, mid1, mid2, ax, ctype='discharge'):
        an_x, an_y = self._make_anchors(mid1, mid2, ctype=ctype)
        x_points, y_points = self._get_curve(an_x, an_y)
        if not self.a_connection_exists[ctype]:
            self.a_connection_exists[ctype] = True
            lab = ctype
        else:
            lab = None
        ax.plot(x_points, y_points, self.connection_style[ctype], label=lab)

    def plot_topology(self, axtitle="", to_file="", content:list[str]=['all']):
        import matplotlib.pyplot as plt

        self.init_coords()
        self.relax_coords()
        f = plt.figure(1, figsize=(16,14))
        ax = plt.subplot(111)
        any_pump = False
        for mid in self.modules.keys():
            dis = self.modules[mid].dis_to
            byp = self.modules[mid].byp_to
            spi = self.modules[mid].spi_to
            self.draw_connection(mid, dis, ax, ctype='discharge')
            if dis!=byp:
                self.draw_connection(mid, byp, ax, ctype='bypass')
            if dis!=spi:
                self.draw_connection(mid, spi, ax, ctype='spillage')
            for P in self.modules[mid].pump_topo.keys():
                pmp_to = self.modules[mid].pump_topo[P][0]
                pmp_from = self.modules[mid].pump_topo[P][1]
                if pmp_to != mid:
                    self.draw_connection(mid, pmp_to, ax, ctype='pump')
                if pmp_from != mid:
                    self.draw_connection(mid, pmp_from, ax, ctype='pump')
        
        #Initialize dicts to hold module labels
        self.label_ID = {}
        self.label_name = {}
        self.label_plant = {}
        self.label_vol = {}
        self.label_MW = {}
        self.label_qmax = {}
        self.label_inflow = {}
        #self.label_unreg = {}
        self.label_pump = {}
        
        for mid in self.modules.keys():
            self._plot_module(mid, ax)
        self.populate_selected_labels(content=content)
        ax.legend(loc='lower right')
        if axtitle!="":
            ax.set_title(axtitle)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect(0.25)
        if to_file=="":
            plt.show()
        else:
            f.save_figure(to_file, bbox_inches='tight')
