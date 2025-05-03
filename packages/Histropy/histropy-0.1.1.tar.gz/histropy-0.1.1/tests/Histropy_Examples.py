from Histropy.InterHist import InterHist

#Creates Figure 1: Main Histropy window with no changes made from opening
figure1 = InterHist("tests/test_images/from acta paper 512 square no noise.jpg")

#Creates Figure 4: Main Histropy window with range limited from 48 to 80
figure4 = InterHist("tests/test_images/from acta paper 512 square no noise.jpg", lbound=48, rbound=80)

#Creates Figure 7: Two overlaid histograms, no noise and p1 enforced
figure7 = InterHist("tests/test_images/from acta paper 512 square no noise.jpg", lbound=160, rbound=174, overlay_image_list=["tests/test_images/p1 of from acta paper 512 square 0.1 Gaussian.jpg"])

#Creates Figure 8: Three overlaid histograms
figure4 = InterHist("tests/test_images/from acta paper 512 square no noise.jpg", lbound=160, rbound=174, overlay_image_list=["tests/test_images/p1 of from acta paper 512 square 0.1 Gaussian.jpg", "tests/test_images/p4g of from acta paper 512 square 0.1 Gaussian.jpg", "tests/test_images/p4 of from acta paper 512 square 0.1 Gaussian.jpg"])

#Creates Figure A2: Overlaid gaussian with p2 and p4 enforced
figureA2 = InterHist("tests/test_images/from acta paper 512 square 0.1 Gaussian.jpg", overlay_image_list=["tests/test_images/p2 of from acta paper 512 square 0.1 Gaussian.jpg", "tests/test_images/p4 of from acta paper 512 square 0.1 Gaussian.jpg"])