# delta-execution-models

This repository contains the accompanying code for our ICRA 2017 paper

A. Mitrevski, A. Kuestenmacher, S. Thoduka, and P. G. Pl&ouml;ger, "Improving the Reliability of Service Robots in the Presence of External Faults by Learning Action Execution Models," in *Robotics and Automation (ICRA), IEEE Int. Conf.*, 2017.

MT_UseCases
===========

MT_UseCases is a Visual Studio solution of our Unreal Engine simulation. The simulation can run in three different modes:

1. *Random data collection mode*: Used when collecting data for learning a symbolic delta model and a geometric data mapping (the one described in [1]).
2. *GSM data collection mode*: Used for collecting GSM data.
3. *Evaluation mode*: Only used to evaluate the success of the learned models with respect to finding feasible robot-independent execution poses.

The parameters that are necessary for initialising the simulation can all be set in *MT_UseCases/Content/parameters.xml*:

* *simulation_type* (string): The mode in which the simulation should run (the accepted values are *random*, *rotation_optimised*, and *optimised*, corresponding to the three modes described above).
* *description_file* (string): Description file of the scenario that should be simulated (the description files are found under *MT_UseCases/Content/scenario_descriptions/&lt;UseCase&gt;/&lt;Scenario&gt;*).
* *duration* (float): The duration of a single simulation trial (in seconds).
* *copies* (int): The number of scenario copies that should be simulated in parallel.
* *display_rows* (int): The number of rows in which the scenario copies should be arranged; if the number of rows is *n*, each set of *n* scenario objects copies will have the same *x* coordinate values, but different *y* values.
* *row_offset* (float): The *y* offset between the scenario copies (depends on the sizes of the simulated objects).
* *column_offset* (float): The *x* offset between the scenario copies (depends on the sizes of the simulated objects).
* *copies_per_floor* (int): The scenario objects are placed above floor objects whose physics is disabled; this parameter controls the addition of new floor objects.
* *floor_offset* (float): The *x* offset between two different floor objects.
* *translation_tolerance* (float): The translation tolerance that is used when evaluating whether two positions are the same.
* *rotation_tolerance* (float): The rotation tolerance that is used when evaluating whether two rotations are the same.
* *translation_epsilon* (float): Only used for evaluating whether a given object is above another.
* *log_file* (string): Path of a log file to which the simulated object data should be saved. Only used when *simulation_mode* is set to either *random* or *rotation_optimised*.
* *optimisation_data_file* (string): Path of a file to which an initial guess for pose optimisation is written; should have the value *Absolute_Path_of_rule_learner/initial_guess.log*. Only used when *simulation_mode* is set to either *rotation_optimised* or *optimised*.
* *optimised_data_file* (string): Path of a file to which a set of optimised manipulated object poses is written; should have the value *Absolute_Path_of_rule_learner/optimised_guess.log*. Only used when *simulation_mode* is set to either *rotation_optimised* or *optimised*.
* *optimisation_script* (string): Path of a script that should be used for optimising the manipulated object's pose. Only used when *simulation_mode* is set to either *rotation_optimised* or *optimised*. When *simulation_mode* has the value *rotation_optimised*, *optimisation_script* should have the value *Absolute_Path_of_rule_learner/solve_delta_without_gsm.py*. When *simulation_mode* is set to *optimised*, *optimisation_script* should have the value *Absolute_Path_of_rule_learner/solve_delta.py*.
* *key_file* (string): Path of a file to which the object and instance keys are written before pose optimisation; should have the value *Absolute_Path_of_rule_learner/keys.txt*. Only used when *simulation_mode* is set to either *rotation_optimised* or *optimised*.
* *optimisation_keys* (string): A string that should print the object and instance keys and the number of objects in the problem instance on separate lines; should have the value *&lt;ObjectKey&gt;\n&lt;InstanceKey&gt;\n&lt;NumberOfInstanceObjects&gt;*. Regarding the number of objects, a value of *1* specifies that a delta naught model is used for describing the action, while a value greater than *1* specifies that a delta model is used. Only used when *simulation_mode* is set to either *rotation_optimised* or *optimised*.
* *number_of_trials* (int): The number of trials in an evaluation experiment. Only used when *simulation_mode* is set to *optimised*.
* *attempts_per_trial* (int): The number of times the execution in a trial is allowed to be performed; the trial is considered a failure if none of the executions are successful. Only used when *simulation_mode* is set to *optimised*.
* *trial_result_file* (string): Path of a file to which the results of the evaluation trials are written. Only used when *simulation_mode* is set to *optimised*.

Upon starting the Unreal Engine editor, the value of the variable *parametersFile* should be set to the absolute path of *MT_UseCases/Content/parameters.xml*. 

All 3D models used in the simulation were taken from [Archive 3D](http://archive3d.net/).

[1] R. Dearden and C. Burbridge, "Manipulation planning using learned symbolic state abstractions," *Robotics and Autonomous Systems*, vol. 62, no. 3, pp. 355 – 365, 2014.

rule_learner
============

*rule_learner* is a set of Python packages and scripts that are used for learning action execution models and optimising manipulated object poses using the learned models. *rule_learner* depends on the following packages:

* numpy
* scipy
* scikit-learn
* couchdb-python
* shapely

For learning an action execution model:

1. (if running the software for the first time) create a directory called *data* inside *rule_learner* and a directory called *learned_mappings* inside the newly created *data* directory
2. copy the log file collected by running the Unreal Engine simulation in the *random* mode to the *rule_learner/data* directory
3. if additional GSM data was collected by running the simulation in the *rotation_optimised* mode, copy the log file to the *rule_learner/data* directory as well
4. rename the log file with random data so that its name has the format *&lt;ObjectKey&gt;_&lt;InstanceKey&gt;.log*
5. rename the log file with GSM data so that its name has the format *&lt;ObjectKey&gt;_&lt;InstanceKey&gt;_gsm.log*
6. write the object and instance keys and the GSM resolution in *rule_learner/keys.txt* (each one on a separate line)
7. run *problem_learner.py* (the geometric mapping learning step is usually slow, so this script could take several minutes to finish)
8. run *gsm_learner.py*

A couchdb server should be running before using the software.

The scripts *rule_learner/solve_delta.py* and *rule_learner/solve_delta_without_gsm.py* are meant to be called from external software (such as the Unreal Engine simulation), such that they use the files *rule_learner/keys.log*, *rule_learner/initial_guess.log*, *rule_learner/optimised_guess.log*, and *rule_learner/bad_guesses.log* for interacting with the external software. The *path* variables in the two scripts should be set to the absolute path of *rule_learner* before they are called.
