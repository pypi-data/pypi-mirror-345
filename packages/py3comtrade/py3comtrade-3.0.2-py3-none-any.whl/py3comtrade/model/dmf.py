from dataclasses import dataclass, field
from typing import List, Optional
import xml.etree.ElementTree as ET

from openpyxl.descriptors import namespace


# 定义数据类
@dataclass
class AnalogChannel:
    idx_cfg: int
    idx_org: int
    type: str
    flag: str
    freq: int
    au: float
    bu: float
    sIUnit: str
    multiplier: Optional[str]
    primary: int
    secondary: int
    ps: str
    idx_rlt: int
    ph: str

@dataclass
class StatusChannel:
    idx_cfg: int
    idx_org: int
    type: str
    flag: str
    contact: str
    srcRef: str

@dataclass
class ACVChn:
    ua_idx: int
    ub_idx: int
    uc_idx: int
    un_idx: int
    ul_idx: int

@dataclass
class StaChn:
    idx_cfg: int

@dataclass
class RX:
    r1: float
    x1: float
    r0: float
    x0: float

@dataclass
class CG:
    c1: float
    c0: float
    g1: float
    g0: float

@dataclass
class PX:
    px: float
    px0: float

@dataclass
class MR:
    idx: int
    mr0: float
    mx0: float

@dataclass
class ACC_Bran:
    bran_idx: int
    ia_idx: int
    ib_idx: int
    ic_idx: int
    in_idx: int
    dir: str

@dataclass
class DifferentialCurrent:
    ua_idx: int
    ub_idx: int
    uc_idx: int

@dataclass
class Bus:
    idx: int
    bus_name: str
    srcRef: int
    VRtg: float
    VRtgSnd: float
    VRtgSnd_Pos: str
    bus_uuid: str
    ACVChn: ACVChn
    StaChn: List[StaChn]
    SDL_Protect: bool
    SDL_Breaker: bool

@dataclass
class Line:
    idx: int
    line_name: str
    bus_ID: int
    srcRef: int
    VRtg: float
    ARtg: float
    ARtgSnd: float
    LinLen: float
    bran_num: int
    line_uuid: str
    remote_ID: int
    remote_Flag: int
    differential_ID: int
    RX: RX
    CG: CG
    PX: PX
    MR: MR
    ACC_Bran: ACC_Bran
    AnaChn: List[int]
    StaChn: List[StaChn]
    DifferentialCurrent: DifferentialCurrent
    SDL_Protect: bool
    SDL_Breaker: bool

@dataclass
class ComtradeModel:
    station_name: str
    version: str
    reference: str
    rec_dev_name: str
    AnalogChannel: List[AnalogChannel]
    StatusChannel: List[StatusChannel]
    Bus: List[Bus]
    Line: List[Line]

# 辅助函数：获取元素文本，支持默认值
def get_text(element, tag, default=None):
    child = element.find(f'scl:{tag}', namespace)
    return child.text if child is not None else default

# 辅助函数：获取元素整数值，支持默认值
def get_int(element, tag, default=None):
    text = get_text(element, tag, default)
    return int(text) if text is not None else default

# 辅助函数：获取元素浮点数值，支持默认值
def get_float(element, tag, default=None):
    text = get_text(element, tag, default)
    return float(text) if text is not None else default

# 解析 AnalogChannel 元素
def parse_analog_channel(element):
    return AnalogChannel(
        idx_cfg=get_int(element, 'idx_cfg'),
        idx_org=get_int(element, 'idx_org'),
        type=get_text(element, 'type'),
        flag=get_text(element, 'flag'),
        freq=get_int(element, 'freq'),
        au=get_float(element, 'au'),
        bu=get_float(element, 'bu'),
        sIUnit=get_text(element, 'sIUnit'),
        multiplier=get_text(element, 'multiplier'),
        primary=get_int(element, 'primary'),
        secondary=get_int(element, 'secondary'),
        ps=get_text(element, 'ps'),
        idx_rlt=get_int(element, 'idx_rlt'),
        ph=get_text(element, 'ph')
    )

# 解析 StatusChannel 元素
def parse_status_channel(element):
    return StatusChannel(
        idx_cfg=get_int(element, 'idx_cfg'),
        idx_org=get_int(element, 'idx_org'),
        type=get_text(element, 'type'),
        flag=get_text(element, 'flag'),
        contact=get_text(element, 'contact'),
        srcRef=get_text(element, 'srcRef')
    )

# 解析 ACVChn 元素
def parse_acvchn(element):
    return ACVChn(
        ua_idx=get_int(element, 'ua_idx'),
        ub_idx=get_int(element, 'ub_idx'),
        uc_idx=get_int(element, 'uc_idx'),
        un_idx=get_int(element, 'un_idx'),
        ul_idx=get_int(element, 'ul_idx')
    )

# 解析 StaChn 元素
def parse_stachn(element):
    return StaChn(
        idx_cfg=get_int(element, 'idx_cfg')
    )

# 解析 RX 元素
def parse_rx(element):
    return RX(
        r1=get_float(element, 'r1'),
        x1=get_float(element, 'x1'),
        r0=get_float(element, 'r0'),
        x0=get_float(element, 'x0')
    )

# 解析 CG 元素
def parse_cg(element):
    return CG(
        c1=get_float(element, 'c1'),
        c0=get_float(element, 'c0'),
        g1=get_float(element, 'g1'),
        g0=get_float(element, 'g0')
    )

# 解析 PX 元素
def parse_px(element):
    return PX(
        px=get_float(element, 'px'),
        px0=get_float(element, 'px0')
    )

# 解析 MR 元素
def parse_mr(element):
    return MR(
        idx=get_int(element, 'idx'),
        mr0=get_float(element, 'mr0'),
        mx0=get_float(element, 'mx0')
    )

# 解析 ACC_Bran 元素
def parse_acc_bran(element):
    return ACC_Bran(
        bran_idx=get_int(element, 'bran_idx'),
        ia_idx=get_int(element, 'ia_idx'),
        ib_idx=get_int(element, 'ib_idx'),
        ic_idx=get_int(element, 'ic_idx'),
        in_idx=get_int(element, 'in_idx'),
        dir=get_text(element, 'dir')
    )

# 解析 DifferentialCurrent 元素
def parse_differential_current(element):
    return DifferentialCurrent(
        ua_idx=get_int(element, 'ua_idx'),
        ub_idx=get_int(element, 'ub_idx'),
        uc_idx=get_int(element, 'uc_idx')
    )

# 解析 Bus 元素
def parse_bus(element):
    acvchn = parse_acvchn(element.find('scl:ACVChn', namespace))
    stachns = [parse_stachn(stachn) for stachn in element.findall('scl:StaChn', namespace)]
    sdl_protect = element.find('scl:SDL_Protect', namespace) is not None
    sdl_breaker = element.find('scl:SDL_Breaker', namespace) is not None
    return Bus(
        idx=get_int(element, 'idx'),
        bus_name=get_text(element, 'bus_name'),
        srcRef=get_int(element, 'srcRef'),
        VRtg=get_float(element, 'VRtg'),
        VRtgSnd=get_float(element, 'VRtgSnd'),
        VRtgSnd_Pos=get_text(element, 'VRtgSnd_Pos'),
        bus_uuid=get_text(element, 'bus_uuid'),
        ACVChn=acvchn,
        StaChn=stachns,
        SDL_Protect=sdl_protect,
        SDL_Breaker=sdl_breaker
    )

# 解析 Line 元素
def parse_line(element):
    rx = parse_rx(element.find('scl:RX', namespace))
    cg = parse_cg(element.find('scl:CG', namespace))
    px = parse_px(element.find('scl:PX', namespace))
    mr = parse_mr(element.find('scl:MR', namespace))
    acc_bran = parse_acc_bran(element.find('scl:ACC_Bran', namespace))
    anachns = [int(get_text(anachn, 'idx_cfg')) for anachn in element.findall('scl:AnaChn', namespace)]
    stachns = [parse_stachn(stachn) for stachn in element.findall('scl:StaChn', namespace)]
    differential_current = parse_differential_current(element.find('scl:DifferentialCurrent', namespace))
    sdl_protect = element.find('scl:SDL_Protect', namespace) is not None
    sdl_breaker = element.find('scl:SDL_Breaker', namespace) is not None
    return Line(
        idx=get_int(element, 'idx'),
        line_name=get_text(element, 'line_name'),
        bus_ID=get_int(element, 'bus_ID'),
        srcRef=get_int(element, 'srcRef'),
        VRtg=get_float(element, 'VRtg'),
        ARtg=get_float(element, 'ARtg'),
        ARtgSnd=get_float(element, 'ARtgSnd'),
        LinLen=get_float(element, 'LinLen'),
        bran_num=get_int(element, 'bran_num'),
        line_uuid=get_text(element, 'line_uuid'),
        remote_ID=get_int(element, 'remote_ID'),
        remote_Flag=get_int(element, 'remote_Flag'),
        differential_ID=get_int(element, 'differential_ID'),
        RX=rx,
        CG=cg,
        PX=px,
        MR=mr,
        ACC_Bran=acc_bran,
        AnaChn=anachns,
        StaChn=stachns,
        DifferentialCurrent=differential_current,
        SDL_Protect=sdl_protect,
        SDL_Breaker=sdl_breaker
    )

# 主解析函数
def parse_ymz_dmf(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    namespace = {'scl': 'http://www.iec.ch/61850/2003/SCL'}

    # 解析 ComtradeModel 的属性
    station_name = get_text(root, 'station_name')
    version = get_text(root, 'version')
    reference = get_text(root, 'reference')
    rec_dev_name = get_text(root, 'rec_dev_name')

    # 解析 AnalogChannel 元素列表
    analog_channels = [parse_analog_channel(ac) for ac in root.findall('scl:AnalogChannel', namespace)]

    # 解析 StatusChannel 元素列表
    status_channels = [parse_status_channel(sc) for sc in root.findall('scl:StatusChannel', namespace)]

    # 解析 Bus 元素列表
    buses = [parse_bus(bus) for bus in root.findall('scl:Bus', namespace)]

    # 解析 Line 元素列表
    lines = [parse_line(line) for line in root.findall('scl:Line', namespace)]

    # 返回 ComtradeModel 对象
    return ComtradeModel(
        station_name=station_name,
        version=version,
        reference=reference,
        rec_dev_name=rec_dev_name,
        AnalogChannel=analog_channels,
        StatusChannel=status_channels,
        Bus=buses,
        Line=lines
    )

# 使用示例
file_path = 'd:\\codeArea\\gitee\\comtradeOfPython\\tests\\data\\ymz.dmf'
comtrade_model = parse_ymz_dmf(file_path)
