import calendar
import os
import sys
from datetime import datetime
from pathlib import Path

import cv2 as cv2
import numpy as np
from sklearn import cluster

expected_dice = 5
dim = (1440, 810)
date = datetime.utcnow()
now = calendar.timegm(date.utctimetuple())


def main():
    if len(sys.argv) < 2:
        print('No file passed as arg')
        sys.exit(-1)

    image_filename = sys.argv[1]
    res = process(image_filename)
    # When everything done, release the capture
    # cap.release()
    return res


def process(filename):
    frame = cv2.imread(filename)
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    # We'll define these later
    blobs = get_blobs(frame)
    dice = get_dice_from_blobs(blobs)

    if len(dice) != expected_dice:
        raise ValueError(f'Number of found dice ({len(dice)}) is less than {expected_dice} (file: {filename})')

    for i in dice:
        if i[0] == 0 or i[0] > 6:
            raise ValueError(f'Number of pips ({i[0]}) is not as expected for file: {filename}')

    overlay_info(frame, dice, blobs)

    file_path = Path(f'{os.getcwd()}/{filename}').absolute()
    proof_file_path = file_path.parent.joinpath('proof')
    proof_file_path.mkdir(parents=True, exist_ok=True)
    proof_file = f'{proof_file_path}/{file_path.name.replace(".jpg", f".{now}.jpg")}'
    cv2.imwrite(proof_file, frame)

    print(f'Dice found: {[item[0] for item in dice]} (file: {filename})')

    cv2.destroyAllWindows()

    return [item[0] for item in dice]


def get_blobs(frame):
    params = cv2.SimpleBlobDetector_Params()

    # params.filterByInertia
    params.minInertiaRatio = 0.6

    detector = cv2.SimpleBlobDetector_create(params)

    frame_blurred = cv2.medianBlur(frame, 11)
    # show(frame_blurred)
    frame_gray = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2GRAY)
    # show(frame_gray)
    blobs = detector.detect(frame_gray)

    return blobs


def overlay_info(frame, dice, blobs):
    # Overlay blobs
    for b in blobs:
        pos = b.pt
        r = b.size / 2

        cv2.circle(frame, (int(pos[0]), int(pos[1])),
                   int(r), (255, 0, 0), 2)

    # Overlay dice number
    for d in dice:
        # Get textsize for text centering
        textsize = cv2.getTextSize(
            str(d[0]), cv2.FONT_HERSHEY_PLAIN, 3, 2)[0]

        cv2.putText(frame, str(d[0]),
                    (int(d[1] - textsize[0] / 2),
                     int(d[2] + textsize[1] / 2)),
                    cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)


def show(img, wait=True):
    cv2.imshow('image', img)
    if wait:
        cv2.waitKey(0)


def get_dice_from_blobs(blobs):
    # Get centroids of all blobs
    x = []
    for b in blobs:
        pos = b.pt

        if pos is not None:
            x.append(pos)

    x = np.asarray(x)

    if len(x) > 0:
        # Important to set min_sample to 0, as a dice may only have one dot
        clustering = cluster.DBSCAN(eps=40, min_samples=1).fit(x)

        # Find the largest label assigned + 1, that's the number of dice found
        num_dice = max(clustering.labels_) + 1

        dice = []

        # Calculate centroid of each dice, the average between all a dice's dots
        for i in range(num_dice):
            x_dice = x[clustering.labels_ == i]

            centroid_dice = np.mean(x_dice, axis=0)

            dice.append([len(x_dice), *centroid_dice])

        return dice

    else:
        return []


if __name__ == '__main__':
    main()
