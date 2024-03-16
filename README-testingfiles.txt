Below are the tests that were run.

Manually run:
Command line args
    - no args
    - numeric args

Test faulty files
    - CMD not found
    - No test files
    - 1 test file not found
    - multiple not found
    - 1 found others not found 
        - mid list and beginning


Automatic tests (bash_testing.sh) - naming scheme:
test faulty cmds 
 t1_1   - filter no args
 t1_2   - fields no args
 t1_3   - replace no args
       - fields
    t1_41    - no quotes
    t1_42    - no fields
    t1_43    - fields non numeric
       - replace 
    t1_51    - one string
    t1_52    - no quotes (one)
    t1_53    - no quotes (both)
    t1_54    - extra string

