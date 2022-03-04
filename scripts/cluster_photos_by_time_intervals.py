#! /usr/bin/env python

import sys
import shutil
import subprocess as spc
from datetime import datetime
from sklearn.mixture import GaussianMixture
from pathlib import Path
from argparse import ArgumentParser


def get_options():
    parser = ArgumentParser(usage="cluster_photos_by_time_intervals.py -i sample_dir -o out_dir",
                            description="")
    parser.add_argument("-i", "--input", dest="sample_dir", type=Path,
                        help="The directory that contains all photos of a sample.")
    parser.add_argument("-o", "--output", dest="output_dir", type=Path, default=None,
                        help="Output directory. Make clustering at the original directory if not provided. ")
    # This is just for postfix matching
    # format is not considered yet, but exiftool can automatically recognize CR3 info without designation
    parser.add_argument("--postfix", dest="photo_postfix", default=".dng",
                        help="The postfix of the photo files. ")
    parser.add_argument("-r", "--rotation", dest="rotation_threshold", default=15., type=float,
                        help="By seconds. Arbitrary threshold to identify the between-rotations time interval. "
                             "This time interval is caused by manual adjustment of the tripod or other equipment"
                             " to make a different angle towards to turntable and is usually very long (> 60s). "
                             "Default: %(default)ss")
    parser.add_argument("-a", "--angle", dest="angle_threshold", default=1., type=float,
                        help="By seconds. Arbitrary threshold to identify the between-angles time interval. "
                             "Set to -1 for using GMM automatic identification (currently problematic). "
                             "Default: %(default)ss")
    parser.add_argument("--quiet", dest="quiet", default=False,
                        help="Quiet mode. ")
    return parser.parse_args()


def check_exiftool_availability(quiet=False):
    # check exiftool and print the version
    exiftool_version = \
        spc.Popen("exiftool -ver", shell=True, stdout=spc.PIPE, stderr=spc.PIPE).communicate()[0].decode("utf8").strip()
    check_pass = True
    try:
        exiftool_version = float(exiftool_version)
    except:
        check_pass = False
    if not check_pass:
        raise FileNotFoundError("Please have exiftool installed in the PATH!\n")
    else:
        if not quiet:
            sys.stdout.write("Using exiftool v%2.2f\n" % exiftool_version)


def get_precise_date(photo_f):
    # use exiftool to extract the milliseconds information (default %Y:%m:%d %H:%M:%S is not enough)
    date_str = spc.Popen(
        f"exiftool -s -s -s -SubSecCreateDate {photo_f}",
        shell=True, stdout=spc.PIPE, stderr=spc.PIPE).communicate()[0].decode("utf8").strip()
    # use datetime.strptime() to convert time str to a datetime obj
    # BTW, dateutil works badly. e.g. for 2021:07:15 02:07:17.24+08:00
    date_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S.%f%z")
    return date_obj


def get_precise_dates(_photo_files, quiet=False):
    _dates_and_file = []
    print_step = int(len(_photo_files) / 10)
    count_photo = 1
    sys.stdout.write("Parsing photo exif: ")
    sys.stdout.flush()
    for photo_f in _photo_files:
        _dates_and_file.append([get_precise_date(photo_f=photo_f), photo_f])
        if not quiet:
            if count_photo % print_step == 0:
                sys.stdout.write("*")
                sys.stdout.flush()
            count_photo += 1
    sys.stdout.write("\n")
    return _dates_and_file


def use_gmm_to_cluster_intervals(_intervals, n_components, quiet=False):
    gm = GaussianMixture(n_components=n_components).fit(_intervals)
    # create the translator: from the gmm category id to the interval id
    mean_ids = [(_gmm_id, _mean) for _gmm_id, _mean in enumerate(gm.means_)]
    mean_ids.sort(key=lambda x: -x[1])  # sort from large interval (1) to small interval (2)
    id_translator = {_gmm_id: sorted_id + 1 for sorted_id, (_gmm_id, _mean) in enumerate(mean_ids)}
    # print the means
    if not quiet:
        sys.stdout.write("Interval Averages: %.4f, %.4f\n" % tuple([_mean for _gmm_id, _mean in mean_ids]))
    # assign intervals to levels and store the levels
    return [id_translator[_gmm_id] for _gmm_id in gm.predict(_intervals)]


def cluster(time_intervals, rotation_threshold=10, angle_threshold=1., quiet=False):
    """
    We have three sets of time intervals: between-rotations(0), between-angles-within-rotation(1), between-brackets(2)
    1. between-rotations is caused by manual operation,
       so it can be (and better to be) solved by arbitrarily set a threshold
    2. between-angles-within-rotation and between-brackets can be solved by
       fitting the time intervals into a Gaussian mixture model
    :param time_intervals: 2D array. If you data has a single feature, using array.reshape(-1, 1)
    :param rotation_threshold:
    :param angle_threshold: using gmm if -1
    :param quiet:
    :return:
    """
    interval_levels = []
    if angle_threshold == -1:
        interval_subset_l_1_2 = []
        for ti in time_intervals:
            if ti[0] > rotation_threshold:
                # assign intervals to levels and store the levels
                if interval_subset_l_1_2:
                    interval_levels.extend(use_gmm_to_cluster_intervals(interval_subset_l_1_2, n_components=2, quiet=quiet))
                interval_levels.append(0)  # assign current interval (ti) as between-rotations(0)
                interval_subset_l_1_2 = []
            else:
                interval_subset_l_1_2.append(ti)
        if interval_subset_l_1_2:
            interval_levels.extend(use_gmm_to_cluster_intervals(interval_subset_l_1_2, n_components=2, quiet=quiet))
    else:
        for ti in time_intervals:
            if ti[0] > rotation_threshold:
                interval_levels.append(0)
            elif ti[0] > angle_threshold:
                interval_levels.append(1)
            else:
                interval_levels.append(2)
    return interval_levels


def cluster_photo(from_file, to_file, moving_mode):
    if moving_mode:
        shutil.move(from_file, to_file)
    else:
        shutil.copy(from_file, to_file)


def main():
    options = get_options()
    change_the_original = False
    if options.output_dir is None:
        options.output_dir = options.sample_dir
        change_the_original = True
        if not options.quiet:
            sys.stdout.write("Warning: output not provided! Making changes to the original dir! \n")
    check_exiftool_availability(quiet=options.quiet)
    photo_files = list(options.sample_dir.glob("*" + options.photo_postfix))
    if not photo_files:
        sys.stdout.write(f"No photos matching *{options.photo_postfix} found! Check the postfix and the directory!\n")
        sys.exit()
    dates_files = get_precise_dates(photo_files, quiet=options.quiet)
    dates_files.sort(key=lambda x: x[0])  # sort dates_files increasingly

    # for test
    # with open(options.sample_dir / "dates_files.txt", "w") as dates_output:
    #     dates_output.writelines([str(x[0]) + "\n" for x in dates_files])

    # each element is a list for the shape requirement of sklearn.mixture.GaussianMixture
    intervals = [[(dates_files[_go_ + 1][0] - dates_files[_go_][0]).total_seconds()]
                 for _go_ in range(0, len(dates_files) - 1)]

    # for test
    # with open(options.sample_dir / "intervals.txt", "w") as interval_output:
    #     interval_output.writelines([str(x[0]) + "\n" for x in intervals])

    interval_lls = cluster(
        time_intervals=intervals,
        rotation_threshold=options.rotation_threshold,
        angle_threshold=options.angle_threshold,
        quiet=options.quiet)
    rotation_id = 1
    angle_id = 1
    options.output_dir.mkdir(exist_ok=True)
    new_rotation_p = options.output_dir / ("rotation_%i" % rotation_id)
    new_rotation_p.mkdir()
    new_angle_p = new_rotation_p / ("angle_%i" % angle_id)
    new_angle_p.mkdir()
    new_photo_p = new_angle_p / dates_files[0][1].name
    cluster_photo(dates_files[0][1], new_photo_p, moving_mode=change_the_original)
    for go_i, itv_level in enumerate(interval_lls):
        if itv_level == 0:
            rotation_id += 1
            angle_id = 1
            new_rotation_p = options.output_dir / ("rotation_%i" % rotation_id)
            new_rotation_p.mkdir()
            new_angle_p = new_rotation_p / ("angle_%i" % angle_id)
            new_angle_p.mkdir()
            new_photo_p = new_angle_p / dates_files[go_i + 1][1].name
            cluster_photo(dates_files[go_i + 1][1], new_photo_p, moving_mode=change_the_original)
        elif itv_level == 1:
            angle_id += 1
            new_angle_p = new_rotation_p / ("angle_%i" % angle_id)
            new_angle_p.mkdir()
            new_photo_p = new_angle_p / dates_files[go_i + 1][1].name
            cluster_photo(dates_files[go_i + 1][1], new_photo_p, moving_mode=change_the_original)
        elif itv_level == 2:
            new_photo_p = new_angle_p / dates_files[go_i + 1][1].name
            cluster_photo(dates_files[go_i + 1][1], new_photo_p, moving_mode=change_the_original)


if __name__ == '__main__':
    main()
