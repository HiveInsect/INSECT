import re
import yaml
from insect.facts import Fact
from insect.fact_kinds import FactKind

class LineTrackingLoader(yaml.SafeLoader):
    pass


def _construct_mapping_with_line(loader, node, deep=False):
    mapping = yaml.SafeLoader.construct_mapping(loader, node, deep=deep)
    mapping["__line__"] = node.start_mark.line + 1  # 0-indexed라 +1
    return mapping


LineTrackingLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_with_line,
)

# docker-py(Apache License 2.0)의 docker/utils/ports.py에서 가져온 정규식
# 원본: https://github.com/docker/docker-py/blob/main/docker/utils/ports.py
# 변경 없이 그대로 사용, 11개 케이스 직접 검증 완료
PORT_SPEC = re.compile(
    "^"
    "("
    r"(\[?(?P<host>[a-fA-F\d.:]+)\]?:)?"
    r"(?P<ext>[\d]*)(-(?P<ext_end>[\d]+))?:"
    ")?"
    r"(?P<int>[\d]+)(-(?P<int_end>[\d]+))?"
    "(?P<proto>/(udp|tcp|sctp))?"
    "$"
)

DRIVE_AT_FIELD_START = re.compile(r"(?:^|(?<=:))[A-Za-z]:[\\/]")

def _split_short_volume(spec: str) -> list[str]:
    """volume 내부 사용 함수"""
    def protect(m):
        return m.group(0).replace(':', '\x00')
    protected = DRIVE_AT_FIELD_START.sub(protect, spec)
    parts = protected.split(':', maxsplit=2)
    return [p.replace('\x00', ':') for p in parts]


def _as_list(value):
    return value if isinstance(value, list) else []


SIMPLE_FIELDS = {
    "privileged": (FactKind.PRIVILEGED, lambda v: {"enabled": v}),
    "network_mode": (FactKind.NETWORK_MODE, lambda v: {"mode": v}),
    "cap_add": (FactKind.CAP_ADD, lambda v: {"caps": v}),
    "cap_drop": (FactKind.CAP_DROP, lambda v: {"caps": v}),
    "security_opt": (FactKind.SECURITY_OPT, lambda v: {"options": v}),
    "pid": (FactKind.PID_MODE, lambda v: {"mode": v}),
    "ipc": (FactKind.IPC_MODE, lambda v: {"mode": v}),
    "userns_mode": (FactKind.USERNS_MODE, lambda v: {"mode": v}),
}


def parse(file: str) -> list[Fact]:
    facts = []
    with open(file, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=LineTrackingLoader)
        if not isinstance(data, dict):
            return facts

    services = data.get("services", {})
    for service_name, service_config in services.items():
        if not isinstance(service_config, dict):
            continue
        facts += _parse_ports(service_name, service_config, file, service_config.get("__line__", 0))
        facts += _parse_user(service_name, service_config, file, service_config.get("__line__", 0))
        facts += _parse_environment(service_name, service_config, file, service_config.get("__line__", 0))
        facts += _parse_simple_fields(service_name, service_config, file, service_config.get("__line__", 0))
        facts += _parse_volumes(service_name, service_config, file, service_config.get("__line__", 0))
        facts += _parse_devices(service_name, service_config, file, service_config.get("__line__", 0))
        facts += _parse_build_args(service_name, service_config, file, service_config.get("__line__", 0))
        facts += _parse_read_only(service_name, service_config, file, service_config.get("__line__", 0))
        facts += _parse_image(service_name, service_config, file, service_config.get("__line__", 0))

    facts += _parse_networks(data, file, data.get("__line__", 0))

    return facts

def _parse_ports(service_name, service_config, file, line) -> list[Fact]:
    facts = []
    for entry in _as_list(service_config.get("ports", [])):
        if isinstance(entry, dict):
            host = entry.get("host_ip") or "0.0.0.0"
            entry_line = entry.get("__line__", line)
            target_port = entry.get("target")
            host_port = entry.get("published")
            protocol = entry.get("protocol")
            if protocol is None:
                protocol = "tcp"
            # target은 필수 - 없거나 int 변환 실패면 이 entry 통째로 버림
            try:
                target_port = int(target_port)
            except (TypeError, ValueError):
                continue

            # host_port는 선택 - 없으면 None 유지(매핑 안 됨 상태)
            if host_port is not None:
                try:
                    host_port = int(host_port)
                except (TypeError, ValueError):
                    host_port = None
            facts.append(Fact(kind=FactKind.BIND, subject=service_name,
                                attrs={"host": host, "host_port": host_port, "target_port": target_port, "protocol": protocol},
                                file=file, line=entry_line, source_format="compose"))
            continue

        m = PORT_SPEC.match(str(entry))
        if not m:
            continue

        host = m.group("host") or "0.0.0.0"
        ext_start_str = m.group("ext")                    # 호스트 포트 시작 (문자열 or None)
        int_start = int(m.group("int"))                    # 컨테이너 포트 시작
        int_end = int(m.group("int_end") or int_start)
        ext_start = int(ext_start_str) if ext_start_str else None
        protocol = m.group("proto")
        if protocol:
            protocol = protocol[1:]   # "/tcp" -> "tcp"
        elif protocol is None:
            protocol = "tcp"

        for target_port in range(int_start, int_end + 1):
            # target_port가 int_start에서 몇 만큼 진행됐는지에 맞춰 host_port도 함께 이동
            offset = target_port - int_start
            host_port = ext_start + offset if ext_start is not None else None
            facts.append(Fact(kind=FactKind.BIND, subject=service_name,
                            attrs={"host": host, "host_port": host_port, "target_port": target_port, "protocol": protocol},
                            file=file, line=line, source_format="compose"))
    return facts


def _parse_user(service_name, service_config, file, line) -> list[Fact]:
    facts = []
    user = service_config.get("user")   # 없으면 None
    if user is None:
        user = "root"
    facts = [Fact(kind=FactKind.RUN_AS, subject=service_name,
                   attrs={"user": user},
                   file=file, line=line, source_format="compose")]
    return facts


def _parse_environment(service_name, service_config, file, line) -> list[Fact]:
    facts = []
    env = service_config.get("environment", {})
    if isinstance(env, dict):
        entry_line = env.get("__line__", line) 
        for key, value in env.items():
            if key == "__line__":
                continue
            facts.append(Fact(kind=FactKind.ENV_VAR,subject=service_name,
                       attrs={"key":key, "value":value},
                       file=file, line=entry_line, source_format="compose"))
    elif isinstance(env, list):
            for entry in env:
                if not isinstance(entry, str):
                    continue
                if "=" in entry:
                    key, value = entry.split("=",1)
                    facts.append(Fact(kind=FactKind.ENV_VAR,subject=service_name,
                       attrs={"key":key, "value":value},
                       file=file, line=line, source_format="compose"))
                else:
                    key, value = entry, None
                    facts.append(Fact(kind=FactKind.ENV_VAR,subject=service_name,
                       attrs={"key":key, "value":value},
                       file=file, line=line, source_format="compose"))
    return facts


def _parse_volumes(service_name, service_config, file, line) -> list[Fact]:
    # 주의: attrs["options"]는 타입이 혼재함 —
    #   short syntax: mode 문자열("ro", "ro,z" 등) 또는 None
    #   long syntax:  read_only 값(bool) 또는 None
    # 룰에서 이 필드 사용 시 두 타입 모두 처리할 것 (의도된 설계, 원본 보존 우선)
    facts = []
    for entry in _as_list(service_config.get("volumes", {})):
        if isinstance(entry, str):
            parts = _split_short_volume(entry)
            source, mode = None, None
            if len(parts) == 1:
                target = parts[0]
            elif len(parts) == 2:
                source, target = parts[0], parts[1]
            elif len(parts) == 3:
                source, target = parts[0], parts[1]
                mode = parts[2]  # 필요하면 씀
            read_only = mode is not None and "ro" in mode.split(",")
            facts.append(Fact(kind=FactKind.MOUNT,subject=service_name,
                attrs={"source":source, "target":target, "mode":mode, "read_only":read_only},
                file=file, line=line, source_format="compose"))
        elif isinstance(entry, dict):
                source = entry.get("source")
                target = entry.get("target")
                read_only = bool(entry.get("read_only", False))   # 없으면 False로 정규화
                entry_line = entry.get("__line__", line)
                facts.append(Fact(kind=FactKind.MOUNT,subject=service_name,
                    attrs={"source":source, "target":target, "mode": None, "read_only":read_only},
                    file=file, line=entry_line, source_format="compose"))
    return facts


def _parse_devices(service_name, service_config, file, line) -> list[Fact]:
    facts = []
    for entry in _as_list(service_config.get("devices", [])):
        if not isinstance(entry, str):       # ← 첫 줄
            continue
        permissions, container_path = "rwm", None
        parts = entry.split(":", maxsplit=2)
        if len(parts) == 1:
            host_path = parts[0]
        elif len(parts) == 2:
            host_path, container_path = parts[0], parts[1]
        elif len(parts) == 3:
            host_path, container_path, permissions = parts[0], parts[1], parts[2]
        facts.append(Fact(kind=FactKind.DEVICE,subject=service_name,
                    attrs={"host_path":host_path, "container_path":container_path, "permissions":permissions},
                    file=file, line=line, source_format="compose"))
    return facts


def _parse_build_args(service_name, service_config, file, line) -> list[Fact]:
    facts = []
    build = service_config.get("build")
    if not isinstance(build, dict):
        return facts  # build가 없거나 문자열이면 args 자체가 없음
    args = build.get("args", {})
    if isinstance(args, dict):
        entry_line = args.get("__line__", line) 
        for key, value in args.items():
            if key == "__line__":
                continue
            facts.append(Fact(kind=FactKind.BUILD_ARG,subject=service_name,
                       attrs={"key":key, "value":value},
                       file=file, line=entry_line, source_format="compose"))
    elif isinstance(args, list):
            for entry in args:
                if not isinstance(entry, str):
                    continue
                if "=" in entry:
                    key, value = entry.split("=",1)
                    facts.append(Fact(kind=FactKind.BUILD_ARG,subject=service_name,
                       attrs={"key":key, "value":value},
                       file=file, line=line, source_format="compose"))
                else:
                    key, value = entry, None
                    facts.append(Fact(kind=FactKind.BUILD_ARG,subject=service_name,
                       attrs={"key":key, "value":value},
                       file=file, line=line, source_format="compose"))
    return facts


def _parse_read_only(service_name, service_config, file, line) -> list[Fact]:
    enabled = service_config.get("read_only", False)  # 없으면 False(=쓰기 가능=덜 안전)
    return [Fact(kind=FactKind.READ_ONLY, subject=service_name,
                  attrs={"enabled": enabled},
                  file=file, line=line, source_format="compose")]


def _parse_image(service_name, service_config, file, line) -> list[Fact]:
    image = service_config.get("image")
    if not isinstance(image, str):
        return []
    
    digest = None
    if "@" in image:
        image, digest = image.split("@", 1)
    
    name, tag = image, None
        # 미해석 변수 치환(${...})이 있으면 콜론이 변수 문법의 일부일 수 있어
    # tag 분리를 건너뛰고 name에 통째로 관찰만 함 (판단은 안 함)
    if "${" not in image:
        idx = image.rfind(":")
        if idx != -1 and "/" not in image[idx:]:
            name, tag = image[:idx], image[idx+1:]
        
    return [Fact(kind=FactKind.IMAGE, subject=service_name,
                    attrs={"name": name, "tag": tag, "digest": digest},
                    file=file, line=line, source_format="compose")]


def _parse_simple_fields(service_name, service_config, file, line) -> list[Fact]:
    facts = []
    for field, (kind, make_attrs) in SIMPLE_FIELDS.items():
        if field in service_config:
            facts.append(Fact(kind=kind, subject=service_name,
                               attrs=make_attrs(service_config[field]),
                               file=file, line=line, source_format="compose"
                            )
                        )
    return facts


def _parse_networks(data, file, line) -> list[Fact]:
    facts = []
    networks = data.get("networks", {})
    for network_name, network_config in networks.items():
        if not isinstance(network_config, dict):
            continue
        entry_line = network_config.get("__line__", line)
        if network_config.get("internal") is True:
            facts.append(Fact(kind=FactKind.NETWORK, subject=network_name,
                               attrs={"internal": True},
                               file=file, line=entry_line, source_format="compose"))
    return facts