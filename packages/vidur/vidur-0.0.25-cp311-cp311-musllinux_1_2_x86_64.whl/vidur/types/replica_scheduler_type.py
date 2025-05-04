from vidur.types.base_int_enum import BaseIntEnum


class ReplicaSchedulerType(BaseIntEnum):
    FASTER_TRANSFORMER = 1
    ORCA = 2
    SARATHI = 3
    VLLM = 4
    LIGHTLLM = 5
    MNEMOSYNE_FCFS_FIXED_CHUNK = 6
    MNEMOSYNE_FCFS = 7
    MNEMOSYNE_EDF = 8
    MNEMOSYNE_LRS = 9
    MNEMOSYNE_ST = 10
