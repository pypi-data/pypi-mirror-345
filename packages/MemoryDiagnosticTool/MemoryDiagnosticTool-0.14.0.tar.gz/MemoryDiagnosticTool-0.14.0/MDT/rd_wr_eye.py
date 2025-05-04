"""
Author  : john.khor@amd.com
Desc    : Plot Read Write Data Eye at each training step that is available
"""
import os, re, argparse
import pandas as pd
import numpy as np
#from pylab import *
from matplotlib import pyplot
from matplotlib import patches
from matplotlib import animation
from matplotlib import cm
from PIL import Image



class Tempdata():
    prm  = None
    oe   = None
    ch   = None
    cs   = None
    phy  = None
    bit  = None
    base = [0,0]

ch_phy_info = re.compile("CHANNEL: ([0-9]+),  PHY: ([0-9]+),  PHYINIT: ")
mr10_hash = re.compile("BTFW:.*MR10\[dbyte(\d+).nibble(\d+)\]: 0x([0-9A-Fa-f]+)")
mr40_hash = re.compile("BTFW:.*MR40\[dbyte(\d+).nibble(\d+)\]: 0x([0-9A-Fa-f]+)")
mr40_hash = re.compile("BTFW:.*MR40.*Dbyte 0x(\d+), Nibble 0x(\d+), Mr40 0x(\d+),")

def serialize_data(log):
    chlogs = {i:[] for i in range(16)}
    with open(log, 'r') as ifh:
        for line in ifh.readlines():
            line = line.strip()
            match = ch_phy_info.search(line)
            if match:
                ch, phy = match.groups()
                chlogs[int(ch)].append(f"{line}")
    output = []
    for k, v in chlogs.items():
        for l in v:
            output.append(l)
    return output

def twos_comp(val, bits=7):
    if (val & (1 << (bits - 1))) != 0: 
        val = val - (1 << bits)
    return val 

def getmr10(datas):
    jedec_ref = [125-i for i in range(0x7f, -1,-1)]
    mr10_ref  = [i for i in range(0x7f,-1,-1)]
    txv = dict(zip(mr10_ref, jedec_ref))
    
    mr10_datas = {}
    for ch in range(8):
        for phy in range(2):
            for bit in range(40):
                ch_phy_bit = f"{ch}_{phy}_{bit}"
                mr10_datas.update({ch_phy_bit:0})
    for d in datas:
        match = ch_phy_info.search(d)
        if match:
            ch, phy = match.groups()
            ch = int(ch)
            phy = int(phy)
        match = mr10_hash.search(d)
        if match:
            db, nb, val = match.groups()
            db = int(db)
            nb = int(nb)
            val = txv[int(val, 16)&0x7F] # refer JEDEC SPEC MR10; index started from 35%
            for b in range(4):
                bit = (db*8)+(nb*4)+b
                ch_phy_bit = f"{ch}_{phy}_{bit}"
                mr10_datas[ch_phy_bit] = val
    return mr10_datas

def getmr40(datas):
    mr40_datas = {}
    for ch in range(8):
        for phy in range(2):
            for cs in range(4):
                for bit in range(40):
                    ch_phy_bit = f"{ch}_{phy}_{cs}_{bit}"
                    mr40_datas.update({ch_phy_bit:0})
    for d in datas:
        match = ch_phy_info.search(d)
        if match:
            ch, phy = match.groups()
            ch = int(ch)
            phy = int(phy)
        match = mr40_hash.search(d)
        if match:
            db, nb, val = match.groups()
            db = int(db)
            nb = int(nb)
            val = int(val, 16)
            for cs in range(4): # ranks
                for b in range(4): # bits per nibble
                    bit = (db*8)+(nb*4)+b
                    ch_phy_bit = f"{ch}_{phy}_{cs}_{bit}"
                    mr40_datas[ch_phy_bit] = val
    return mr40_datas

class RdScanState():
    def __init__(self, ch, phy, rk, db, bit):
        self.ch  = ch
        self.phy = phy
        self.rk  = rk
        self.db  = db
        self.bit = bit
        self.data = []
    def add_data(self, d):
        self.data.append(d)

class eyeState():
    def __init__(self, prm, ch, phy, cs, bit, oe, dly_offset, count = 0):
        # self.btsq = btsq
        self.prm  = prm
        self.oe   = oe
        self.ch   = ch
        self.cs   = cs
        self.phy  = phy
        self.bit  = bit
        self.dly_offset = dly_offset
        self.count = count
        self.data = {'Upper':{}, 'Lower':{}}
    def add_data(self, dir, data):
        self.data[dir].update({self.count//2:data})

# Class Function for Rd HW Accelerator Eye Scan
class Rd_Eye_Scan():
    def __init__(self, files, mdtpath):
        self.lane_info   = re.compile("BTFW:.*RDEYE Eye Scan\].*Rank = (\d+), Byte = (\d+), (.*?) Nibble, Lane = (\d+), Pi code start = ([0-9]+)")
        self.start_info  = re.compile("BTFW:.*RDEYE Eye Scan\].*lane_sel = (\d+), Pi offset = ([0-9]+)")
        # data_info   = re.compile("BTFW:.*RDEYE Eye Scan\].*Lane = (\d+), Vref[High|Low].*= ([0-9]+)", re.I)
        self.data_info = re.compile("BTFW:.*Rank = (\d), Byte = (\d), lane_sel = (\d), Lane = (\d), Vref(.*?) = ([0-9]+)", re.I)
        self.df_list = []
        self.files = files
        self._pic = False
        self._pch = False
        self._stat = True
        self._gif = False
        self._mdtpath = mdtpath        

    def get_data_frame(self, datas):
        data_struct = {'RawFile':[],\
                       'PRM':[],\
                       'CH':[],\
                       'PHY':[],\
                       'CS':[],\
                       'DB':[],\
                       'NIB':[],\
                       'DQ':[],\
                       'BIT':[],\
                       # 'Start_PI':[],\
                       'PI_Offset':[],\
                       'Vref_Offset':[]
                       }
        for d in datas:
            for t,v in d.data:
                nib = (d.bit//4)%2
                dq  = d.bit%4
                data_struct['RawFile'].append(self.rawfile)
                data_struct['PRM'].append('RD_Comp')
                data_struct['CH'].append(d.ch)
                data_struct['PHY'].append(d.phy)
                data_struct['CS'].append(d.rk)
                data_struct['DB'].append(d.db)
                data_struct['NIB'].append(nib)
                data_struct['DQ'].append(dq)
                data_struct['BIT'].append(d.bit)
                # data_struct['Start_PI'].append(d.pi_start)
                data_struct['PI_Offset'].append(t)
                data_struct['Vref_Offset'].append(v)
        return pd.DataFrame(data_struct)

    def calculate_1d(self, df):
        tbrl = {}
        prms = set(df.PRM)
        chs  = set(df.CH)
        phys = set(df.PHY)
        cs_s = set(df.CS)
        bits = set(df.BIT)
        for rf in set(df.RawFile):
            tbrl.update({rf:{}})
            for prm in prms:
                for c in chs:
                    for p in phys:
                        for r in cs_s:
                            for b in bits:
                                bit = f'{prm}_{c}_{p}_{r}_{b}'
                                tbrl[rf].update({bit:[]})
                                subdf = df[(df.RawFile==rf) & (df.PRM==prm) & (df.CH==c) & (df.PHY==p) & (df.CS==r) & (df.BIT==b)]                    
                                top, btm, lft, rgt = 999,999,999,999
                                if not subdf.empty:
                                    max_t = subdf.PI_Offset.max()
                                    min_t = subdf.PI_Offset.min()
                                    
                                    EW_l = subdf[subdf.Vref_Offset==0].PI_Offset.tolist()
                                    if len(EW_l)>0 :
                                        if 0 in EW_l:
                                            lft = rgt = 0
                                        else:
                                            rgt_list = subdf[(subdf.PI_Offset>0)&(subdf.Vref_Offset==0)].PI_Offset.tolist()
                                            lft_list = subdf[(subdf.PI_Offset<0)&(subdf.Vref_Offset==0)].PI_Offset.tolist()
                                            rgt = min(rgt_list) if len(rgt_list)>0 else max_t
                                            lft = max(lft_list) if len(lft_list)>0 else min_t
                                    else:
                                        rgt_list = subdf[(subdf.PI_Offset>0)&(subdf.Vref_Offset<3)&(subdf.Vref_Offset>-3)].PI_Offset.tolist()
                                        lft_list = subdf[(subdf.PI_Offset<0)&(subdf.Vref_Offset<3)&(subdf.Vref_Offset>-3)].PI_Offset.tolist()
                                        rgt = min(rgt_list) if len(rgt_list)>0 else max_t
                                        lft = max(lft_list) if len(lft_list)>0 else min_t
                                        
                                    EH_l = subdf[subdf.PI_Offset==0].Vref_Offset.tolist()
                                    if len(EH_l)>0 and not(0 in EH_l):
                                        top = subdf[(subdf.PI_Offset==0)].Vref_Offset.max()
                                        btm = subdf[(subdf.PI_Offset==0)].Vref_Offset.min()
                                else:
                                    top, btm, lft, rgt = 0,0,0,0
                                tbrl[rf].update({bit:[top, btm, rgt, lft]})
                                    
        df['Top'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][0]), axis = 1)
        df['Btm'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][1]), axis = 1)
        df['Rgt'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][2]), axis = 1)
        df['Lft'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][3]), axis = 1)

    def picture_dump_ch(self, df):
        col_code = cm.rainbow ## colour code
        rflist = list(set(df.RawFile))
        db_s = sorted(list(set(df.DB)))
        css  = sorted(list(set(df.CS)))
        bits = sorted(list(set(df.BIT)))
        phys = sorted(list(set(df.PHY)))
        chs  = sorted(list(set(df.CH)))
        nibs = [i for i  in range(10)]
        # grids = len(chs)*len(phys)*len(css)*len(nibs)
        grids = len(phys)*len(bits)
        cols = 8 # fix 8 columns
        rows = int(grids/cols)
        hspace = 0.95
        for rf in rflist:
            for ch in chs:                
                for cs in css:
                    cs = int(cs)
                    # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
                    ax = [i for i in range(rows*cols)]
                    pyplot.figure(figsize = (cols*3, rows*3))
                    pyplot.figtext(0.5, 0.99, f"CH{ch} Rank{cs} RD Eye Scan", fontsize=20, va='top', ha='center')
                    colours = col_code(np.linspace(0, 1, 4))
                    tlegend = [patches.Patch(color=c, label=f"dq{i}") for c,i in zip(colours, [0,1,2,3])]
                    for r in range(rows):
                        for c in range(cols):
                            i = r*(cols)+c
                            ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
                    # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #
                    i=0
                    for phy in phys:
                        ch = int(ch)
                        cs = int(cs)
                        phy = int(phy)
                        subset = df[(df.RawFile==rf) & (df.CH==ch) & (df.PHY==phy) & (df.CS==cs)]
                        xmin, xmax = subset.PI_Offset.min()-5, subset.PI_Offset.max()+5
                        ymin, ymax = subset.Vref_Offset.min()-5,  subset.Vref_Offset.max()+5
                        # ------------------------------ITERATE GRAPH CONSTRUCTION START ------------------------------ #
                        for bt in bits:
                            pyplot.axes(ax[i])
                            bt = int(bt)
                            db = int(bt//8)
                            nib = int((bt//4)%2)
                            pyplot.title(f'PHY{phy} CS{cs} DB{db} Nib{nib} DQ{bt%4}', fontsize = 10)
                            subset = df[(df.CH==ch) & (df.PHY==phy) & (df.BIT==bt)  & (df.CS==cs) & (df.RawFile==rf)]
                            pyplot.ylim(ymin, ymax); pyplot.yticks(np.arange(ymin, ymax, int((ymax-ymin)/10)))
                            pyplot.xlim(xmin, xmax); pyplot.xticks(np.arange(xmin, xmax, int((xmax-xmin)/10)))
                            pyplot.axhline(0, color='0.5', linestyle = ':', alpha = 0.5)
                            pyplot.axvline(0, color='0.5', linestyle = ':', alpha = 0.5)
                            ax[i].scatter(subset.PI_Offset, subset.Vref_Offset, color=colours[bt%4], s=20, alpha = 0.8, marker = '.')
                            # if bt%4 ==3: i+=1
                            i+=1
                        # ------------------------------ITERATE GRAPH CONSTRUCTION END ------------------------------- #
                    pyplot.tight_layout()
                    pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                    pyplot.subplots_adjust(top = hspace, right = 0.95)
                    # show()
                    # out_pic = os.path.join(dirname, f"{basename}_ReadEyeScan.jpg")
                    if self._mdtpath:
                        filename = os.path.basename(rf)
                        bn = filename.split('.')[0]
                        out_pic = os.path.join(self._mdtpath, f'{bn}_RD_Composite_CH{ch}_Rank{cs}.jpg')
                    else:
                        out_pic = os.path.splitext(rf)[0]+f'_RD_Composite_CH{ch}_Rank{cs}.jpg'
                    pyplot.savefig(out_pic)
                    pyplot.close()
                    

    def picture_dump(self, df):
        col_code = cm.rainbow ## colour code
        rflist = list(set(df.RawFile))
        db_s = sorted(list(set(df.DB)))
        css  = sorted(list(set(df.CS)))
        bits = sorted(list(set(df.BIT)))
        phys = sorted(list(set(df.PHY)))
        chs  = sorted(list(set(df.CH)))
        nibs = [i for i  in range(10)]
        # grids = len(chs)*len(phys)*len(css)*len(nibs)
        grids = len(chs)*len(phys)*len(css)*len(bits)
        cols = 8 # fix 8 columns
        rows = int(grids/cols)
        hspace = np.linspace(0.95, 0.98, 16)[len(chs)]
        for rf in rflist:
            # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
            ax = [i for i in range(rows*cols)]
            pyplot.figure(figsize = (cols*3, rows*3))
            pyplot.figtext(0.5, 0.99, f"RD Eye Scan", fontsize=20, va='top', ha='center')
            colours = col_code(np.linspace(0, 1, 4))
            tlegend = [patches.Patch(color=c, label=f"dq{i}") for c,i in zip(colours, [0,1,2,3])]
            for r in range(rows):
                for c in range(cols):
                    i = r*(cols)+c
                    ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
            # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #
            i = 0
            for ch in chs:
                for phy in phys:
                    for cs in css:
                        ch = int(ch)
                        phy = int(phy)
                        cs = int(cs)
                        subset = df[(df.RawFile==rf) & (df.CH==ch) & (df.PHY==phy) & (df.CS==cs)]
                        xmin, xmax = subset.PI_Offset.min()-5, subset.PI_Offset.max()+5
                        ymin, ymax = subset.Vref_Offset.min()-5,  subset.Vref_Offset.max()+5
                        # ------------------------------ITERATE GRAPH CONSTRUCTION START ------------------------------ #
                        for bt in bits:
                            bt = int(bt)
                            pyplot.axes(ax[i])
                            db = bt//8
                            nib = (bt//4)%2
                            pyplot.title(f'CH{ch} PHY{phy} CS{cs} DB{db} Nib{nib} DQ{bt%4}', fontsize = 10)
                            subset = df[(df.CH==ch) & (df.PHY==phy) & (df.BIT==bt)  & (df.CS==cs) & (df.RawFile==rf)]
                            pyplot.ylim(ymin, ymax); pyplot.yticks(np.arange(ymin, ymax, int((ymax-ymin)/10)))
                            pyplot.xlim(xmin, xmax); pyplot.xticks(np.arange(xmin, xmax, int((xmax-xmin)/10)))
                            pyplot.axhline(0, color='0.5', linestyle = ':', alpha = 0.5)
                            pyplot.axvline(0, color='0.5', linestyle = ':', alpha = 0.5)
                            ax[i].scatter(subset.PI_Offset, subset.Vref_Offset, color=colours[bt%4], s=20, alpha = 0.8, marker = '.')
                            # if bt%4 ==3: i+=1
                            i+=1
                        # ------------------------------ITERATE GRAPH CONSTRUCTION END ------------------------------- #
                        pyplot.tight_layout()
                        pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                        pyplot.subplots_adjust(top = hspace, right = 0.95)
                        # show()
            # out_pic = os.path.join(dirname, f"{basename}_ReadEyeScan.jpg")
            if self._mdtpath:
                filename = os.path.basename(rf)
                bn = filename.split('.')[0]
                out_pic = os.path.join(self._mdtpath, f'{bn}_RD_Composite.jpg')
            else:
                out_pic = os.path.splitext(rf)[0]+'_RD_Composite.jpg'
            pyplot.savefig(out_pic)
            pyplot.close()

    def process(self, srlz_data):
        header = re.compile("BTFW: \[RDEYE Eye\] (.*)")
        datas = []
        temp = Tempdata()
        ln_sel_ref = {0 : [3,1,6,7], 1 : [0,2,4,5]} 
        # temp = {}
        for line in srlz_data:
            line = line.strip()
            match = ch_phy_info.search(line)
            if match:
                ch, phy = match.groups()
                temp.ch = int(ch)
                temp.phy = int(phy)
            match = self.start_info.search(line)
            if match:
                ln_sel, pi_off = match.groups()
                temp.currpi = twos_comp(int(pi_off) & 0xFF, 8)
                continue
            match = self.data_info.search(line)
            if match:
                rk, db, ln_sel, ln, dir, _data = match.groups()
                rk = int(rk)
                db = int(db)
                ln = int(ln)
                ln_sel = int(ln_sel)
                ln = ln_sel_ref[ln_sel][ln]
                bit = (db*8)+ln
                dir = dir.strip().lower()
                _data = twos_comp(int(_data) & 0x1FF, 9)
                if (((dir == 'high') & (_data<0)) | ((dir == 'low') & (_data>0))): continue
                # if _data>=180 or _data<=-180: continue
                # print(f"CH{temp.ch} PHY{temp.phy} RK{rk} DB{d.db} Ln{d.ln}")
                if len(datas) == 0:
                    datas.append(RdScanState(temp.ch, temp.phy, rk, db, bit))
                    datas[0].add_data((temp.currpi, dir, _data))
                else:
                    found = False
                    for d in datas:
                        if (d.ch==temp.ch) and (d.phy==temp.phy) and (d.rk==rk) and (d.db==db) and (d.bit==bit):
                            d.add_data((temp.currpi, dir, _data))
                            found = True
                            break;
                    if not found:
                        d = RdScanState(temp.ch, temp.phy, rk, db, bit)
                        d.add_data((temp.currpi, dir, _data))
                        datas.append(d)
        return self.get_data_frame(datas)
        
    def main(self):
        basename = os.path.splitext(os.path.basename(self.files[0]))[0]
        if self._mdtpath:
            out_csv = os.path.join(self._mdtpath, f"{basename}_ReadEyeScan.csv")
            out_stat_csv = os.path.join(self._mdtpath, f"MDT_ReadScan_STAT.csv")        
        else:
            out_csv = os.path.join(dirname, f"{basename}_ReadEyeScan.csv")
            out_stat_csv = os.path.join(dirname, f"{basename}_ReadScan_STAT.csv")
        for f in self.files:
            try:
                self.df_list = []
                self.rawfile = f
                srlz_data = serialize_data(f)
                self.df_list.append(self.process(srlz_data))
                df = pd.concat(self.df_list)
                if not df.empty:
                    df.to_csv(out_csv, mode="w", header=True, index = False)
                    if self._stat:
                        self.calculate_1d(df)   
                        dfstat = df.drop_duplicates(subset = ["RawFile","PRM","PHY","CH","CS","BIT"])
                        dfstat = dfstat[["RawFile","PRM","PHY","CH","CS","DB","NIB","DQ","BIT","Top","Btm","Rgt","Lft"]]
                        dfstat = dfstat.copy()  # Create a copy of the DataFrame slice
                        # Get just the filenames
                        dfstat['Filename'] = dfstat['RawFile'].apply(lambda x: os.path.basename(x))
                        # Add the IOD column based on filename content
                        dfstat['IOD'] = dfstat['Filename'].apply(lambda x: 0 if 'iod0' in x else (1 if 'iod1' in x else None))
                        if os.path.exists(out_stat_csv):
                            dfstat.to_csv(out_stat_csv, mode="a", header=False, index = 0)
                        else:
                            dfstat.to_csv(out_stat_csv, mode="a", header=True, index = 0)
                    if self._pic | self._gif | self._pch:
                        print('Generating RD_EYE_SCAN Pictures....')
                        if self._pch:
                            self.picture_dump_ch(df)
                        if self._pic or (len(set(df.CH))>1):
                            self.picture_dump(df)
            except:
                print("[Rd Eye Scan]: Parssing error for file: ", f)

# Class Function for Rd Wr FW Vref/Timing Eye Scan
class Rd_Wr_Eye():
    def __init__(self, files, mdtpath):
        self.txswitchrank = re.compile("BTFW:.*\[WR TRAIN\] D5WrTrain.*training start rank ([0-9])")
        self.r_train_v_info = re.compile("BTFW:.*Read Train Vref: Rank 0x([0-9a-fA-F]+), Dbyte 0x([0-9a-fA-F]+), Nibble 0x([0-9a-fA-F]+), Dq 0x([0-9a-fA-F]+), Vref 0x([0-9a-fA-F]+)")
        self.r_train_d_info = re.compile("BTFW:.*Read Train Delays: Rank 0x([0-9a-fA-F]+), Dbyte 0x([0-9a-fA-F]+), Nibble 0x([0-9a-fA-F]+), Dq 0x([0-9a-fA-F]+), Phase 0x([0-9a-fA-F]+), PiCode 0x([0-9a-fA-F]+)")
        self.r_chinfo = re.compile("Dumping(.*?)Eyes for: Cs:(.*?), Dbyte:(.*?), Nibble:(.*?), Dq:(.*)")
        self.roe_info = re.compile('Dumping Rd Eyes for Delay/Vref (.*?) Phase')
        #self.w_chinfo = re.compile("Dumping(.*?)Eye for: Ch:(.*?), Db:(.*?), Dq:(.*)")
        self.w_chinfo = re.compile("PHYINIT:  <<--- Rank (.*?), DB: (.*?), Dq: (.*?) --->>")
        self.cntr_info = re.compile("-- DelayOffset: (.*?),.*CenterDelay:(.*?),.*CenterVref:(.*?)--" )
        self.data_cntr = re.compile("Train Eye EyePts(.*?):(.*)")
        self.btfw_seq = re.compile("BTFW:.*BTFWSEQ: TRAIN STEP:(.*?)Enabled: 1 Start.")
        self.read_base = re.compile("DAC Vref Step Size =\s*[0-9A-Fa-f].*Delay Step Size =\s*[0-9a-fA-F].*EyePtsLowerBase.*= ([0-9a-fA-F]+)\s*EyePtsUpperBase.*= ([0-9a-fA-F]+)")
        self.df_list = []
        self.eye_datas = {}
        self.files = files
        self._pic = False
        self._pch = False
        self._stat = True
        self._gif = False
        self._mdtpath = mdtpath
        
        self.ccc_info = re.compile("<<- 2D Eye Print,(.*?)Eye ->>")

    def get_rd_train(self, datas):
        rd_datas = {}
        for ch in range(8):
            for phy in range(2):
                for rk in range(4):
                    for bit in range(40):
                        ch_phy_bit = f"{ch}_{phy}_{rk}_{bit}"
                        rd_datas.update({ch_phy_bit:{}})
                        rd_datas[ch_phy_bit] = {'vref':0, 'pi':{'RD_odd':0,'RD_even':0}}
        for d in datas:
            match = ch_phy_info.search(d)
            if match:
                ch, phy = match.groups()
                ch = int(ch)
                phy = int(phy)
            match = self.r_train_v_info.search(d)
            if match:
                rk, db, nb, dq, vref = match.groups()
                rk = int(rk)
                db = int(db)
                nb = int(nb)
                dq = int(dq)
                bit = (db*8)+(nb*4)+dq
                if bit > 80: print(d)
                vref = int(vref, 16)
                ch_phy_bit = f"{ch}_{phy}_{rk}_{bit}"
                rd_datas[ch_phy_bit]['vref'] = vref
            match = self.r_train_d_info.search(d)
            if match:
                oe_ref = {0:'RD_odd',1:'RD_even'}
                rk, db, nb, dq, _ph, pi = match.groups()
                rk = int(rk)
                db = int(db)
                nb = int(nb)
                dq = int(dq)
                bit = (db*8)+(nb*4)+dq
                ph = oe_ref[int(_ph, 16)]
                pi = twos_comp(int(pi, 16) + 128)
                ch_phy_bit = f"{ch}_{phy}_{rk}_{bit}"
                rd_datas[ch_phy_bit]['pi'].update({ph:pi})
        return rd_datas

    def fill_eye(self, df):
        delays = sorted([i for i in set(df.DELAY)])
        eye_s = {'Vref':[], 'Delay':[]}
        for t in delays:
            vrefs = df[df.DELAY == t].VREF.tolist()
            if (len(vrefs)==0) or any([np.isnan(i) for i in vrefs]):
                eye_s['Vref'].append(0)
                eye_s['Delay'].append(0)
            else:
                for v in range(int(min(vrefs)), int(max(vrefs))):
                    eye_s['Vref'].append(v)
                    eye_s['Delay'].append(t)
        return pd.DataFrame(eye_s)

    def eyeCoM(self, df):
        CoM = {}
        prms = set(df.PRM)
        chs  = set(df.CH)
        phys = set(df.PHY)
        cs_s = set(df.CS)
        bits = set(df.BIT)
        for prm in prms:
            for c in chs:
                for p in phys:
                    for r in cs_s:
                        for b in bits:
                            subdf = df[(df.PRM==prm) & (df.CH==c) & (df.PHY==p) & (df.CS==r) & (df.BIT==b)]
                            if subdf.empty: continue
                            bit = f'{prm}_{c}_{p}_{r}_{b}'
                            eyedata = self.fill_eye(subdf)
                            if (len(subdf)<=2) or len(set(eyedata.Delay))<2 or len(set(eyedata.Vref))<2:
                                t_center = 0
                                v_center = 0
                            else:
                                weightedEH = 0; instantEH = 0
                                weightedEW = 0; instantEW = 0
                                delays = sorted([i for i in set(eyedata.Delay)])
                                for t in delays:
                                    edge = sorted(eyedata[eyedata.Delay == t].Vref.tolist())
                                    instantEH += edge[-1] - edge[0] 
                                    weightedEH += t*(edge[-1] - edge[0])
                                t_center = weightedEH / instantEH
                                vrefs = sorted([i for i in set(eyedata.Vref)])
                                for v in vrefs:
                                    edge = sorted(eyedata[eyedata.Vref == v].Delay.tolist())
                                    instantEW += edge[-1] - edge[0] 
                                    weightedEW += v*(edge[-1] - edge[0])
                                v_center = weightedEW / instantEW
                            CoM.update({bit:(t_center, v_center)})
        return CoM
    
    def construct_eye(self, prm, ch, phy, cs, bit, oddeven, dly_offset, dir, data_t, data_v):
        data = {'DELAY':data_t, 'VREF':data_v}
        if len(self.eye_datas)==0:
            eye = eyeState(prm, ch, phy, cs, bit, oddeven, dly_offset, 0)
            eye.add_data(dir, data)
            self.eye_datas = [eye]
        else:
            found = False
            for eye in self.eye_datas:
                if (eye.prm==prm and eye.ch==ch and eye.phy==phy and eye.cs==cs and eye.bit==bit and eye.oe==oddeven):
                    eye.count +=1
                    eye.add_data(dir, data)
                    found = True
                    break;
            if found == False:
                eye = eyeState(prm, ch, phy, cs, bit, oddeven, dly_offset, 0)
                eye.add_data(dir, data)
                self.eye_datas.append(eye)
    
    def make_df(self):
        data_dict = {'PRM':[],\
                     'CH':[],\
                     'PHY':[],\
                     'CS':[],\
                     'DB':[],\
                     'NIB':[],\
                     'DQ':[],\
                     'BIT':[],\
                     'MR40':[],\
                     'PRE_LAUNCH':[],\
                     'ERROR':[],\
                     'VREF':[],\
                     'DELAY':[],
                    }
        for e in self.eye_datas:
            prm = e.prm+e.oe
            _data_top = e.data['Upper']
            _data_btm = e.data['Lower']
            db = e.bit//8
            nb = (e.bit//4)%2
            dq = e.bit%4
            ch_phy_bit = f"{e.ch}_{e.phy}_{e.cs}_{e.bit}"
            prm_ch_phy_bit = f"{prm}_{e.ch}_{e.phy}_{e.cs}_{e.bit}"
            total_sets = sorted([i for i in set([i for i in _data_top] + [i for i in _data_btm])])
            missing_data = False
            eye_closed = []
            for s in total_sets:
                s = s%2                    
                ## ---------------------------------- CHECK MISSING INFO START -------------------------------- ##
                err_msg = ''
                err_template = 'ERROR on MR40={1} DQ{0}' if ('RD' in prm) else 'ERROR on DQ{0}'
                if (s not in _data_top) or (s not in _data_btm):
                    if (s not in _data_top) and (s not in _data_btm):
                        print(f'MISSING EYE CONTOUR: Set{s+1} {prm:<7} CH{e.ch:<2} PHY{e.phy:<2} CS{e.cs:<2} DB{db:<2} NB{nb:<2} DQ{dq:<2}')
                        dummy_data = {'VREF':[np.nan for i in range(62)],'DELAY':[np.nan for i in range(62)]}
                        _data_top[s] = dummy_data
                        _data_btm[s] = dummy_data
                    if (s not in _data_top) and (s in _data_btm): # Found Bottom, Top Missing
                        print(f'MISSING UPPER CONTOUR: Set{s+1} {prm:<7} CH{e.ch:<2} PHY{e.phy:<2} CS{e.cs:<2} DB{db:<2} NB{nb:<2} DQ{dq:<2}')
                        dummy_data = {'VREF':[np.nan for i in _data_btm[s]['VREF']],'DELAY':[i for i in _data_btm[s]['DELAY']]}
                        _data_top[s] = dummy_data
                    if (s not in _data_btm) and (s in _data_top): # Found Top, Bottom Missing
                        print(f'MISSING LOWER CONTOUR: Set{s+1} {prm:<7} CH{e.ch:<2} PHY{e.phy:<2} CS{e.cs:<2} DB{db:<2} NB{nb:<2} DQ{dq:<2}')
                        dummy_data = {'VREF':[np.nan for i in _data_top[s]['VREF']],'DELAY':[i for i in _data_top[s]['DELAY']]}
                        _data_btm[s] = dummy_data
                    missing_data = True
                    err_msg = err_template.format(dq, s)
                ## ---------------------------------- CHECK MISSING INFO END ---------------------------------- ##
                
                total_delay = sorted([i for i in set((_data_top[s]['DELAY'] + _data_btm[s]['DELAY']))])
                invalid_data_found = 0
                for i, t in enumerate(total_delay):
                    mr40_edge = t
                    self.mr40_stat[prm_ch_phy_bit] = {'edge':mr40_edge if (s and prm!='WR') else 0}
                    if t>127 and prm!='WR': break;
                    try:
                        top = _data_top[s]['VREF'][i]
                        btm = _data_btm[s]['VREF'][i]
                    except:
                        break
                    if (top > btm) or (missing_data):
                        if missing_data: top = btm = np.nan
                        data_dict['PRM'].extend([prm]*2)
                        data_dict['CH'].extend([e.ch]*2)
                        data_dict['PHY'].extend([e.phy]*2)
                        data_dict['CS'].extend([e.cs]*2)
                        data_dict['DB'].extend([db]*2)
                        data_dict['NIB'].extend([nb]*2)
                        data_dict['DQ'].extend([dq]*2)
                        data_dict['BIT'].extend([e.bit]*2)
                        data_dict['MR40'].extend([self.mr40_data[ch_phy_bit]]*2)
                        data_dict['ERROR'].extend([err_msg]*2)
                        data_dict['PRE_LAUNCH'].extend([s]*2)
                        data_dict['VREF'].extend([top, btm] )
                        data_dict['DELAY'].extend([t,  t])
                    elif (top < btm):
                        invalid_data_found += 1
                if invalid_data_found == len(total_delay):
                    eye_closed.append(s)
            if len(eye_closed) == len(total_sets):
                # print("CH{} PHY{} CS{} BIT{} S{} {} {} {}".format( e.ch, e.phy, e.cs, e.bit, s, prm, set(_data_top[s]['VREF']), set(_data_btm[s]['VREF'])))
                data_dict['PRM'].extend([prm]*2)
                data_dict['CH'].extend([e.ch]*2)
                data_dict['PHY'].extend([e.phy]*2)
                data_dict['CS'].extend([e.cs]*2)
                data_dict['DB'].extend([db]*2)
                data_dict['NIB'].extend([nb]*2)
                data_dict['DQ'].extend([dq]*2)
                data_dict['BIT'].extend([e.bit]*2)
                data_dict['MR40'].extend([self.mr40_data[ch_phy_bit]]*2)
                data_dict['ERROR'].extend([f'ERROR EYE CLOSED DQ{dq}']*2)
                data_dict['PRE_LAUNCH'].extend([s]*2)
                data_dict['VREF'].extend([np.nan, np.nan] )
                data_dict['DELAY'].extend([np.nan, np.nan])
        df = pd.DataFrame(data_dict)
        if not df.empty:
            df['RawFile'] = self.rawfile
            #df['Vref_Center'] = df.apply(lambda x: self.read_data.get(f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}", {}).get('vref', self.mr10_data.get(f"{x.CH}_{x.PHY}_{x.BIT}", 0)),axis=1)
            df['Vref_Center'] = df.apply(lambda x: self.read_data.get(f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}", {}).get('vref') if 'RD' in x.PRM else self.mr10_data.get(f"{x.CH}_{x.PHY}_{x.BIT}", 0),axis=1)
            df['Delay_Center'] = df.apply(lambda x: self.read_data.get(f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}", {}).get('pi', {}).get(x.PRM, 0) if ('RD' in x.PRM) else 0,axis=1)
            df['MR40_EDGE'] = df.apply(lambda x: self.mr40_stat.get(f"{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}", {}).get('edge', 0),axis=1)
            df['DELAY'] = df.apply(lambda x: (x.DELAY + x.MR40_EDGE) if (x.PRE_LAUNCH == 0 and x.PRM != 'WR') else x.DELAY,axis=1)
            df['Vref_Offset'] = df.VREF - df.Vref_Center
            df['PI_Offset'] = df.DELAY - df.Delay_Center
        return df

    def geteye(self, srlz_data):
        eyes = []
        count = 0
        cs = 0
        oddeven = ''
        self.mr40_stat = {}
        for prm in ['RD_odd', 'RD_even']:
            for ch in range(16):
                for phy in range(2):
                    for cs in range(4):
                        for bit in range(40):
                            self.mr40_stat[f"{prm}_{ch}_{phy}_{cs}_{bit}"] = {'edge':0}
        for content in srlz_data:
            content = content.strip()
            ## --------------------- GRAB CHANNEL PHY NUMBER --------------------------- #
            match = ch_phy_info.search(content)
            if match:
                ch, phy = match.groups()
                ch = int(ch)
                phy = int(phy)
            ## --------------------- GRAB READ ODD EVEN PHASE -------------------------- #
            match = self.roe_info.search(content)
            if match:
                oddeven = match.group(1).strip().lower()
                oddeven = '_'+oddeven
                continue
            ## --------------------- GRAB CURRENT CCC PIN INFORMATION ------------------ #
            match = self.ccc_info.search(content)
            if match:
                prm = match.group(1).strip().upper()
                continue
            ## --------------------- GRAB CURRENT READ PIN INFORMATION ----------------- #
            match = self.r_chinfo.search(content)
            if match:
                prm, cs, db, nb, dq = match.groups()
                prm = prm.strip().upper()
                cs = int(cs)
                bit = (int(db)*8) + (int(nb)*4) + int(dq)
                continue
            ## --------------------- GRAB TX TRAIN RANK INFORMATION -------------------- #
            match = self.txswitchrank.search(content)
            if match:
                cs = match.group(1)
                cs = int(cs)
                continue
            ## --------------------- GRAB CURRENT WRITE PIN INFORMATION ---------------- #
            match = self.w_chinfo.search(content)
            if match:
                _rank, db, dq = match.groups()
                prm = 'WR' #prm.strip().upper()
                oddeven = ''
                bit = (int(db)*8) + int(dq)            
                continue
            ## --------------------- GRAB TRAINED VALUE INFORMATION -------------------- #
            match = self.cntr_info.search(content)
            if match and prm in ['RD', 'WR']:
                dly_offset, dly_ctr, vref_ctr = match.groups()
                dly_ctr = int(dly_ctr)
                vref_ctr = int(vref_ctr)
                dly_offset = int(dly_offset)
                continue
            ## --------------------- GRAB READ BASE VALUE INFORMATION ------------------ #
            match = self.read_base.search(content)
            if match:
                lb, ub = match.groups()
                lb = int(lb)
                ub = int(ub)
                continue
            ## --------------------- GRAB RD WR EYE DATA ------------------------------- #
            match = self.data_cntr.search(content)
            if match and prm in ['RD', 'WR']:
                dir, data = match.groups()
                base = (lb if dir.upper() == 'LOWER' else ub) if prm=='RD' else 0
                data_v = [int(i)+base for i in data.split()]
                data_t = [dly_offset+i for i in range(len(data_v))]
                data_len = len(data)
                self.construct_eye(prm, ch, phy, cs, bit, oddeven, dly_offset, dir, data_t, data_v)
                continue

    def calculate_1d(self, df):
        # df['Vref_Offset'] = df.apply(lambda x: int(x.VREF) - int(x.Vref_Center), axis = 1)
        # df['PI_Offset']   = df.apply(lambda x: int(x.DELAY) - int(x.Delay_Center), axis = 1)
        tbrl = {}
        prms = set(df.PRM)
        chs  = set(df.CH)
        phys = set(df.PHY)
        cs_s = set(df.CS)
        bits = set(df.BIT)
        for rf in set(df.RawFile):
            tbrl.update({rf:{}})
            for prm in prms:
                for c in chs:
                    for p in phys:
                        for r in cs_s:
                            for b in bits:
                                bit = f'{prm}_{c}_{p}_{r}_{b}'
                                tbrl[rf].update({bit:[]})
                                subdf = df[(df.RawFile==rf) & (df.PRM==prm) & (df.CH==c) & (df.PHY==p) & (df.CS==r) & (df.BIT==b)]                    
                                top, btm, lft, rgt = 999,999,999,999
                                if not subdf.empty:
                                    max_t = subdf.PI_Offset.max()
                                    min_t = subdf.PI_Offset.min()
                                    
                                    EW_l = subdf[subdf.Vref_Offset==0].PI_Offset.tolist()
                                    if len(EW_l)>0 :
                                        if 0 in EW_l:
                                            lft = rgt = 0
                                        else:
                                            rgt_list = subdf[(subdf.PI_Offset>0)&(subdf.Vref_Offset==0)].PI_Offset.tolist()
                                            lft_list = subdf[(subdf.PI_Offset<0)&(subdf.Vref_Offset==0)].PI_Offset.tolist()
                                            rgt = min(rgt_list) if len(rgt_list)>0 else max_t
                                            lft = max(lft_list) if len(lft_list)>0 else min_t
                                    else:
                                        rgt_list = subdf[(subdf.PI_Offset>0)&(subdf.Vref_Offset<3)&(subdf.Vref_Offset>-3)].PI_Offset.tolist()
                                        lft_list = subdf[(subdf.PI_Offset<0)&(subdf.Vref_Offset<3)&(subdf.Vref_Offset>-3)].PI_Offset.tolist()
                                        rgt = min(rgt_list) if len(rgt_list)>0 else max_t
                                        lft = max(lft_list) if len(lft_list)>0 else min_t
                                        
                                    EH_l = subdf[subdf.PI_Offset==0].Vref_Offset.tolist()
                                    if len(EH_l)>0:
                                        if 0 in EH_l:
                                            top = btm = 0
                                        else:
                                            top = subdf[(subdf.PI_Offset==0)].Vref_Offset.max()
                                            btm = subdf[(subdf.PI_Offset==0)].Vref_Offset.min()
                                    else:
                                        max_v = subdf.Vref_Offset.max()
                                        min_v = subdf.Vref_Offset.min()
                                        top = max_v
                                        btm = min_v
                                else:
                                    top, btm, lft, rgt = 0,0,0,0
                                [top, btm, rgt, lft] = [(0 if np.isnan(i) else i) for i in [top, btm, rgt, lft]]
                                tbrl[rf].update({bit:[top, btm, rgt, lft]})
                                    
        df['Top'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][0]) , axis = 1)
        df['Btm'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][1]) , axis = 1)
        df['Rgt'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][2]) , axis = 1)
        df['Lft'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][3]) , axis = 1)

    def picture_dump_ch(self, df0):
        col_code = cm.Set1 ## colour code
        bits = [i for i in range(40)]#sorted(list(set(df.BIT)))
        nibs = [i for i  in range(10)]
        for rf in set(df0.RawFile):
            df = df0[df0.RawFile==rf]
            phys = sorted(list(set(df.PHY)))
            chs  = sorted(list(set(df.CH)))
            css  = sorted(list(set(df.CS)))
            hspace = 0.9
            grids = len(phys)*len(css)*len(nibs)
            cols = 10 # fix 10 columns
            rows = int(grids/cols)
            piclist = {c:[] for c in chs}
            for prm in set(df.PRM):
                for ch in chs:
                    # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
                    ax = [i for i in range(rows*cols)]
                    pyplot.figure(figsize = (cols*3, rows*3))
                    pyplot.figtext(0.5, 0.99, f"{prm:<8} CH{ch} Eye Plots", fontsize=20, va='top', ha='center')
                    colours = col_code(np.linspace(0, 1, len(nibs)))
                    tlegend = [patches.Patch(color=c, label=f"dq{i}") for c,i in zip(colours, [0,1,2,3])]
                    for r in range(rows):
                        for c in range(cols):
                            i = r*(cols)+c
                            ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
                    # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #
                    i = 0
                    for phy in phys:
                        for cs in css:
                            ch = int(ch)
                            phy = int(phy)
                            cs = int(cs)
                            if 'RD' in prm:
                                subset = df[(df.PRM==prm)]
                                xmin, xmax  = -127, 128
                                x_ticks = sorted([i for i in range(-127, 128, 20)]+[0])
                                x_labels = [str((i+127)%128) for i in x_ticks]
                                ymin = df[((df.PRM=='RD_odd')|(df.PRM=='RD_even')) & (df.CS==cs)].VREF.min() -10
                                ymax = df[((df.PRM=='RD_odd')|(df.PRM=='RD_even')) & (df.CS==cs)].VREF.max() +10
                                y_ticks = [i for i in range(int(ymin-10), int(ymax+10), 15)]
                            else:
                                subset = df[(df.PRM==prm) & (df.CS==cs)]
                                xmin, xmax = subset.DELAY.min(), subset.DELAY.max()
                                ymin, ymax = subset.VREF.min(),  subset.VREF.max()
                                x_ticks = [i for i in range(int(xmin-10), int(xmax+10), 10)]
                                x_labels = [str(i) for i in x_ticks]
                                y_ticks = [i for i in range(int(ymin-10), int(ymax+10), 10)]
                            for bit in bits:
                                #mr40edge = self.mr40_stat[f"{prm}_{ch}_{phy}_{cs}_{bit}"]['edge'] if prm!='WR' else 0
                                key = f"{prm}_{ch}_{phy}_{cs}_{bit}"
                                if prm != 'WR' and key in self.mr40_stat and 'edge' in self.mr40_stat[key]:
                                    mr40edge = self.mr40_stat[key]['edge']
                                else:
                                    mr40edge = 0
                                edge = mr40edge
                                pyplot.axes(ax[i])
                                db = bit//8
                                nib = (bit//4)%2
                                subset = df[(df.PRM==prm) & (df.CH==ch) & (df.CS==cs) & (df.PHY==phy) & (df.DB==db) & (df.NIB==nib)]
                                err_msg = '\n'.join([j for j in [i for i in set(subset.ERROR.to_list())] if j.strip()!=''])
                                pyplot.title(f'CH{ch} PHY{phy} CS{cs} DB{db} Nib{nib}', fontsize = 10)
                                subset = df[(df.PRM==prm) & (df.CH==ch) & (df.CS==cs) & (df.PHY==phy) & (df.BIT==bit)]
                                v_center = np.mean(subset.Vref_Center)
                                t_center = np.mean(subset.Delay_Center) - (edge)
                                pyplot.ylim(ymin, ymax); pyplot.yticks(y_ticks)
                                pyplot.xlim(xmin, xmax); pyplot.xticks(x_ticks, x_labels, rotation =90)
                                pyplot.axvline(0,        color='k',   linestyle = ':', alpha = 0.5, label = 'MR40=0')
                                pyplot.axhline(v_center, color='0.5', linestyle = ':', alpha = 0.3)
                                pyplot.axvline(t_center, color='0.5', linestyle = ':', alpha = 0.3)
                                ax[i].scatter(t_center, v_center, color=colours[bit%4], marker = '*', s = 30)
                                x_values = subset.DELAY - (edge)
                                y_values = subset.VREF
                                ax[i].text(xmin, ymin, err_msg, va='bottom', ha='left', color = 'r', fontsize = 10)
                                ax[i].scatter(x_values, y_values, color=colours[bit%4], s=20, alpha = 0.5, marker = '.')
                                if bit%4 ==3: i+=1
                    pyplot.tight_layout()
                    pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                    pyplot.subplots_adjust(top = hspace, right = 0.95)
                    # show()
                    if self._mdtpath:
                        filename = os.path.basename(rf)
                        bn = filename.split('.')[0]
                        out_pic = os.path.join(self._mdtpath, f'{bn}_{prm}_CH{ch}.jpg')
                    else:
                        out_pic = os.path.splitext(rf)[0]+f'_{prm}_CH{ch}.jpg'
                    pyplot.savefig(out_pic)
                    #if 'RD' in prm: #only append pic list because wanted to looks at the odd even swapping gif
                    #    piclist[ch].append(out_pic)
                    pyplot.close()
            if self._gif:
                for ch, pictures in piclist.items():
                    if pictures==[]: continue
                    self.make_gif(pictures, rf, ch)

    def picture_dump(self, df0):
        col_code = cm.Set1 ## colour code
        bits = [i for i in range(40)]#sorted(list(set(df.BIT)))
        nibs = [i for i  in range(10)]
        for rf in set(df0.RawFile):
            df = df0[df0.RawFile==rf]
            phys = sorted(list(set(df.PHY)))
            chs  = sorted(list(set(df.CH)))
            css  = sorted(list(set(df.CS)))
            hspace = np.linspace(0.95, 0.98, 16)[len(chs)]
            grids = len(chs)*len(phys)*len(css)*len(nibs)
            cols = 10 # fix 10 columns
            rows = int(grids/cols)
            piclist = []
            for prm in set(df.PRM):
                # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
                ax = [i for i in range(rows*cols)]
                pyplot.figure(figsize = (cols*3, rows*3))
                pyplot.figtext(0.5, 0.99, f"{prm:<8} Eye Plots", fontsize=20, va='top', ha='center')
                colours = col_code(np.linspace(0, 1, len(nibs)))
                tlegend = [patches.Patch(color=c, label=f"dq{i}") for c,i in zip(colours, [0,1,2,3])]
                for r in range(rows):
                    for c in range(cols):
                        i = r*(cols)+c
                        ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
                # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #
                # ------------------------------ITERATE GRAPH CONSTRUCTION START ------------------------------ #
                i = 0
                for ch in chs:
                    for phy in phys:
                        for cs in css:
                            if 'RD' in prm:
                                subset = df[(df.PRM==prm)]
                                xmin, xmax  = -127, 128
                                x_ticks = sorted([i for i in range(-127, 128, 20)]+[0])
                                x_labels = [str((i+127)%128) for i in x_ticks]
                                ymin = df[((df.PRM=='RD_odd')|(df.PRM=='RD_even')) & (df.CS==cs)].VREF.min() -10
                                ymax = df[((df.PRM=='RD_odd')|(df.PRM=='RD_even')) & (df.CS==cs)].VREF.max() +10
                                y_ticks = [i for i in range(int(ymin-10), int(ymax+10), 15)]
                            else:
                                subset = df[(df.PRM==prm) & (df.CS==cs)]
                                xmin, xmax = subset.DELAY.min(), subset.DELAY.max()
                                ymin, ymax = subset.VREF.min(),  subset.VREF.max()
                                x_ticks = [i for i in range(xmin-10, xmax+10, 10)]
                                x_labels = [str(i) for i in x_ticks]
                                y_ticks = [i for i in range(int(ymin-10), int(ymax+10), 10)]
                            for bit in bits:
                                #mr40edge = self.mr40_stat[f"{prm}_{ch}_{phy}_{cs}_{bit}"]['edge'] if prm != 'WR' else 0
                                key = f"{prm}_{ch}_{phy}_{cs}_{bit}"
                                if prm != 'WR' and key in self.mr40_stat and 'edge' in self.mr40_stat[key]:
                                    mr40edge = self.mr40_stat[key]['edge']
                                else:
                                    mr40edge = 0
                                edge = mr40edge
                                pyplot.axes(ax[i])
                                db = bit//8
                                nib = (bit//4)%2
                                subset = df[(df.PRM==prm) & (df.CH==ch) & (df.CS==cs) & (df.PHY==phy) & (df.DB==db) & (df.NIB==nib)]
                                err_msg = '\n'.join([j for j in [i for i in set(subset.ERROR.to_list())] if j.strip()!=''])
                                pyplot.title(f'CH{ch} PHY{phy} CS{cs} DB{db} Nib{nib}', fontsize = 10)
                                subset = df[(df.PRM==prm) & (df.CH==ch) & (df.CS==cs) & (df.PHY==phy) & (df.BIT==bit)]
                                v_center = np.mean(subset.Vref_Center)
                                t_center = np.mean(subset.Delay_Center) - (edge)
                                pyplot.ylim(ymin, ymax); pyplot.yticks(y_ticks)
                                pyplot.xlim(xmin, xmax); pyplot.xticks(x_ticks, x_labels, rotation =90)
                                pyplot.axvline(0,        color='k',   linestyle = ':', alpha = 0.5, label = 'MR40=0')
                                pyplot.axhline(v_center, color='0.5', linestyle = ':', alpha = 0.3)
                                pyplot.axvline(t_center, color='0.5', linestyle = ':', alpha = 0.3)
                                ax[i].text(xmin, ymin, err_msg, va='bottom', ha='left', color = 'r', fontsize = 10)
                                ax[i].scatter(t_center, v_center, color=colours[bit%4], marker = '*', s = 30)
                                x_values = subset.DELAY - (edge)
                                y_values = subset.VREF
                                ax[i].scatter(x_values, y_values, color=colours[bit%4], s=20, alpha = 0.5, marker = '.')
                                if bit%4 ==3: i+=1
                # ------------------------------ITERATE GRAPH CONSTRUCTION END ------------------------------- #
                pyplot.tight_layout()
                pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                pyplot.subplots_adjust(top = hspace, right = 0.95)
                # show()
                if self._mdtpath:
                    filename = os.path.basename(rf)
                    bn = filename.split('.')[0]
                    out_pic = os.path.join(self._mdtpath, f'{bn}_{prm}.jpg')
                else:
                    out_pic = os.path.splitext(rf)[0]+f'_{prm}.jpg'
                pyplot.savefig(out_pic)
                #if 'RD' in prm: #only append pic list because wanted to looks at the odd even swapping gif
                #    piclist.append(out_pic)
                pyplot.close()
            if self._gif:
                print('Making GIF...')
                self.make_gif(piclist, rf)

    def make_gif(self, piclist, gifname, ch = None):
        frames = [Image.open(image) for image in piclist]
        frame_one = frames[0]
        if self._mdtpath:
            filename = os.path.basename(gifname)
            bn = filename.split('.')[0]
            if (ch == None):
                out_gif = os.path.join(self._mdtpath, f'{bn}_RD.gif')
            else:
                out_gif = os.path.join(self._mdtpath, f'{bn}_RD_CH{ch}.gif')      
        else:
            if (ch == None):
                out_gif = os.path.splitext(gifname)[0]+'_RD.gif'
            else:
                out_gif = os.path.splitext(gifname)[0]+f'_RD_CH{ch}.gif'
        frame_one.save(out_gif, format="GIF", append_images=frames,  save_all=True, duration=800, loop=1000)

    def main(self):
        if self._mdtpath:
            out_stat_csv = os.path.join(self._mdtpath, f"MDT_RW_Eye_STAT.csv")        
        else:               
            out_stat_csv = os.path.join(dirname, f"{basename}_RW_Eye_STAT.csv")       
        for f in self.files:
            try:
                base = os.path.splitext(os.path.basename(f))[0]
                dfstat = []
                self.df_list = []
                self.rawfile = f
                srlz_data = serialize_data(f)
                self.read_data = self.get_rd_train(srlz_data)
                self.mr10_data = getmr10(srlz_data)
                self.mr40_data = getmr40(srlz_data)
                self.geteye(srlz_data)
                self.df_list.append(self.make_df())
                df = pd.concat(self.df_list)
                if not(df.empty):
                    if self._stat: 
                        eyecom = self.eyeCoM(df)
                        df['Delay_Center'] = df.apply(lambda x: int(eyecom[f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][0]) if (x.PRM=='WR') else x.Delay_Center, axis = 1)
                        self.calculate_1d(df)   
                        dfstat = df.drop_duplicates(subset = ["RawFile","PRM","PHY","CH","CS","BIT"])
                        dfstat = dfstat[["RawFile","PRM","PHY","CH","CS","DB","NIB","DQ","BIT","Vref_Center","Delay_Center","Top","Btm","Rgt","Lft"]]                        
                        dfstat = dfstat.copy()  # Create a copy of the DataFrame slice
                        # Get just the filenames
                        dfstat['Filename'] = dfstat['RawFile'].apply(lambda x: os.path.basename(x))
                        # Add the IOD column based on filename content
                        dfstat['IOD'] = dfstat['Filename'].apply(lambda x: 0 if 'iod0' in x else (1 if 'iod1' in x else None))
                        if os.path.exists(out_stat_csv):
                            dfstat.to_csv(out_stat_csv, mode="a", header=False, index = 0)
                        else:
                            dfstat.to_csv(out_stat_csv, mode="a", header=True, index = 0)
                    if self._mdtpath:
                        out_csv = os.path.join(self._mdtpath, f"{base}_RW_Eye.csv")
                    else:
                        out_csv = os.path.join(dirname, f"{base}_RW_Eye.csv")
                    df.to_csv(out_csv, mode="w", header=True, index = False)
                    if self._pic | self._gif | self._pch:
                        print('Generating RD_WR_EYE Pictures....')
                        if self._pch:
                            self.picture_dump_ch(df)
                        if self._pic or (len(set(df.CH))>1) or self._gif:
                            self.picture_dump(df)
            except:
                print("[Rd Wr Eye]: Parssing error for file: ", f) 
            
        # sys.exit() ## JOHN
        
        

def _parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("log",                 help = "Path Contains Log or logfile", type = str)
    parser.add_argument("--stat",       '-s',  help = "Statistic Summary",            action='store_true')
    parser.add_argument("--picture",    '-p',  help = "Dump Picture",                 action='store_true')
    parser.add_argument("--pic_per_ch", '-pch',help = "Dump Picture Per Channel",     action='store_true')
    parser.add_argument("--gif",        '-g',  help = "Dump GIF Image",               action='store_true')
    return parser.parse_args()

if __name__ == "__main__":
    file = _parse().log
    _pic = _parse().picture
    _pch = _parse().pic_per_ch
    _stat = _parse().stat
    _gif  = _parse().gif
    if os.path.exists(file):
        if os.path.isfile(file):
            dirname  = os.path.dirname(file)
            files = [file]
        elif os.path.isdir(file):
            dirname  = file
            files = [os.path.join(dirname, i) for i in os.listdir(file) if i.endswith('.log')]
    else:
        sys.exit("File Not Exists!")
    basename = os.path.splitext(os.path.basename(file))[0]
    rd_wr = Rd_Wr_Eye(files, "")
    rd_scan = Rd_Eye_Scan(files, "")
    rd_wr.main()
    rd_scan.main()