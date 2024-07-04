from PIL import Image
from circuits_draw import draw_circuit
from schemdraw import Drawing
def test_draw_circuit():
    # dwg = Drawing()
    with Drawing(
            file='my_circuit.svg',
            show=False) as dwg:
        draw_circuit('R0-p(L3, R3)', dwg)
        image_bytes = dwg.get_imagedata('svg')
    # dwg.save('my_circuit.svg')
    # Image.open(image_bytes)

    assert False
