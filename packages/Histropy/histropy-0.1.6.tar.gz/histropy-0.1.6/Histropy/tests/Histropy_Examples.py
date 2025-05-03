from Histropy.InterHist import InterHist
from importlib import resources
from pathlib import Path

def get_image_path(filename):
    resource = resources.files('Histropy.data').joinpath(filename)
    with resources.as_file(resource) as path:
        return str(path)
    
from_acta_paper_512_square_no_noise = get_image_path("from acta paper 512 square no noise.jpg")
from_acta_paper_512_square_01_gaussian = get_image_path("from acta paper 512 square 0.1 Gaussian.jpg")
p1_of_from_acta_paper_512_square_01_gaussian = get_image_path("p1 of from acta paper 512 square 0.1 Gaussian.jpg")
p2_of_from_acta_paper_512_square_01_gaussian = get_image_path("p2 of from acta paper 512 square 0.1 Gaussian.jpg")
p4_of_from_acta_paper_512_square_01_gaussian = get_image_path("p4 of from acta paper 512 square 0.1 Gaussian.jpg")
p4g_of_from_acta_paper_512_square_01_gaussian = get_image_path("p4g of from acta paper 512 square 0.1 Gaussian.jpg")
#Creates Figure 1: Main Histropy window with no changes made from opening
figure1 = InterHist(from_acta_paper_512_square_no_noise)

#Creates Figure 4: Main Histropy window with range limited from 48 to 80
figure4 = InterHist(from_acta_paper_512_square_no_noise, lbound=48, rbound=80)

#Creates Figure 7: Two overlaid histograms, no noise and p1 enforced
figure7 = InterHist(from_acta_paper_512_square_no_noise, lbound=160, rbound=174, overlay_image_list=[p1_of_from_acta_paper_512_square_01_gaussian])

#Creates Figure 8: Three overlaid histograms
figure4 = InterHist(from_acta_paper_512_square_no_noise, lbound=160, rbound=174, overlay_image_list=[p1_of_from_acta_paper_512_square_01_gaussian, p4g_of_from_acta_paper_512_square_01_gaussian, p4_of_from_acta_paper_512_square_01_gaussian])

#Creates Figure A2: Overlaid gaussian with p2 and p4 enforced
figureA2 = InterHist(from_acta_paper_512_square_01_gaussian, overlay_image_list=[p2_of_from_acta_paper_512_square_01_gaussian, p4_of_from_acta_paper_512_square_01_gaussian])