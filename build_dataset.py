# import the necessary packages
from bs4 import BeautifulSoup
from imutils import paths
import argparse
import random
import os
# Set the dataset base path here
BASE_PATH = "./dataset"

# build the path to the annotations and input images
ANNOT_PATH = os.path.sep.join([BASE_PATH, 'annotations'])
IMAGES_PATH = os.path.sep.join([BASE_PATH, 'images'])

# degine the training/testing split
# If you have only training dataset then put here TRAIN_TEST_SPLIT = 1
TRAIN_TEST_SPLIT = 0.80

#  build the path to the output training and test .csv files
TRAIN_CSV = os.path.sep.join([BASE_PATH, 'train.csv'])
TEST_CSV = os.path.sep.join([BASE_PATH, 'test.csv'])

# build the path to the output classes CSV files
CLASSES_CSV = os.path.sep.join([BASE_PATH, 'classes.csv'])

# build the path to the output predictions dir
OUTPUT_DIR = os.path.sep.join([BASE_PATH, 'predictions'])

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--annotations", default=ANNOT_PATH,
    help='path to annotations')
ap.add_argument("-i", "--images", default=IMAGES_PATH,
	help="path to images")
ap.add_argument("-t", "--train", default=TRAIN_CSV,
	help="path to output training CSV file")
ap.add_argument("-e", "--test", default=TEST_CSV,
	help="path to output test CSV file")
ap.add_argument("-c", "--classes", default=CLASSES_CSV,
	help="path to output classes CSV file")
ap.add_argument("-s", "--split", type=float, default=TRAIN_TEST_SPLIT,
	help="train and test split")
args = vars(ap.parse_args())

# Create easy variable names for all the arguments
annot_path = args["annotations"]
images_path = args["images"]
train_csv = args["train"]
test_csv = args["test"]
classes_csv = args["classes"]
train_test_split = args["split"]

# grab all image paths then construct the training and testing split
imagePaths = list(paths.list_files(images_path))
random.shuffle(imagePaths)
i = int(len(imagePaths) * train_test_split)
trainImagePaths = imagePaths[:i]
testImagePaths = imagePaths[i:]

# create the list of datasets to build
dataset = [ ("train", trainImagePaths, train_csv),
            ("test", testImagePaths, test_csv)]

# initialize the set of classes we have
CLASSES = set()

# loop over the datasets
for (dType, imagePaths, outputCSV) in dataset:
    # load the contents
    print ("[INFO] creating '{}' set...".format(dType))
    print ("[INFO] {} total images in '{}' set".format(len(imagePaths), dType))

    # open the output CSV file
    csv = open(outputCSV, "w")

    # loop over the image paths
    for imagePath in imagePaths:
        # build the corresponding annotation path
        fname = imagePath.split(os.path.sep)[-1]
        fname = "{}.xml".format(fname[:fname.rfind(".")])
        annotPath = os.path.sep.join([annot_path, fname])

        # load the contents of the annotation file and buid the soup
        contents = open(annotPath).read()
        soup = BeautifulSoup(contents, "html.parser")

        # extract the image dimensions
        w = int(soup.find("width").string)
        h = int(soup.find("height").string)

        # loop over all object elements
        for o in soup.find_all("object"):
            #extract the label and bounding box coordinates
            label = o.find("name").string
            xMin = int(float(o.find("xmin").string))
            yMin = int(float(o.find("ymin").string))
            xMax = int(float(o.find("xmax").string))
            yMax = int(float(o.find("ymax").string))

            # truncate any bounding box coordinates that fall outside
            # the boundaries of the image
            xMin = max(0, xMin)
            yMin = max(0, yMin)
            xMax = min(w, xMax)
            yMax = min(h, yMax)

            # ignore the bounding boxes where the minimum values are larger
            # than the maximum values and vice-versa due to annotation errors
            if xMin >= xMax or yMin >= yMax:
                continue
            elif xMax <= xMin or yMax <= yMin:
                continue

            # write the image path, bb coordinates, label to the output CSV
            row = [os.path.abspath(imagePath),str(xMin), str(yMin), str(xMax),
                    str(yMax), str(label)]
            csv.write("{}\n".format(",".join(row)))

            # update the set of unique class labels
            CLASSES.add(label)

    # close the CSV file
    csv.close()

# write the classes to file
print("[INFO] writing classes...")
csv = open(classes_csv, "w")
rows = [",".join([c, str(i)]) for (i,c) in enumerate(CLASSES)]
csv.write("\n".join(rows))
csv.close()
