# Instance Generator Job Shop Scheduling

## Description
Benchmark generator for the Job Shop Problem (BG-JSP)

## Generating a JSP problem instance

To generate an instance of the problem, we will use the Generator class, located in the Generador module.
To do this, we initialize the generator, giving it the following parameters:

1. **JSON:`json`**
   - **Description**: Parameter that indicates if the generated instance will be stored in JSON format.
   - **Possible values**: Boolean value. Only the values True or False can be obtained.
   - **Example of possible values**: `True`, `False`
   - **Default value**: `False`

2. **DZN:`dzn`**
   - **Description**: Parameter that indicates if the generated instance will be stored in DZN format.
   - **Possible values**: Boolean value. Only the values True or False can be obtained.
   - **Example of possible values**: `True`, `False`
   - **Default value**: `False`

3. **Taillard:`taillard`**
   - **Description**: Parameter that indicates if the generated instance will be stored in taillard format.
   - **Possible values**: Boolean value. Only the values True or False can be obtained.
   - **Example of possible values**: `True`, `False`
   - **Default value**: `False`

4. **Save Path:`savepath`**
   - **Description**: Path where the problem instance file will be generated. 
   - **Possible values**: String.
   - **Example of possible values**: `./problems`, `./instances`
   - **Default value**: `./output`


Once the generator has been initialized, we proceed to generate different instances of the JSP problem with different values for this initialization; for that we use the following function using the following parameters to customize the generated instances:

1. **Jobs:`jobs`**
   - **Description**: Number of jobs that will have the problem generated.
   - **Possible values**: Integer value.
   - **Example of possible values**: `3`, `4`.
   - **Default value**: `10`

2. **Machines:`machines`**
   - **Description**: Number of machines that will have the problem generated.
   - **Possible values**: Integer value.
   - **Example of possible values**: `6`, `2`.
   - **Default value**: `4`

3. **Release and Due Date:`ReleaseDateDueDate`**
   - **Descripción**: Establish that each task has an instant of release and completion limit.
   - **Possible values**: 
      - `0`: Neither the works nor the operations of each of them will have an instant release or time limit for completion.
      - `1`: The work will have an instant of release and instant of completion limit.
      - `2`: The operations of each job will have a release time and a limiting end time.
   - **Example of possible values**: `1`, `2`
   - **Default value**: `0`

4. **Speeds:`speed`**
   - **Description**: Number of speeds that will be available to perform each task.
   - **Possible values**: Integer value.
   - **Example of possible values**: `3`, `5`
   - **Default value**: `1`

5. **Distribution:`distribution`**
   - **Description**: Type of distribution to be followed for data generation.
   - **Possible values**: You can only set one of the following values: `uniform` `normal` `exponential.`
   - **Example of possible values**: `uniform`, `exponential`
   - **Default value**: `normal`

6. **Seed:`seed`**
   - **Description**: Base number for data generation.
   - **Possible values**: Integer value.
   - **Example of possible values**: `84`, `32`
   - **Default value**: `1`

## Example of JSON generated

This JSON shows how the data generated from a JSP problem with 2 machines and 4 jobs will look. For this generation, we have the following code:
``` python
from IGJSP.generador import Generator
generator = Generator(json=True,savepath="output")
generator.generate_new_instance(jobs=4,machines=2,ReleaseDateDueDate=2,distribution="exponential",seed=53) 
```

```json
{
    "nbJobs": [
        0,
        1
    ],
    "nbMchs": [
        0,
        1,
        2,
        3
    ],
    "speed": 1,
    "timeEnergy": [
        {
            "jobId": 0,
            "operations": {
                "0": {
                    "speed-scaling": [
                        {
                            "procTime": 8,
                            "energyCons": 92
                        }
                    ],
                    "release-date": 30,
                    "due-date": 41
                },
                "2": {
                    "speed-scaling": [
                        {
                            "procTime": 17,
                            "energyCons": 84
                        }
                    ],
                    "release-date": 41,
                    "due-date": 77
                },
                "3": {
                    "speed-scaling": [
                        {
                            "procTime": 3,
                            "energyCons": 97
                        }
                    ],
                    "release-date": 77,
                    "due-date": 80
                },
                "1": {
                    "speed-scaling": [
                        {
                            "procTime": 7,
                            "energyCons": 93
                        }
                    ],
                    "release-date": 80,
                    "due-date": 88
                }
            },
            "release-date": 30,
            "due-date": 88
        },
        {
            "jobId": 1,
            "operations": {
                "1": {
                    "speed-scaling": [
                        {
                            "procTime": 4,
                            "energyCons": 96
                        }
                    ],
                    "release-date": 0,
                    "due-date": 5
                },
                "3": {
                    "speed-scaling": [
                        {
                            "procTime": 3,
                            "energyCons": 97
                        }
                    ],
                    "release-date": 5,
                    "due-date": 9
                },
                "2": {
                    "speed-scaling": [
                        {
                            "procTime": 1,
                            "energyCons": 99
                        }
                    ],
                    "release-date": 9,
                    "due-date": 10
                },
                "0": {
                    "speed-scaling": [
                        {
                            "procTime": 6,
                            "energyCons": 94
                        }
                    ],
                    "release-date": 10,
                    "due-date": 17
                }
            },
            "release-date": 0,
            "due-date": 17
        }
    ],
    "minMakespan": 35,
    "minEnergy": 752,
    "maxMinMakespan": 14,
    "maxMinEnergy": 0
}
```
