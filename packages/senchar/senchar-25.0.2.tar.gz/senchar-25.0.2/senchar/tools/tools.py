from .bias import Bias
from .dark import Dark
from .defects import Defects
from .detcal import DetCal
from .eper import Eper
from .fe55 import Fe55
from .gain import Gain
from .gainmap import GainMap
from .linearity import Linearity
from .prnu import Prnu
from .ptc import Ptc
from .qe import QE
from .superflat import Superflat

# create tools,  automatically added to db.tools dict
bias = Bias()
dark = Dark()
defects = Defects()
detcal = DetCal()
eper = Eper()
fe55 = Fe55()
gain = Gain()
gainmap = GainMap()
linearity = Linearity()
prnu = Prnu()
ptc = Ptc()
qe = QE()
superflat = Superflat()
