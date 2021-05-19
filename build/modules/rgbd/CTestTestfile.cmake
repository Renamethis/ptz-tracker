# CMake generated Testfile for 
# Source directory: /home/user/ptz-tracker/opencv_contrib/modules/rgbd
# Build directory: /home/user/ptz-tracker/build/modules/rgbd
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(opencv_test_rgbd "/home/user/ptz-tracker/build/bin/opencv_test_rgbd" "--gtest_output=xml:opencv_test_rgbd.xml")
set_tests_properties(opencv_test_rgbd PROPERTIES  LABELS "Extra;opencv_rgbd;Accuracy" WORKING_DIRECTORY "/home/user/ptz-tracker/build/test-reports/accuracy")
