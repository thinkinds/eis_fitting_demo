from schemdraw import Drawing, Segment
from schemdraw.elements import Element2Term
from schemdraw import elements
from schemdraw.elements import ResistorIEC, Inductor, CPE, Capacitor, Line, Dot
from schemdraw.segments import SegmentText
import re

PARA_HEIGHT = 1


class Warburg(elements.ResistorIEC):
    def __init__(self, *d, **kwargs):
        super().__init__(*d, **kwargs)
        self.segments.append(SegmentText([0.5, 0], 'W'))


# map circuit elements to drawing functions
ele_map = {'R': ResistorIEC,
           'C': Capacitor,
           'CPE': CPE,
           'W': Warburg,
           'Wo': Warburg,
           'Ws': Warburg,
           'L': Inductor}


def draw_circuit(cir_str: str, d: Drawing) -> Drawing:
    """ Constructs an SchemDraw drawing of a circuit that is specified as
        a string.
        :param d:
        :param cir_str: circuit string, e.g. 'R0-p(R1,C1)-p(R2-Wo1,C2)'
    """

    # function to draw parallel elements
    def draw_parallel(para_ele: str, d: Drawing):
        """ Constructs an SchemDraw drawing of a parallel circuit"""
        match = re.search(r'p\(([^,]+),([^)]+)\)', para_ele)  # max parallel branches = 2
        branch_1, branch_2 = match.groups()
        num_1 = len(branch_1.split('-'))
        num_2 = len(branch_2.split('-'))
        if max(num_1, num_2) > 1:
            unit_branch = 2  # narrow gap
        else:
            unit_branch = 3
        len_max = unit_branch * max(num_1, num_2)
        unit_1 = len_max / num_1
        unit_2 = len_max / num_2

        d.add(Line(d='right', l=.5))
        d.add(Dot())
        d.push()
        d.add(Line(d='up', l=PARA_HEIGHT))
        # draw branch 1
        d.config(unit=unit_1)
        draw_circuit(branch_1, d)
        d.config()
        d.add(Line(d='down', l=PARA_HEIGHT))
        d.add(Dot())
        d.pop()
        # draw branch 2
        d.add(Line(d='down', l=PARA_HEIGHT))
        d.config(unit=unit_2)
        draw_circuit(branch_2, d)
        d.config()
        d.add(Line(d='up', l=PARA_HEIGHT))
        d.add(Line(d='right', l=.5))

        # return d

    # drawing = Drawing()
    split_pattern = r'-(?![^\(]*\))'

    components_list = re.split(split_pattern, cir_str)

    for component in components_list:
        if component[0] != 'p':
            match = re.search(r'^[a-zA-Z]*', component.strip())
            if match:
                comp_type = match.group(0)
            else:
                raise ValueError('cannot match component type, it should a string like "R" or "CPE"')
            d.add(ele_map[comp_type](label=component).right())
        else:
            draw_parallel(component, d)

    return d
