"""
Version : 2.0
Author  : saukae.tan@amd.com
Desc    : extract training value from the log that is available
"""

import re
import sys
import os
import pandas as pd
import argparse
import glob
import numpy as np
import site
import shutil
from collections import defaultdict
from MDT.chseq import sort_text_by_channel_phy

def get_bios_hostname(base):
    bios = ""
    hostname = ""
    text = base.split("_")
    if len(text)>1:
        bios = text[0]
        hostname = text[1]      
    for item in text:
        if item.startswith("V"):
            bios = item
        if ("congo" in item) or ("morocco" in item):
            hostname = item
    return bios, hostname


def get_files_from_directory(directory):
    """Get all .csv files from the given directory."""
    csv_files = glob.glob(os.path.join(directory, "*.csv*"))
    print(csv_files)
    return csv_files


def convert_to_xy_dicts(coord_list):
    """
    Convert a list of [x, y] pairs into a list of {"x": x, "y": y} dictionaries.

    Args:
        coord_list (list): List of [x, y] coordinate pairs.

    Returns:
        list: List of {"x": x, "y": y} dictionaries.
    """
    return [{"x": x, "y": y} for x, y in coord_list]



def convert_qca_eye_to_named_variables(qca_eye):
        # Group keys by the first five elements (excluding dev)
        grouped = defaultdict(list)
        for key in qca_eye:
            group_key = key[:5]  # (soc, iod, ch, sub, rank)
            grouped[group_key].append(key)
        # Process each group
        results = {}
        for group_key, full_keys in grouped.items():
            soc, iod, ch, sub, rank = group_key
            var_name = f"QCAp{soc}i{iod}c{ch}s{sub}r{rank}_data"
            results[var_name] = [convert_to_xy_dicts(qca_eye[key]) for key in sorted(full_keys)]
        return results

import shutil
import os

def update_qca_html_from_results(results_dict, template_file="qca_eye.html", output_prefix="file"):
    for i, var_name in enumerate(results_dict.keys(), start=1):
        output_file = f"{output_prefix}{i}_qca.html"
        shutil.copy(template_file, output_file)
        with open(output_file, "r") as f:
            lines = f.readlines()
        replacement_line = f'const {var_name} = results["{var_name}"];\n'
        with open(output_file, "w") as f:
            for line in lines:
                if line.strip().startswith(f"const {var_name} = [...defaultData]"):
                    f.write(replacement_line)
                else:
                    f.write(line)



def compare_byte_sequence_by_group(dataset1, dataset2):
        # Group values by (channel, subchannel, rank)
        def group_by_channel(data):
            grouped = defaultdict(dict)
            for (soc, iod, ch, subch, rank, byte), val in data.items():
                grouped[(soc, iod, ch, subch, rank)][byte] = val
            return grouped
        grouped1 = group_by_channel(dataset1)
        grouped2 = group_by_channel(dataset2)
        # Compare each group
        mismatch_group={}
        for key in grouped1:
            if key not in grouped2:
                mismatch_group[key]="missing"
                continue    # Missing group in dataset2
            bytes1 = grouped1[key]
            bytes2 = grouped2[key]
            if set(bytes1.keys()) != set(bytes2.keys()):
                mismatch_group[key]="key mismatched" # Mismatched byte keys
                continue
            # Get sorted byte order based on values
            sorted_bytes1 = sorted(bytes1, key=lambda b: bytes1[b], reverse=True)
            sorted_bytes2 = sorted(bytes2, key=lambda b: bytes2[b], reverse=True)
            if sorted_bytes1 != sorted_bytes2:
                mismatch_group[key]=f"bytes mismatched:<br>WL   :{sorted_bytes1}<br>RxEN:{sorted_bytes2}" # Order mismatch
                continue
        return mismatch_group


def detect_DCS_DCA(filename):
    # Regex pattern to capture all relevant values
    ###rcd_pattern = re.compile(r"RCD Write Channel (\d+) SubChannel (\d+) Page (0x[0-9A-Fa-f]+) Register (0x[0-9A-Fa-f]+) Data (0x[0-9A-Fa-f]+)")
    ##CHANNEL: 7,  PHY: 1,  PHYINIT: [MemDdr5RcdWriteWrapper]SubChannel: 1, Dimm: 0 Page: 0x0 RW47 data is 0x13
    rcd_pattern = re.compile(
        r"CHANNEL:\s*([0-9]+),\s*PHY:\s*([0-9]+),\s*PHYINIT:\s*\[MemDdr5RcdWriteWrapper\]SubChannel:\s*([0-9]+),\s*Dimm:\s*([0-9]+)\s*Page:\s*(0x[0-9A-Fa-f]+)\s*RW([0-9A-Fa-f]+)\s*data is\s*(0x[0-9A-Fa-f]+)"
    )
    ##CHANNEL: 0,  PHY: 0,  PHYINIT: BTFW: [DCSDLYSW] min_dly: 54, max_dly: 172, dlyStep: 1 at dcs0
    ##CHANNEL: 0,  PHY: 0,  PHYINIT: BTFW: [DCSTM] vref = 45, winMax = 118, vref_w = 45, dly_g = 113
    dcs_dly_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DCSDLYSW\]\s*min_dly:\s*(\d+),\s*max_dly:\s*(\d+),\s*dlyStep:\s*(\d+)\s*at\s*dcs(\d+)"
    )
    dcs_vref_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DCSTM\]\s*vref\s*=\s*(\d+),\s*winMax\s*=\s*(\d+),\s*vref_w\s*=\s*(\d+),\s*dly_g\s*=\s*(\d+)"
    )
    ##CHANNEL: 7,  PHY: 1,  PHYINIT: BTFW: [DCADLYSW]: pin:7 left:266 right:309 window:43 dlystep:1 dly:159
    ##CHANNEL: 7,  PHY: 1,  PHYINIT: BTFW: [DCATM] vref = 19, win = 43,  winMax = 58, vref_w = 58, dly_g = 160
    dca_dly_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DCADLYSW\]:\s*pin:(\d+)\s*left:(\d+)\s*right:(\d+)\s*window:(\d+)\s*dlystep:(\d+)\s*dly:(\d+)"
    )
    dca_vref_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DCATM\]\s*vref\s*=\s*(\d+),\s*win\s*=\s*(\d+),\s*winMax\s*=\s*(\d+),\s*vref_w\s*=\s*(\d+),\s*dly_g\s*=\s*(\d+)"
    )
    # Dictionary to store the latest Data value for each unique (Channel, SubChannel, Page, Register)
    dcs_dly = {}
    dcs_vref = {}
    dcs_win = {}
    dcs_eye = {}
    dca_dly = {}
    dca_vref = {}
    dca_win = {}
    dca_eye = {}
    # Process each line in the log
    with open(filename, "r") as file:
        previous_line = ""
        dimm = 0
        for line in file:
            rcd_match = rcd_pattern.search(line)
            dcsvref_match = dcs_vref_pattern.search(line)
            if dcsvref_match:
                dcsdly_match = dcs_dly_pattern.search(previous_line)
                if dcsdly_match:
                    channel, subchannel, vref, winMax, vrefMax, delayMax = (
                        dcsvref_match.groups()
                    )
                    channel2, subchannel2, left, right, dcs_step, cs_pin = (
                        dcsdly_match.groups()
                    )
                    if channel == channel2 and subchannel == subchannel2:
                        dcs_key = (
                            int(channel),
                            int(subchannel),
                            int(dimm),
                            int(cs_pin),
                        )  # Unique key for each entry
                        dcs_dly[dcs_key] = int(delayMax)  # Store the latest occurrence
                        dcs_vref[dcs_key] = int(vrefMax)
                        if dcs_key not in dcs_eye:
                            dcs_eye[dcs_key] = []
                        dcs_eye[dcs_key].append([int(vref), int(left)])
                        dcs_eye[dcs_key].append([int(vref), int(right)])
                        dcs_win[dcs_key] = int(winMax)
            dcavref_match = dca_vref_pattern.search(line)
            if dcavref_match:
                dcadly_match = dca_dly_pattern.search(previous_line)
                if dcadly_match:
                    channel, subchannel, ca_pin, left, right, window, step, delay = (
                        dcadly_match.groups()
                    )
                    channel2, subchannel2, vref, window2, winMax, vrefMax, delayMax = (
                        dcavref_match.groups()
                    )
                    if channel == channel2 and subchannel == subchannel2:
                        dcadly_key = (
                            int(channel),
                            int(subchannel),
                            int(ca_pin),
                        )  # Unique key for each entry
                        dca_dly[dcadly_key] = int(
                            delayMax
                        )  # Store the latest occurrence
                        dcavref_key = (
                            int(channel),
                            int(subchannel),
                            int(dimm),
                            int(ca_pin),
                        )
                        dca_vref[dcavref_key] = int(vrefMax)
                        dcaeye_key = (
                            int(channel),
                            int(subchannel),
                            int(dimm),
                            int(ca_pin),
                        )
                        if dcaeye_key not in dca_eye:
                            dca_eye[dcaeye_key] = []
                        dca_eye[dcaeye_key].append([int(vref), int(left)])
                        dca_eye[dcaeye_key].append([int(vref), int(right)])
                        dca_win[dcavref_key] = int(winMax)
            else:
                if rcd_match:
                    (rcd_channel, rcd_subchannel, sub, dimm, page, register, value) = (
                        rcd_match.groups()
                    )
            previous_line = line
    return dcs_dly, dcs_vref, dcs_win, dcs_eye, dca_dly, dca_vref, dca_win, dca_eye

def process_wr_dq(prev, curr, header_pattern, subheader_pattern, data_pattern, dfe):
    result=[]
    header_match = header_pattern.search(prev[6])
    if not header_match:
        return []
    if dfe:
        channel, subchannel, rank, tap = header_match.groups()
    else:
        channel, subchannel, rank = header_match.groups()
    subheader_match = subheader_pattern.search(prev[5])
    if not subheader_match:
        return []
    channel2, subchannel2 = subheader_match.groups()
    if channel != channel2 or subchannel != subchannel2:
        return []
    for i in range(5):
        data_match = data_pattern.search(prev[i])
        if data_match:
            groups= data_match.groups()
            db = int(groups[2])
            if dfe:            
                result.extend([((int(channel), int(subchannel), int(rank), int(tap), db*8+j), int(groups[j+3])) for j in range(8)])
            else:
                result.extend([((int(channel), int(subchannel), int(rank), db*8+j), int(groups[j+3])) for j in range(8)])
    return result

def process_wr_nibble(prev, curr, header_pattern, subheader_pattern, data_pattern):
    result=[]
    header_match = header_pattern.search(prev[6])
    if not header_match:
        return []
    channel, subchannel, rank = header_match.groups()
    subheader_match = subheader_pattern.search(prev[5])
    if not subheader_match:
        return []
    channel2, subchannel2 = subheader_match.groups()
    if channel != channel2 or subchannel != subchannel2:
        return []
    for i in range(5):
        data_match = data_pattern.search(prev[i])
        if data_match:
            groups= data_match.groups()
            db = int(groups[2]) 
            result.extend([((int(channel), int(subchannel), int(rank), db*2+j), int(groups[j+3])) for j in range(2)])
    return result



def process_rd_lines(prev, curr, header_pattern, subheader_pattern, data_pattern, rdvref):
    result=[]
    header_match = header_pattern.search(prev[6])
    if not header_match:
        return []
    if rdvref:
        channel, subchannel = header_match.groups()
    else:
        channel, subchannel, rank = header_match.groups()
    subheader_match = subheader_pattern.search(prev[5])
    if not subheader_match:
        return []
    channel2, subchannel2 = subheader_match.groups()
    if channel != channel2 or subchannel != subchannel2:
        return []
    for i in range(5):
        data_match = data_pattern.search(prev[i])
        if data_match:
            groups= data_match.groups()
            db = int(groups[2]) 
            if rdvref:
                result.extend([((int(channel), int(subchannel), db*8+j), int(groups[j+4])) for j in range(8)])
            else:
                result.extend([((int(channel), int(subchannel), int(rank), db*8+j), int(groups[j+4])) for j in range(8)])
    return result


def process_mrlines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern):
        header_match = header_pattern.search(prev2)
        if not header_match:
            return []
        channel, subchannel, mr, rank = header_match.groups()
        subheader_match = subheader_pattern.search(prev1)
        if not subheader_match:
            return []
        channel2, subchannel2 = subheader_match.groups()
        if channel != channel2 or subchannel != subchannel2:
            return []
        data_match = data_pattern.search(curr)
        if not data_match:
            return []
        groups = data_match.groups()
        if len(groups) != 12 or groups[0] != channel or groups[1] != subchannel:
            return []
        # Return list of (key, value) tuples
        return [
            ((int(channel), int(subchannel), int(rank), int(mr), i), int(groups[i + 2], 16))
            for i in range(10)
        ]


def process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, hex_enable):
    header_match = header_pattern.search(prev2)
    if not header_match:
        return []

    channel, subchannel, rank = header_match.groups()

    subheader_match = subheader_pattern.search(prev1)
    if not subheader_match:
        return []

    channel2, subchannel2 = subheader_match.groups()

    if channel != channel2 or subchannel != subchannel2:
        return []

    data_match = data_pattern.search(curr)
    if not data_match:
        return []

    groups = data_match.groups()
    if len(groups) != 12 or groups[0] != channel or groups[1] != subchannel:
        return []

    # Return list of (key, value) tuples
    if hex_enable:
        return [
            ((int(channel), int(subchannel), int(rank), i), int(groups[i + 2], 16))
            for i in range(10)
        ]
    else:
        return [
            ((int(channel), int(subchannel), int(rank), i), int(groups[i + 2]))
            for i in range(10)
        ]

def detect_qca_rank(curr):
    rank_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*Rank:(\d+)\s*--->>"
    )
    rank_match = rank_pattern.search(curr)
    if rank_match:
        channel, subchannel, rank = rank_match.groups()
        return int(rank)
    return -1

def detect_qcs_eye_start(curr):
    start_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Cs\s*Eye\s*->>"
    )
    end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Qca\s*Eye\s*->>"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
        channel, subchannel = start_match.groups()
        key = (channel, subchannel)
        return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel = end_match.groups()
            key = (channel, subchannel)
            return key, False
    return (), False

def detect_qca_eye_start(curr):
    start_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Qca\s*Eye\s*->>"
    )
    end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*TxDQS\s*Coarse\s*Delay\s*>>"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
       channel, subchannel = start_match.groups()
       key = (channel, subchannel)
       return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel, r = end_match.groups()
            key = (channel, subchannel)
            return key, False
    return (), False


def process_qcs_eye(prev3, prev2, prev1, curr, qcs_start):
    #pattern definition
    dev_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*Rank:\s*(\d+),\s*Ch:\s*(\d+)\s*--->>"
    )
    offset_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*DelayOffset:\s*(\d+),\s*CenterDelay:\s*(\d+),\s*CenterVref:\s*(\d+)\s*--->>"
    )
    data_pattern=re.compile(
        r"Train Eye EyePts(.*?):(.*)"
    ) 
    #extract eye from log
    qcs_eye={}    
    match = dev_pattern.search(prev3)
    if match:
        ch, sub, r, _ch = match.groups()
        if (ch, sub) in qcs_start:
            if qcs_start[ch, sub]== True:
                match = offset_pattern.search(prev2)
                if match:
                    c, s, delayoffset, centerdelay, centervref = match.groups()
                    match = data_pattern.search(prev1)
                    if match:
                        eyepts, data= match.groups()
                        data2=[int(c) for c in data.split()]
                        if eyepts=='Upper':
                            qcs_eye[int(ch), int(sub), int(r)]=[[i+int(delayoffset), val] for i, val in enumerate(data2) if val != 0]
                        else:
                            qcs_eye[int(ch), int(sub), int(r)]=[[i+int(delayoffset), val] for i, val in enumerate(data2) if val != 255]
                        match = data_pattern.search(curr)
                        if match:
                            eyepts, data= match.groups()
                            data2=[int(c) for c in data.split()]
                            if eyepts=='Upper':
                                qcs_eye[int(ch), int(sub), int(r)].extend([[i+int(delayoffset), val] for i, val in enumerate(data2) if val != 0])
                            else:
                                qcs_eye[int(ch), int(sub), int(r)].extend([[i+int(delayoffset), val] for i, val in enumerate(data2) if val != 255]) 

    return qcs_eye

    
 
def process_qca_eye(prev3, prev2, prev1, curr, qca_start, rank):
    #pattern definition
    dev_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*Nb:(\d+)\s*--->>"
    )
    offset_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*DelayOffset:\s*NA,\s*CenterDelay:\s*NA,\s*CenterVref:\s*NA\s*--->>"
    )
    data_pattern=re.compile(
        r"Train Eye EyePts(.*?):(.*)"
    ) 
    #extract eye from log
    qca_eye={}    
    match = dev_pattern.search(prev3)
    if match:
        ch, sub, dev = match.groups()
        if (ch, sub) in qca_start:
            if qca_start[ch, sub]== True:
                match = offset_pattern.search(prev2)
                if match:
                    match = data_pattern.search(prev1)
                    if match:
                        eyepts, data= match.groups()
                        data2=[int(c) for c in data.split()]
                        if eyepts=='Upper':
                            qca_eye[int(ch), int(sub), int(rank), int(dev)]=[[i, val] for i, val in enumerate(data2) if val != 0]
                        else:
                            qca_eye[int(ch), int(sub), int(rank), int(dev)]=[[i, val] for i, val in enumerate(data2) if val != 255]
                        match = data_pattern.search(curr)
                        if match:
                            eyepts, data= match.groups()
                            data2=[int(c) for c in data.split()]
                            if eyepts=='Upper':
                                qca_eye[int(ch), int(sub), int(rank), int(dev)].extend([[i, val] for i, val in enumerate(data2) if val != 0])
                            else:
                                qca_eye[int(ch), int(sub), int(rank), int(dev)].extend([[i, val] for i, val in enumerate(data2) if val != 255]) 
    return qca_eye

def process_dcs_value(prev1, curr):
    result = []
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[DCS\]\s*<<\s*Rank:\s*(\d+),\s*VrefCS, CSCoarseDelay, CSFineDelay, Gain, Tap\s*>>"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[DCS\]\s*VrefCS\s*=\s*(\d+),\s*CSCoarseDelay\s*=\s*(\d+),\s*CSFineDelay\s*=\s*(\d+),\s*Gain\s*=\s*(\d+),\s*Tap1\s*=\s*(\d+),\s*Tap2\s*=\s*(\d+),\s*Tap3\s*=\s*(\d+),\s*Tap4\s*=\s*(\d+)"
    )
    match = header_pattern.search(prev1)
    if match:
        channel, subchannel, rank = match.groups()
        datamatch = data_pattern.search(curr)
        if datamatch:
            channel, subchannel, vref, coarse, fine, gain, tap1, tap2, tap3, tap4 = datamatch.groups()
            result = [((int(channel), int(subchannel), int(rank)),(int(vref), int(coarse),int(fine),int(gain),int(tap1),int(tap2),int(tap3),int(tap4)))]
    return result    

def process_dca_value(prev1, curr):
    result = []
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[DCA\]\s*<<\s*(\w+),\s*VrefCA, CACoarseDelay, CAFineDelay, Gain, Tap\s*>>"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[DCA\]\s*VrefCA\s*=\s*(\d+),\s*CACoarseDelay\s*=\s*(\d+),\s*CAFineDelay\s*=\s*(\d+),\s*Gain\s*=\s*(\d+),\s*Tap1\s*=\s*(\d+),\s*Tap2\s*=\s*(\d+),\s*Tap3\s*=\s*(\d+),\s*Tap4\s*=\s*(\d+),\s*Tap5\s*=\s*(\d+),\s*Tap6\s*=\s*(\d+)"
    )
    match = header_pattern.search(prev1)
    if match:
        channel, subchannel, ca = match.groups()
        datamatch = data_pattern.search(curr)
        if datamatch:
            channel, subchannel, vref, coarse, fine, gain, tap1, tap2, tap3, tap4, tap5, tap6 = datamatch.groups()
            result = [((int(channel), int(subchannel), ca),(int(vref), int(coarse),int(fine),int(gain),int(tap1),int(tap2),int(tap3),int(tap4),int(tap5),int(tap6)))]
    return result  

def process_qcs_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*Rank:\s*(\d+),\s*QACSDelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )   
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result

def process_qcs_vref(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*Rank:\s*(\d+),\s*VrefCS\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )   
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result


def process_qca_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*Rank:\s*(\d+),\s*QACADelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )      
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result

def process_qcavref_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*Rank:\s*(\d+),\s*VrefCA\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )      
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result

def process_wlcoarse_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*TxDQS\s*Coarse\s*Delay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )    
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_wlfine_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*TxDQS\s*Fine\s*Delay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )    
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_wlmr3_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*MR3\s*WICA\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )    
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_wlmr7_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*MR7\s*0.5tCK\s*Offset\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )    
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_rxen_coarse_line(prev2, prev1, curr):
    header_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW:\s*\[DBV_INFO\])?\s*<<\s*Rank:\s*(\d+),\s*RxEnCoarseDly\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW:\s*\[DBV_INFO\])?\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW:\s*\[DBV_INFO\])?\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_rxen_fine_line(prev2, prev1, curr):
    header_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW:\s*\[DBV_INFO\])?\s*<<\s*Rank:\s*(\d+),\s*RxEnFineDly\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW:\s*\[DBV_INFO\])?\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW:\s*\[DBV_INFO\])?\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_read_even_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*RXDQS Dpi_ClkTCode Even\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*Db\s*\|\s*Nb0Dq0\s*\|\s*Nb0Dq1\s*\|\s*Nb0Dq2\s*\|\s*Nb0Dq3\s*\|\s*Nb1Dq0\s*\|\s*Nb1Dq1\s*\|\s*Nb1Dq2\s*\|\s*Nb1Dq3"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )
    result = process_rd_lines(prev, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_read_odd_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*RXDQS Dpi_ClkCCode Odd\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*Db\s*\|\s*Nb0Dq0\s*\|\s*Nb0Dq1\s*\|\s*Nb0Dq2\s*\|\s*Nb0Dq3\s*\|\s*Nb1Dq0\s*\|\s*Nb1Dq1\s*\|\s*Nb1Dq2\s*\|\s*Nb1Dq3"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )
    result = process_rd_lines(prev, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result
    
def process_read_vref(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*<<\s*afe_RdacCtrl\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*Db\s*\|\s*Nb0Dq0\s*\|\s*Nb0Dq1\s*\|\s*Nb0Dq2\s*\|\s*Nb0Dq3\s*\|\s*Nb1Dq0\s*\|\s*Nb1Dq1\s*\|\s*Nb1Dq2\s*\|\s*Nb1Dq3"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )
    result = process_rd_lines(prev, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result

def process_write_nb_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*TxDqNibbleDelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Nb0\s*\|\s*Nb1\s*"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_wr_nibble(prev, curr, header_pattern, subheader_pattern, data_pattern)
    return result    

def process_write_coarse_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*TxDqCoarseDelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Dq0\s*\|\s*Dq1\s*\|\s*Dq2\s*\|\s*Dq3\s*\|\s*Dq4\s*\|\s*Dq5\s*\|\s*Dq6\s*\|\s*Dq7"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_wr_dq(prev, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_write_fine_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*TxDqFineDelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Dq0\s*\|\s*Dq1\s*\|\s*Dq2\s*\|\s*Dq3\s*\|\s*Dq4\s*\|\s*Dq5\s*\|\s*Dq6\s*\|\s*Dq7"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_wr_dq(prev, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result
    
def process_write_dfe(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*DFE BIAS Tap\s*(\d+)\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Dq0\s*\|\s*Dq1\s*\|\s*Dq2\s*\|\s*Dq3\s*\|\s*Dq4\s*\|\s*Dq5\s*\|\s*Dq6\s*\|\s*Dq7"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_wr_dq(prev, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result
    
def process_write_vref(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*DramVref\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Nb0\s*\|\s*Nb1\s*"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_wr_nibble(prev, curr, header_pattern, subheader_pattern, data_pattern)
    return result

def process_mr_reg(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_MR\]\s*<<\s*MR\s*(\d+),\s*Rank:\s*(\d+)\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_MR\]\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_MR\]\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )
    result = process_mrlines(prev[1], prev[0], curr, header_pattern, subheader_pattern, data_pattern)
    return result

def detect_decoded_log(filename, filename2=""):

    dcs_coarse_delay = {}
    dcs_fine_delay = {}
    dcs_vref = {}
    dcs_gain = {}
    dcs_tap1 = {}
    dcs_tap2 = {}
    dcs_tap3 = {}
    dcs_tap4 = {}
    
    dca_coarse_delay = {}
    dca_fine_delay = {}
    dca_vref = {}
    dca_gain = {}
    dca_tap1 = {}
    dca_tap2 = {}
    dca_tap3 = {}
    dca_tap4 = {}
    dca_tap5 = {}
    dca_tap6 = {}
        
    qcs_delay = {}
    qcs_vref = {}
    qca_delay = {}
    qca_vref = {}
    
    wlcoarse_value = {}
    wlfine_value = {}
    wlmr3_value = {}
    wlmr7_value = {}
    rxen_coarse_value = {}
    rxen_fine_value = {}
    
    readeven_delay = {}
    readodd_delay = {}
    read_vref = {}
    write_nb_delay = {}
    write_coarse_delay = {}
    write_fine_delay = {}
    write_vref = {}
    write_dfe_tap1 = {}
    write_dfe_tap2 = {}
    write_dfe_tap3 = {}
    write_dfe_tap4 = {}
    
    
    mr_reg = {}
    txrank = 0
    qcs_eye_start = {}
    qcs_eye={}
    qca_eye_start = {}
    qca_eye={}

    
    iod=0
    socket = 0
    valid_text=""
    valid_text2=""
    # Process each line in the log
    if filename:
        with open(filename, 'r') as file:
            # Read all lines from the file
            input_text = file.readlines()
        _, valid_text = sort_text_by_channel_phy(input_text)
    if filename2:
        with open(filename2, 'r') as file:
            # Read all lines from the file
            input_text2 = file.readlines()
        _, valid_text2 = sort_text_by_channel_phy(input_text2)
    
    if valid_text and valid_text2:
        split_index = len(valid_text)
        # Combine the tagged lines
        combine_text = valid_text2 + valid_text2
    elif valid_text:
        combine_text = valid_text
        iod= 0
    elif valid_text2:
        combine_text = valid_text2
        iod= 1
   
    rank=0
    previous_line = {}
    previous_line[7] = ""        
    previous_line[6] = ""
    previous_line[5] = ""
    previous_line[4] = ""
    previous_line[3] = ""
    previous_line[2] = ""
    previous_line[1] = ""
    previous_line[0] = ""   
    for idx, line in enumerate(combine_text):
        if valid_text and valid_text2:
            iod = 0 if idx < split_index else 1 
   
        qcs_key, qcs_start= detect_qcs_eye_start(line)
        if qcs_start:
            qcs_eye_start[qcs_key] = qcs_start
        # Get QCS eye value
        temp_qcs= process_qcs_eye(previous_line[2], previous_line[1], previous_line[0], line, qcs_eye_start)
        if temp_qcs:
            for key in temp_qcs:
                qcs_eye[socket, iod, key[0], key[1], key[2]] = temp_qcs[key] 
            
        qca_key, qca_start= detect_qca_eye_start(line)
        if qca_start:
            qca_eye_start[qca_key] = qca_start
        temp = detect_qca_rank(line)
        if temp>0:
            rank=temp
        # Get QCA eye value
        temp_qca= process_qca_eye(previous_line[2], previous_line[1], previous_line[0], line, qca_eye_start, rank)
        if temp_qca:
            for key in temp_qca:
                qca_eye[socket, iod, key[0], key[1], key[2], key[3]] = temp_qca[key]    
        # Get DCS value
        for key, value in process_dcs_value(previous_line[0], line):
            dcs_vref[socket, iod, key[0], key[1], key[2]] = value[0]
            dcs_coarse_delay[socket, iod, key[0], key[1], key[2]] = value[1]
            dcs_fine_delay[socket, iod, key[0], key[1], key[2]] = value[2]
            dcs_gain[socket, iod, key[0], key[1], key[2]] = value[3]
            dcs_tap1[socket, iod, key[0], key[1], key[2]] = value[4]
            dcs_tap2[socket, iod, key[0], key[1], key[2]] = value[5]
            dcs_tap3[socket, iod, key[0], key[1], key[2]] = value[6]
            dcs_tap4[socket, iod, key[0], key[1], key[2]] = value[7]


        # Get DCA delay
        for key, value in process_dca_value(previous_line[0], line):
            if key[2]=='CA0':
                dca=0
            elif key[2]=='CA1':
                dca=1
            elif key[2]=='CA2':
                dca=2
            elif key[2]=='CA3':
                dca=3
            elif key[2]=='CA4':
                dca=4
            elif key[2]=='CA5':
                dca=5
            elif key[2]=='CA6':
                dca=6
            elif key[2]=='PAR':
                dca=7
            
            dca_vref[socket, iod, key[0], key[1], dca] = value[0]
            dca_coarse_delay[socket, iod, key[0], key[1], dca] = value[1]
            dca_fine_delay[socket, iod, key[0], key[1], dca] = value[2]
            dca_gain[socket, iod, key[0], key[1], dca] = value[3]
            dca_tap1[socket, iod, key[0], key[1], dca] = value[4]
            dca_tap2[socket, iod, key[0], key[1], dca] = value[5]
            dca_tap3[socket, iod, key[0], key[1], dca] = value[6]
            dca_tap4[socket, iod, key[0], key[1], dca] = value[7]
            dca_tap5[socket, iod, key[0], key[1], dca] = value[8]
            dca_tap6[socket, iod, key[0], key[1], dca] = value[9]
        
        # Get QCS delay
        for key, value in process_qcs_line(previous_line[1], previous_line[0], line):
            qcs_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get QCS vref
        for key, value in process_qcs_vref(previous_line[1], previous_line[0], line):
            qcs_vref[socket, iod, key[0], key[1], key[2], key[3]] = value

        # Get QCA value
        for key, value in process_qca_line(previous_line[1], previous_line[0], line):
            qca_delay[socket, iod, key[0], key[1], key[2], key[3]] = value  
        # Get QCA Vref value
        for key, value in process_qcavref_line(previous_line[1], previous_line[0], line):
            qca_vref[socket, iod, key[0], key[1], key[2], key[3]] = value            
        # Get WL coarse value
        for key, value in process_wlcoarse_line(previous_line[1], previous_line[0], line):
            wlcoarse_value[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get WL fine value
        for key, value in process_wlfine_line(previous_line[1], previous_line[0], line):
            wlfine_value[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get WL MR3 value
        for key, value in process_wlmr3_line(previous_line[1], previous_line[0], line):
            wlmr3_value[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get WL MR7 value
        for key, value in process_wlmr7_line(previous_line[1], previous_line[0], line):
            wlmr7_value[socket, iod, key[0], key[1], key[2], key[3]] = value
       
        # Get RxEN Coarse value
        for key, value in process_rxen_coarse_line(previous_line[1], previous_line[0], line):
            rxen_coarse_value[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get RxEN Fine value
        for key, value in process_rxen_fine_line(previous_line[1], previous_line[0], line):
            rxen_fine_value[socket, iod, key[0], key[1], key[2], key[3]] = value

        # Get Read Even delay
        for key, value in process_read_even_delay(previous_line, line):
            readeven_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Read Odd delay
        for key, value in process_read_odd_delay(previous_line, line):
            readodd_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Read Vref
        for key, value in process_read_vref(previous_line, line):
            read_vref[socket, iod, key[0], key[1], key[2]] = value

        # Get Write Nibble Delay
        for key, value in process_write_nb_delay(previous_line, line):
            write_nb_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Write Coarse Delay
        for key, value in process_write_coarse_delay(previous_line, line):
            write_coarse_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Write Fine Delay
        for key, value in process_write_fine_delay(previous_line, line):
            write_fine_delay[socket, iod, key[0], key[1], key[2], key[3]] = value             
        # Get Write Vref
        for key, value in process_write_vref(previous_line, line):
            write_vref[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Write DFE
        for key, value in process_write_dfe(previous_line, line):
            if key[3]==1:
                write_dfe_tap1[socket, iod, key[0], key[1], key[2], key[4]] = value  
            elif key[3]==2:
                write_dfe_tap2[socket, iod, key[0], key[1], key[2], key[4]] = value  
            elif key[3]==3:
                write_dfe_tap3[socket, iod, key[0], key[1], key[2], key[4]] = value  
            elif key[3]==4:            
                write_dfe_tap4[socket, iod, key[0], key[1], key[2], key[4]] = value            
        # Get MR register
        for key, value in process_mr_reg(previous_line, line):
            mr_reg[socket, iod, key[0], key[1], key[2], key[3], key[4]] = value


        previous_line[7] = previous_line[6]        
        previous_line[6] = previous_line[5]
        previous_line[5] = previous_line[4]
        previous_line[4] = previous_line[3]
        previous_line[3] = previous_line[2]
        previous_line[2] = previous_line[1]
        previous_line[1] = previous_line[0]
        previous_line[0] = line    


    return (
            dcs_coarse_delay,
            dcs_fine_delay,
            dcs_vref,
            dcs_gain,
            dcs_tap1,
            dcs_tap2,
            dcs_tap3,
            dcs_tap4,
            dca_coarse_delay,
            dca_fine_delay,
            dca_vref,
            dca_gain,
            dca_tap1,
            dca_tap2,
            dca_tap3,
            dca_tap4,
            dca_tap5,
            dca_tap6,    
            qcs_delay,
            qcs_vref,
            qca_delay,
            qca_vref, 
            wlcoarse_value, 
            wlfine_value, 
            wlmr3_value, 
            wlmr7_value, 
            rxen_coarse_value, 
            rxen_fine_value, 
            qca_eye,
            qcs_eye,
            readeven_delay, 
            readodd_delay, 
            read_vref,
            write_nb_delay,
            write_coarse_delay,
            write_fine_delay,
            write_vref,
            write_dfe_tap1,
            write_dfe_tap2,
            write_dfe_tap3,
            write_dfe_tap3,
            mr_reg)



def process_data(data, mode):
    result = []
    for key, value in data.items():
        if mode=='dcs':
            soc, iod, channel, subchannel, rank = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "value/delay": value
            }
        elif mode=='dca' or mode=='readvref':
            soc, iod, channel, subchannel, dca = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "dev/pin": dca,
                "value/delay": value
            }
        elif mode=='mr_reg':
            soc, iod, channel, subchannel, rank, mr, dev = key
            entry = {
                "Param": f"MR_{mr}", 
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "dev/pin": dev,
                "value/delay": value
            }
        else:
            soc, iod, channel, subchannel, rank, dev = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "dev/pin": dev,
                "value/delay": value
            }
        result.append(entry)
    return result

def process_eyedata(data, mode):
    result = []
    for key, value in data.items():
        for delay, vref in data[key]:
            if mode=='qcs':
                soc, iod, channel, subchannel, rank = key
                entry = {
                    "Socket": soc,
                    "IOD": iod,  
                    "channel": channel,
                    "subchannel(phy)": subchannel,
                    "rank": rank,
                    "value/delay": delay,
                    "vref": vref
                }
            elif mode=='qca':
                soc, iod, channel, subchannel, rank, dev = key
                entry = {
                    "Socket": soc,
                    "IOD": iod,  
                    "channel": channel,
                    "subchannel(phy)": subchannel,
                    "rank": rank,
                    "dev/pin": dev,
                    "value/delay": delay,
                    "vref": vref
                }            
            result.append(entry)
    return result



def calculation(
    dcs_fine,
    dcs_coarse,
    dca_fine,
    dca_coarse,
    wlfine_value,
    wlcoarse_value,
    rxen_coarse_value,
    rxen_fine_value,
    readeven_delay,
    readodd_delay,
    write_nb_delay,
    write_coarse_delay,
    write_fine_delay
):
    missing_item=""
    # DCS
    dcs_result = {}
    for key, value in dcs_coarse.items():
        soc, iod, ch, sub, cs = key
        ##TxCsCoarseDly * 64 + stdqs_mdqs_dqsuTx[tc]_TxClkGenPiCode
        dcs_result[key] = (value * 64) + dcs_fine[key]
    # DCA
    dca_result = {}
    for key, value in dca_coarse.items():
        soc, iod, ch, sub, ca = key
        ##TxCaCoarseDly * 64 + stdqs_mdqs_dqtx[ul][0-3]_TxClkGenPiCode
        dca_result[key] = (value * 64) + dca_fine[key]
    # WL
    wl_result = {}
    for key, value in wlcoarse_value.items():
        soc, iod, ch, sub, r, db = key
        ##DqsCoarseDly * 64 + stdqs_mdqs_dqs[ul]Txt_TxClkGenPiCode
        if key in wlfine_value:
            wl_result[key] = (value * 64) + wlfine_value[key]
        else:
            missing_item+=f"<br>missing WL fine {key}<br>"
    # RxEN
    rxen_result = {}
    for key, value in rxen_coarse_value.items():
        soc, iod, ch, sub, r, db = key
        ##int(row['RxDqsCoarseDlyTg DqsCoarseDly'])*128 + np.floor((int(row[f'RXDQS_{ul.upper()}_RDGATE_DL_CTRL srdqs_mdqs_dqs{ul}_RdGateDlCoarseSel'])*16 + int(row[f'RXDQS_{ul.upper()}_RDGATE_DL_CTRL srdqs_mdqs_dqs{ul}_RdGateDlPiCode']))/4)
        if key in rxen_fine_value:
            rxen_result[key] = (value * 128) + np.floor((rxen_fine_value[key])/4)
        else:
            missing_item+=f"<br>missing RxEN fine {key}<br>"

    #read even    
    readeven_result = {}
    for key, value in readeven_delay.items():
        soc, iod, ch, sub, r, dq = key
        if value >= 64:
            readeven_result[key]= 128-value
        else:
            readeven_result[key]= value
    #read odd 
    readodd_result = {}
    for key, value in readodd_delay.items():
        soc, iod, ch, sub, r, dq = key
        if value >= 64:
            readodd_result[key]= 128-value
        else:
            readodd_result[key]= value
    #write delay
    write_result = {}
    for key, value in write_coarse_delay.items():
        soc, iod, ch, sub, r, dq = key
        n= int(dq/4)
        nb_key = (soc, iod, ch, sub, r, n)  #write_nb_delay
        ##(DqCoarseDly + CoarseDly) * 64 + stdqs_mdqs_dqtx[ul][0-3]_TxClkGenPiCode
        if key in write_fine_delay:
            if nb_key in write_nb_delay:
                write_result[key] = (
                    value + write_nb_delay[nb_key]
                ) * 64 + write_fine_delay[key]
            else:
                missing_item+=f"<br>missing TxDqNibbleDelay {key}<br>"
        else:
            missing_item+=f"<br>missing Write fine {key}<br>"
            
    return (
        dcs_result,
        dca_result,
        wl_result, 
        rxen_result,
        readeven_result,
        readodd_result,
        write_result,
        missing_item
    )        

def calculate_standard_deviation_and_range(analysis_csv):
    #initialize warning result
    warning_result=""
    
    # Step 1: Read the CSV data
    df_analysis = pd.read_csv(analysis_csv)
    # Ensure that the 'trained_value' column is included in the columns of interest

    # Step 2: Identify the columns related to 'trained_value' and runX (dynamically find columns that start with 'run')
    columns_of_interest = ["value/delay"] + [col for col in df_analysis.columns if col.startswith("run")]

    # Step 3: Iterate through each row and calculate the standard deviation and range
    df_analysis["standard_deviation"] = df_analysis[columns_of_interest].std(axis=1, ddof=0)
    df_analysis["range"] = df_analysis[columns_of_interest].max(axis=1) - df_analysis[columns_of_interest].min(axis=1)

    # Step 4 Add pass/fail if range >7
    df_analysis["Pass_Fail"] = df_analysis["range"].apply(lambda x: "Warning" if x > 7 else "Pass")

    # Step 5 Check if 'Param' is 'MRL' and 'trained_value' is not between 14 and 17 for all run columns
    # df_analysis["Pass_Fail"] = df_analysis.apply(
        # lambda row: "Fail" if (row["Param"] == "MRL" and not (14 <= row["trained_value"] <= 17)) else row["Pass_Fail"],
        # axis=1,
    # )
    # run_columns = [col for col in df_analysis.columns if col.startswith("run")]
    # df_analysis["Pass_Fail"] = df_analysis.apply(
        # lambda row: "Fail" if (row["Param"] == "MRL" and not all(14 <= row[col] <= 17 for col in run_columns)) else row["Pass_Fail"],
        # axis=1,
    # )

    # Step 6: Copy 'byte' value to new column 'nibble' for 'WL' or 'RXEN' params
    #df_analysis["nibble"] = df_analysis.apply(
    #    lambda row: row["nibble"] if row["Param"] in ["WL", "RXEN"] else "", axis=1
    #)
    # Step 7: Write the updated DataFrame back to the CSV
    df_analysis.to_csv(analysis_csv, index=False)

    # Step 8 Print out/return warning/all pass
    warning = df_analysis[df_analysis["Pass_Fail"] == "Warning"]

    # Step 9: Create a new DataFrame with the max of each range column for each param
    max_range_per_param = df_analysis.groupby("Param")["range"].max().reset_index()
    max_range_per_param.columns = ["Param", "Max Range"]

    # Print the new DataFrame
    warning_result += "Max range for each param:<br>"
    warning_result += max_range_per_param.to_string(index=False).replace("\n", "<br>")
    warning_result += "<br>"
    print("Max range for each param:")
    print(max_range_per_param)
    if not warning.empty:
        print("Warning rows:")
        print(warning)
        #warning_result += "Warning rows:<br>"
        #warning_result += warning.to_string(index=False).replace("\n", "<br>")
        #warning_result += "<br>"
        return warning, warning_result
    else:
        print("All Pass")
        warning_result+="<br>All Pass and no warning<br>"
        return None, warning_result


def process_decodedlog(
    filename, outputfile, run, inputbase, inputhost, inputbios, analysis_csv, filename2=""
):
    missing_printing=f""
    # dcs_dly, dcs_vref, dcs_win, dcs_eye, dca_dly, dca_vref, dca_win, dca_eye  = detect_DCS_DCA(filename)
    (
        dcs_coarse_delay,
        dcs_fine_delay,
        dcs_vref,
        dcs_gain,
        dcs_tap1,
        dcs_tap2,
        dcs_tap3,
        dcs_tap4,
        dca_coarse_delay,
        dca_fine_delay,
        dca_vref,
        dca_gain,
        dca_tap1,
        dca_tap2,
        dca_tap3,
        dca_tap4,
        dca_tap5,
        dca_tap6,    
        qcs_delay,
        qcs_vref,
        qca_delay,
        qca_vref, 
        wlcoarse_value, 
        wlfine_value, 
        wlmr3_value, 
        wlmr7_value, 
        rxen_coarse_value, 
        rxen_fine_value, 
        qca_eye,
        qcs_eye,
        readeven_delay, 
        readodd_delay, 
        read_vref,
        write_nb_delay,
        write_coarse_delay,
        write_fine_delay,
        write_vref,
        write_dfe_tap1,
        write_dfe_tap2,
        write_dfe_tap3,
        write_dfe_tap3,
        mr_reg
    ) = detect_decoded_log(filename, filename2)
    (
        dcs_result,
        dca_result,    
        wl_result, 
        rxen_result,
        readeven_result,
        readodd_result,
        write_result,
        missing_item
    ) = calculation(
        dcs_fine_delay,
        dcs_coarse_delay,
        dca_fine_delay,
        dca_coarse_delay,
        wlcoarse_value, 
        wlfine_value, 
        rxen_coarse_value, 
        rxen_fine_value,
        readeven_delay,
        readodd_delay,
        write_nb_delay,
        write_coarse_delay,
        write_fine_delay
    )
    wl_rxen_ordered_result=""
    result = compare_byte_sequence_by_group(wl_result, rxen_result)
    if result:
        wl_rxen_ordered_result = f"<br>{filename}:<br>(soc,iod,ch,sub,rank)"
        for key, value in result.items(): 
            wl_rxen_ordered_result += f"<br>{key}:<br>{value}"
        
    df_dcsdelay = process_data(dcs_result, 'dcs')
    df_dcsdelay = pd.DataFrame(df_dcsdelay)
    df_dcsdelay["Param"] = "DCS_Delay"
    df_dcsvref = process_data(dcs_vref, 'dcs')
    df_dcsvref = pd.DataFrame(df_dcsvref)
    df_dcsvref["Param"] = "DCS_Vref"
    df_dcsgain = process_data(dcs_gain, 'dcs')
    df_dcsgain = pd.DataFrame(df_dcsgain)
    df_dcsgain["Param"] = "DCS_Gain"
    df_dcstap1 = process_data(dcs_tap1, 'dcs')
    df_dcstap1 = pd.DataFrame(df_dcstap1)
    df_dcstap1["Param"] = "DCS_Tap1"
    df_dcstap2 = process_data(dcs_tap2, 'dcs')
    df_dcstap2 = pd.DataFrame(df_dcstap2)
    df_dcstap2["Param"] = "DCS_Tap2"
    df_dcstap3 = process_data(dcs_tap3, 'dcs')
    df_dcstap3 = pd.DataFrame(df_dcstap3)
    df_dcstap3["Param"] = "DCS_Tap3"
    df_dcstap4 = process_data(dcs_tap4, 'dcs')
    df_dcstap4 = pd.DataFrame(df_dcstap4)
    df_dcstap4["Param"] = "DCS_Tap4"

    df_dcadelay = process_data(dca_result, 'dca')
    df_dcadelay = pd.DataFrame(df_dcadelay)
    df_dcadelay["Param"] = "DCA_Delay"
    df_dcavref = process_data(dca_vref, 'dca')
    df_dcavref = pd.DataFrame(df_dcavref)
    df_dcavref["Param"] = "DCA_Vref"
    df_dcagain = process_data(dca_gain, 'dca')
    df_dcagain = pd.DataFrame(df_dcagain)
    df_dcagain["Param"] = "DCA_Gain"
    df_dcatap1 = process_data(dca_tap1, 'dca')
    df_dcatap1 = pd.DataFrame(df_dcatap1)
    df_dcatap1["Param"] = "DCA_Tap1"
    df_dcatap2 = process_data(dca_tap2, 'dca')
    df_dcatap2 = pd.DataFrame(df_dcatap2)
    df_dcatap2["Param"] = "DCA_Tap2"
    df_dcatap3 = process_data(dca_tap3, 'dca')
    df_dcatap3 = pd.DataFrame(df_dcatap3)
    df_dcatap3["Param"] = "DCA_Tap3"
    df_dcatap4 = process_data(dca_tap4, 'dca')
    df_dcatap4 = pd.DataFrame(df_dcatap4)
    df_dcatap4["Param"] = "DCA_Tap4"
    df_dcatap5 = process_data(dca_tap5, 'dca')
    df_dcatap5 = pd.DataFrame(df_dcatap4)
    df_dcatap5["Param"] = "DCA_Tap5"
    df_dcatap6 = process_data(dca_tap6, 'dca')
    df_dcatap6 = pd.DataFrame(df_dcatap6)
    df_dcatap6["Param"] = "DCA_Tap6"
    
    df_qcs = process_data(qcs_delay, 'qcs')
    df_qcs = pd.DataFrame(df_qcs)
    df_qcs["Param"] = "QAQCS_Delay"

    df_qcsvref = process_data(qcs_vref, 'qcs')
    df_qcsvref = pd.DataFrame(df_qcsvref)
    df_qcsvref["Param"] = "QCS_Vref"

    df_qca = process_data(qca_delay, 'qca')
    df_qca = pd.DataFrame(df_qca)
    df_qca["Param"] = "QAQCA_Delay"

    df_qcavref = process_data(qca_vref, 'qca')
    df_qcavref = pd.DataFrame(df_qcavref)
    df_qcavref["Param"] = "QCA_Vref"

    df_wl = process_data(wl_result, 'wl')
    df_wl = pd.DataFrame(df_wl)
    df_wl["Param"] = "WL_Value"

    df_wlmr3 = process_data(wlmr3_value, 'wl')
    df_wlmr3 = pd.DataFrame(df_wlmr3)
    df_wlmr3["Param"] = "WL_MR3"

    df_wlmr7 = process_data(wlmr7_value, 'wl')
    df_wlmr7 = pd.DataFrame(df_wlmr7)
    df_wlmr7["Param"] = "WL_MR7"    

    df_rxen = process_data(rxen_result, 'rxen')
    df_rxen = pd.DataFrame(df_rxen)
    df_rxen["Param"] = "RxEN_Value"

    df_readeven = process_data(readeven_result, 'rxeven')
    df_readeven = pd.DataFrame(df_readeven)
    df_readeven["Param"] = "Read_Even"
    
    df_readodd = process_data(readodd_result, 'rxodd')
    df_readodd = pd.DataFrame(df_readodd)
    df_readodd["Param"] = "Read_Odd"    

    df_readvref = process_data(read_vref, 'readvref')
    df_readvref = pd.DataFrame(df_readvref)
    df_readvref["Param"] = "Read_Vref(Rdac)"

    df_wrdelay = process_data(write_result, 'write')
    df_wrdelay = pd.DataFrame(df_wrdelay)
    df_wrdelay["Param"] = "Write_Delay"     

    df_wrvref = process_data(write_vref, 'write')
    df_wrvref = pd.DataFrame(df_wrvref)
    df_wrvref["Param"] = "Write_Vref"        

    df_wrdfetap1 = process_data(write_dfe_tap1, 'write')
    df_wrdfetap1 = pd.DataFrame(df_wrdfetap1)
    df_wrdfetap1["Param"] = "Write_DFE_Tap1"  

    df_wrdfetap2 = process_data(write_dfe_tap1, 'write')
    df_wrdfetap2 = pd.DataFrame(df_wrdfetap2)
    df_wrdfetap2["Param"] = "Write_DFE_Tap2" 

    df_wrdfetap3 = process_data(write_dfe_tap1, 'write')
    df_wrdfetap3 = pd.DataFrame(df_wrdfetap3)
    df_wrdfetap3["Param"] = "Write_DFE_Tap3" 

    df_wrdfetap4 = process_data(write_dfe_tap1, 'write')
    df_wrdfetap4 = pd.DataFrame(df_wrdfetap4)
    df_wrdfetap4["Param"] = "Write_DFE_Tap4"     

    df_mrreg = process_data(mr_reg, 'mr_reg')
    df_mrreg = pd.DataFrame(df_mrreg)

    
    df_qcseye = process_eyedata(qcs_eye, 'qcs')
    df_qcseye = pd.DataFrame(df_qcseye)
    df_qcseye["Param"] = "QCS_eye"

    df_qcaeye = process_eyedata(qca_eye, 'qca')
    df_qcaeye = pd.DataFrame(df_qcaeye)
    df_qcaeye["Param"] = "QCA_eye"
    
    df = pd.concat(
        [
            df_dcsdelay,
            df_dcsvref,
            df_dcsgain,
            df_dcstap1,
            df_dcstap2,
            df_dcstap3,
            df_dcstap4,
            df_dcadelay,
            df_dcavref,
            df_dcagain,
            df_dcatap1,
            df_dcatap2,
            df_dcatap3,
            df_dcatap4,
            df_dcatap5,
            df_dcatap6,
            df_qcs,
            df_qcsvref,
            df_qca,
            df_qcavref,
            df_wl,
            df_wlmr3,
            df_wlmr7,
            df_rxen,
            df_readeven,
            df_readodd,
            df_readvref,
            df_wrdelay,
            df_wrvref,
            df_wrdfetap1,
            df_wrdfetap2,
            df_wrdfetap3,
            df_wrdfetap4,
            df_mrreg,
            df_qcseye,
            df_qcaeye
        ]
    ).reset_index(drop=True)
    hstnme = [inputhost]
    bios = [inputbios]
    df["Hostname"] = hstnme * len(df)
    df["BIOS"] = bios * len(df)
    df["Filename"] = inputbase
    df["run"] = run

    ordered_columns = [
        "Filename",
        "Hostname",
        "BIOS",
        "Param",
        "Socket",
        "IOD",           
        "channel",
        "subchannel(phy)",
        "rank",
        "dev/pin",
        "value/delay",
        "vref",
        "run"
    ]

    df = df[ordered_columns]
    if os.path.exists(outputfile):
        df.to_csv(outputfile, mode="a", header=False, index=False)
    else:
        df.to_csv(outputfile, mode="w", header=True, index=False)    


    if analysis_csv:

        df_analysis = pd.concat(
            [
                df_dcsdelay,
                df_dcsvref,
                df_dcsgain,
                df_dcstap1,
                df_dcstap2,
                df_dcstap3,
                df_dcstap4,
                df_dcadelay,
                df_dcavref,
                df_dcagain,
                df_dcatap1,
                df_dcatap2,
                df_dcatap3,
                df_dcatap4,
                df_dcatap5,
                df_dcatap6,
                df_qcs,
                df_qcsvref,
                df_qca,
                df_qcavref,
                df_wl,
                df_wlmr3,
                df_wlmr7,
                df_rxen,
                df_readeven,
                df_readodd,
                df_readvref,
                df_wrdelay,
                df_wrvref,
                df_wrdfetap1,
                df_wrdfetap2,
                df_wrdfetap3,
                df_wrdfetap4,
                df_mrreg
            ]
        ).reset_index(drop=True)
        ordered_columns_analysis = [
            "Param",
            "Socket",
            "IOD",           
            "channel",
            "subchannel(phy)",
            "rank",
            "dev/pin",
            "value/delay"
        ]
        df_analysis = df_analysis[ordered_columns_analysis]

        if run == 0:
            df_analysis.to_csv(analysis_csv, mode="w", header=True, index=False)
        else:

            # Your unique identifying columns
            key_columns = ["Param", "Socket", "IOD", "channel", "subchannel(phy)", "rank", "dev/pin"]

            # Read existing analysis CSV
            df_analysis_existing = pd.read_csv(analysis_csv)

            # Create the new run column name
            run_column_name = f"run{run}"

            # Prepare a temp DataFrame with just keys + value
            df_update = df[key_columns + ["value/delay"]].copy()
            df_update = df_update.rename(columns={"value/delay": run_column_name})

            # Merge the new run values into the existing dataframe
            df_analysis_updated = pd.merge(
                df_analysis_existing,
                df_update,
                on=key_columns,
                how="left"
            )
            df_analysis_updated.to_csv(analysis_csv, mode="w", header=True, index=False)

            # If the run column already exists, update it only where non-null in new data
            if run_column_name in df_analysis_existing.columns:
                # Overwrite only where new value is not null
                df_analysis_updated[run_column_name] = df_analysis_updated[run_column_name + "_y"].combine_first(
                    df_analysis_updated[run_column_name + "_x"]
                )
                # Drop temporary columns
                df_analysis_updated.drop(columns=[run_column_name + "_x", run_column_name + "_y"], inplace=True)
            else:
                # No conflict, just keep the newly merged column
                pass

            # Save back to CSV
            ##df_analysis_updated.to_csv(analysis_csv, mode="w", header=True, index=False)
            print("skip")

            # df_analysis = pd.read_csv(analysis_csv)
            # trained_value_column = df["value/delay"]
            # run_column_name = f"run{run}"
            # df_analysis[run_column_name] = trained_value_column
            # df_analysis.to_csv(analysis_csv, mode="w", header=True, index=False)
    if missing_item:
        missing_printing+=f"file combination that have missing printing: <br>"
        missing_printing+=f"            iod0:{filename}<br>"
        missing_printing+=f"            iod1:{filename2}<br>"
        missing_printing+=missing_item
    return wl_rxen_ordered_result, missing_printing

def grouping_files(filelist):
    # Initialize groups
    grouped_files = defaultdict(dict)
    # Group files based on common prefix (before iodX)
    for filename in filelist:
        match = re.match(r"(.*)_iod(\d)\.parsed\.log", filename)
        if match:
            base = match.group(1)
            iod = match.group(2)
            grouped_files[base][f'iod{iod}'] = filename
    return grouped_files

def log_to_csv(inputlog, jmp_output, analysis_output):
    run = 0
    hostname = ""
    bios = ""
    ordered_result=""
    missing_print=""
    analysis_result=""
    merge= grouping_files(inputlog)
    if len(inputlog) >1:
        for path, iod_files in merge.items():
            iod0_file = iod_files.get("iod0")
            iod1_file = iod_files.get("iod1")
            if iod0_file:
                base = os.path.splitext(os.path.basename(iod0_file))[0]
            else:
                base = os.path.splitext(os.path.basename(iod1_file))[0]
            bios, hostname = get_bios_hostname(base)
            try:
                print(f"start log debug: {analysis_output}")
                ordering, missing=process_decodedlog(iod0_file, jmp_output, run, base, hostname, bios, analysis_output, iod1_file)
                ordered_result+=ordering
                missing_print+=missing
            except:
                print(f"LOG: Fail to process file: {iod0_file} & {iod1_file}" ) 
            run = run + 1
        try:
            _, analysis_result= calculate_standard_deviation_and_range(analysis_output)
        except:
            print("fail to calculate std deviation")

    else:
        base = os.path.splitext(os.path.basename(inputlog[0]))[0]
        bios, hostname = get_bios_hostname(base)
        ordering, missing=process_decodedlog(inputlog[0], jmp_output, run, base, hostname, bios, "")
        ordered_result+=ordering
        missing_print+=missing
    print("csv file generated")
    return ordered_result, missing_print, analysis_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training value Processing")
    parser.add_argument("log", help="log file to process", default=None)
    args = parser.parse_args()
    run = 0
    hostname = ""
    bios = ""
    if os.path.isdir(args.log):
        log_files = get_files_from_directory(args.log)
        newdir, ext = os.path.splitext(os.path.abspath(log_files[0]))
        base = os.path.splitext(os.path.basename(log_files[0]))[0]
        if not os.path.exists(newdir):
            os.mkdir(newdir)
        out_csv = os.path.join(newdir, f"{base}__log_consolidated_jmp.csv")
        analysis_csv = os.path.join(newdir, f"{base}_log_analysis.csv")
        for file in log_files:
            base = os.path.splitext(os.path.basename(file))[0]
            bios, hostname = get_bios_hostname(base)
            process_decodedlog(file, out_csv, run, base, hostname, bios, analysis_csv)
            run = run + 1
        calculate_standard_deviation_and_range(analysis_csv)
    else:
        if os.path.exists(args.log):
            newdir, ext = os.path.splitext(os.path.abspath(args.log))
            base = os.path.splitext(os.path.basename(args.log))[0]
            if not os.path.exists(newdir):
                os.mkdir(newdir)
            out_csv = os.path.join(newdir, f"{base}_log_consolidated_jmp.csv")
            bios, hostname = get_bios_hostname(base)
            process_decodedlog(args.log, out_csv, run, base, hostname, bios, "")
        else:
            sys.exit(f"File {args.log} does not exist")
    print("csv file generated")


