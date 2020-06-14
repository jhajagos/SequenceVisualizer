import os
import h5py


def main(hdf5_file_name):

    ("number_of_samples", "number_of_time_points", "number_of_features")


    train_sequence = "/data/processed/train/sequence/"
    train_target = "/data/processed/train/target/"
    train_identifiers = "/data/processed/train/identifiers/"

    test_sequence = "/data/processed/test/sequence/"
    test_target = "/data/processed/test/target/"
    test_identifiers = "/data/processed/test/target/"

    groups_to_create = [train_sequence, test_sequence, train_target, test_target]

    array_name = "core_array"
    annotation_name = "column_annotations"

    with h5py.File(hdf5_file_name, "w") as f5w:

        for group in groups_to_create:
            f5w.create_group(group)





if __name__ == "__main__":
    hdf5_file_name = "test_processed.hdf5"

    if os.path.exists(hdf5_file_name):
        os.remove(hdf5_file_name)

    main(hdf5_file_name)