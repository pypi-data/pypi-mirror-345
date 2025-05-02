##########
User guide
##########

.. contents::


Local usage
===========
Datapipe is intended for running large production jobs using DIRAC, but running locally on a laptop or a local cluster is frequently useful for testing purposes and is what will be described here.


.. NOTE::
    * For brevity this guide only describes the case of processing gamma and proton files, if you also want to include electrons the situation around training the machine learning models becomes a bit move involved.
    * This guide only shows how to perform a stereo reconstruction analysis, but doing a mono analysis is supported by ctapipe itself
    * The guide assumes you have a directory containing gamma and proton files already processed to data level 1 (dl1), and that they are in the alpha subarray configuration.
    * The provided commands also assumes you are trying to process files in a ``bash`` shell environment.


Processing data to data level 3
*******************************

The high level description of the process goes like this

* Process all gamma and proton files to data level 2
* Merge the two kind of particle files into training and test sets
* Train an energy model on the training gamma file
* Apply the energy model on the training gamma and proton files
* Train a particle classifier on the updated training files
* Finally, apply the energy and classification models on the gamma and proton test files

Setup
-----

* Fetch an up to date set of configuration files from `gitlab <https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/pipeline-configurations>`_.
* Select the configuration files appropriate for the version of ctapipe you intend to use, so pick the files in ``pipeline-configurations/ctapipe/v0.23/v1`` if you intend to use the latest release of ctapipe.
    * If you know you will want to make any changes to the configuration, copy the files to a separate directory.


Processing
----------

To process a dl1 file to dl2 you need to run the command::

    ctapipe-process --input $INPUT_FILE \
        --output $OUTPUT_FILE \
        --config $CONF_FILE \
        --config $SUBARRAY_FILE \
        --provenance-log $PROVENANCE_LOG

Where ``INPUT_FILE`` is path to an input file, ``OUTPUT_FILE`` the path and name of the output file, ``CONF_FILE`` is path to a config file such a ``dl1_to_dl2.yml`` found in the pipeline-configuration path indicated previously. Likewise ``SUBARRAY_FILE`` is the file describing the subarray, in this example ``prod6/subarray_north_alpha.yml`` found next to the  ``dl1_to_dl2.yml`` configuration file. Finally ``PROVENANCE_LOG`` is the path at which the provenace log will be saved, take care to set it to different target for each input file or later tracking will be complicated.

Run the above command with the inputs adjusted so that each of the available input files is processed into a separate file, and you will end up with a set of ``h5`` files containing entries at the path ``dl2/event/subarray/geometry``, which allows for training energy and particle classification models.


Merging
-------
Decide on which fraction of the processed files you want for training and how much you want for testing and save the training and test sets of processed gamma and proton files into a total of four lists, then run something like the following command for each of these lists::

    ctapipe-merge $GAMMA_TRAIN_FILES --output $OUTPUT_DIR/gamma_merged_train.dl2.h5

where ``GAMMA_TRAIN_FILES`` is a environment variable containing list of gamma files you wish to merge into a training set, for example generated using::

    GAMMA_TRAIN_FILES=$(echo $OUTPUT_DIR/gamma*[0-1]*.h5)

with will merge all gamma files in ``OUTPUT_DIR`` with names that start with "0" or "1". Alternatively you could save the files into a literal file (ex ``gamma_train_files.list``), one file name per row, and save the contents into a file, which you then using like this::

    GAMMA_TRAIN_FILES=$(cat gamma_train_files.list)
    ctapipe-merge $GAMMA_TRAIN_FILES --output $OUTPUT_DIR/gamma_merged_train.dl2.h5

Using some method of specifying files, merge your processed gamma and proton files so that you end up with four merged files:
    * Gamma train, the file containing the gamma events to be used for training machine learning models
    * Gamma test, the file with events used for "testing" the performance of the analysis
    * Proton train, the file containing the protons events to be used for training machine learning models
    * Proton test, the file with events used for "testing" the performance of the analysis

Energy regression and particle classification
---------------------------------------------
The training process has the following four steps

* Train an energy model on the training gamma file
* Apply the energy model on the training gamma and proton files
* Train a particle classifier on the updated training files
* Finally, apply the energy and classification models on the gamma and proton test files

First define the following environment variables:

* ``REG_CONF_FILE``, a configuration file for the energy regression training for example ``train_energy_regressor.yml``
* ``CLS_CONF_FILE``, a configuration file for the particle classification training for example ``train_particle_classifier.yml``
* ``INPUT_GAM_FILE``, the Gamma train file created in the previous step
* ``INPUT_PRO_FILE``, the Proton train file
* ``EVAL_GAM_FILE``, the Gamma test file
* ``EVAL_PRO_FILE``, the Proton test file
* ``OUTPUT_DIR``, where to save the output models

Then training and creation of machine learning models for particle classification and energy regression is achieved by running the following set of commands::

    ctapipe-train-energy-regressor --input $INPUT_GAM_FILE \
        --output energy_regressor.pkl \
        --config $REG_CONF_FILE \
        --cv-output $OUTPUT_DIR/cv_energy.h5 \
        --provenance-log $OUTPUT_DIR/train_energy.provenance.log \
        --log-file $OUTPUT_DIR/train_energy.log \
        --log-level INFO \
        --overwrite

    ctapipe-apply-models --input $INPUT_GAM_FILE \
        --output $OUTPUT_DIR/gamma_train_clf.dl2.h5 \
        --reconstructor energy_regressor.pkl \
        --provenance-log $OUTPUT_DIR/apply_gamma_train_reg.provenance.log \
        --log-file $OUTPUT_DIR/apply_gamma_train_clf.log \
        --log-level INFO \
        --overwrite

    ctapipe-apply-models --input $INPUT_PRO_FILE  \
        --output $OUTPUT_DIR/proton_train_clf.dl2.h5 \
        --reconstructor energy_regressor.pkl \
        --provenance-log $OUTPUT_DIR/apply_proton_train_reg.provenance.log \
        --log-file $OUTPUT_DIR/apply_proton_train_clf.log \
        --log-level INFO \
        --overwrite

    ctapipe-train-particle-classifier --signal $OUTPUT_DIR/gamma_train_clf.dl2.h5 \
        --background $OUTPUT_DIR/proton_train_clf.dl2.h5 \
        --output particle_classifier.pkl \
        --config $CLS_CONF_FILE \
        --cv-output $OUTPUT_DIR/cv_particle.h5 \
        --provenance-log $OUTPUT_DIR/train_particle.provenance.log \
        --log-file $OUTPUT_DIR/train_particle.log \
        --log-level INFO \
        --overwrite

which will produce two trained models saved as ``energy_regressor.pkl`` and ``particle_classifier.pkl``. Then to finish we apply these two models to the test files, ``EVAL_GAM_FILE`` and ``EVAL_PRO_FILE``, to produce the final files::

    ctapipe-apply-models --input $EVAL_GAM_FILE \
        --output $OUTPUT_DIR/gamma_final.dl2.h5 \
        --reconstructor energy_regressor.pkl \
        --reconstructor particle_classifier.pkl \
        --provenance-log $OUTPUT_DIR/apply_gamma_final.provenance.log \
        --log-file $OUTPUT_DIR/apply_gamma_final.log \
        --log-level INFO \
        --overwrite

    ctapipe-apply-models --input $EVAL_PRO_FILE \
        --output $OUTPUT_DIR/proton_final.dl2.h5 \
        --reconstructor energy_regressor.pkl \
        --reconstructor particle_classifier.pkl \
        --provenance-log $OUTPUT_DIR/apply_proton_final.provenance.log \
        --log-file $OUTPUT_DIR/apply_proton_final.log \
        --log-level INFO --overwrite

which will produce ``gamma_final.dl2.h5`` and ``proton_final.dl2.h5``.

IRF generation
--------------

IRF generation happens, in principle, in two steps:
* Optimisation of the Gamma vs Hadron cuts, along with a possible directional cut
* Application of these cuts on the "final" files and using the surviving events when filling IRF tables

First define the following environment variables:

* ``OPTIM_CONF_FILE``, a configuration file for the optimisation step, *no example provided*
* ``PNT_CONF_FILE``, a configuration file for making point-like irfs, *no example provided*
* ``FULL_CONF_FILE``, a configuration file for making full-enclosure irfs, *no example provided*
* ``GAM_OPTIM_FILE``, the Gamma file used to optimise selection cuts, can be the train file created earlier, or the test file
* ``PRO_OPTIM_FILE``, the Proton file used to optimise selection cuts, can be the train file created earlier, or the test file
* ``GAM_IRF_FILE``, the Gamma file used to derive the final instrument response, should be the test file created previously
* ``PRO_IRF_FILE``, the Proton file used to derive the final instrument response, should be the test file created previously

The optimistion is performed with the command::

    ctapipe-optimize-event-selection --config $OPTIM_CONF_FILE \
        --gamma-file $GAMMAS \
        --proton-file $PROTONS \
        --output $OUTPUT_DIR/cuts_opt_point.fits \
        --point-like

After which you can create the irfs using::

    ctapipe-compute-irf --config $PNT_CONF_FILE \
        --cuts $OUTPUT_DIR/cuts_opt_point.fits \
        --gamma-file $GAMMAS \
        --proton-file $PROTONS \
        --output $OUTPUT_DIR/point-like-irf.fits \
        --benchmark-output $OUTPUT_DIR/point-like-bench.fits
        --do-background \
        --spatial-selection-applied

    ctapipe-compute-irf --config $FULL_CONF_FILE \
        --cuts $OUTPUT_DIR/cuts_opt_point.fits \
        --gamma-file $GAMMAS \
        --proton-file $PROTONS \
        --output $OUTPUT_DIR/full-enclosure-irf.fits \
        --do-background \
        --no-spatial-selection-applied

And you will get two sets of irfs, full-enclosure and point-like. Note that the choice of supplied command-line settings in the above commands makes it is possible to put all configuration settings into just one single file that is used everywhere.
