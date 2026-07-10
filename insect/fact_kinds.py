# insect/fact_kinds.py
from enum import Enum

class FactKind(str, Enum):
    """str도 상속해서, Fact.kind: str 타입이랑 그대로 호환됨."""
    BIND = "bind"
    RUN_AS = "run_as"
    ENV_VAR = "env_var"
    BUILD_ARG = "build_arg"
    NETWORK = "network"
    PRIVILEGED = "privileged"
    READ_ONLY = "read_only"
    NETWORK_MODE = "network_mode"
    PID_MODE = "pid_mode"
    IPC_MODE = "ipc_mode"
    USERNS_MODE = "userns_mode"
    CAP_ADD = "cap_add"
    CAP_DROP = "cap_drop"
    SECURITY_OPT = "security_opt"
    MOUNT = "mount"
    DEVICE = "device"
    IMAGE = "image"