# secoach 설계서 v2 — 노출경로 기반 인프라 보안 코치

> 상태: 2025 수상작 21 + 비수상작 23 전수분석 + 2026 IaC 동향 + 탐지엔진 고도화 연구 반영한 **확정 방향**.
> 이전 `프로젝트설계서_경량화.md`를 대체. 핵심: 범위="인프라 공격경로"로 좁힘 / 래핑→직접 코어 / **의미기반 탐지(문법 아님)+확신도 계층+Datalog 도달성**(§3.5~3.6, 상세는 **부록 A**) / RAG는 `--explain` 옵션 / 코드IaC는 향후.
> ※ 이 문서 = 본문(§0~12) + **부록 A**(탐지 엔진 고도화 상세) 통합본.

---

## 0. 한 줄 정의

> **바이브코딩으로 짠 배포 설정(docker-compose·Dockerfile·Supabase SQL·vercel·env)을 배포 전에 스캔해, 개별 보안 미설정(security smell)을 인프라 전반에서 탐지하고, *연결되면 위험한 조합*(toxic combination = 인터넷→DB 노출 경로)은 상위 분석으로 격상하며, 그 줄만 고치는 게 아니라 *왜 그 부류가 위험한지* 원리를 가르치는 오픈소스 보안 도구 (pip 라이브러리 + CLI).**

핵심 = **인프라 설정 보안 탐지 엔진**(파일감지→파싱→룰→출력) + 그 위 **정확도·시간축 레이어**: ① 의미기반 정밀 탐지(문법 아닌 의미 — FP 감소) ② 확신도 계층 ③ **toxic combination 분석**(개별 smell을 연결, "점"이 아니라 "선") ④ **재발 동적 감지**(전에도 탐지된 패턴을 추적 → 학습 정착 확인). 넓은 커버리지를 위해 **Trivy/Checkov를 번들로 포함**(첫 실행 시 자동 다운로드)해 `secoach scan ./` 하나로 [자체 룰 + Trivy + Checkov]를 통합 실행하고, 차별점은 이 레이어 + **교육**(레슨·레벨·퀴즈)에 둠.

> 💡 **미래지향 포지션(§1.5):** "바이브코딩"은 죽어가는 라벨 → secoach의 지속 가능한 정체성은 **"AI가 생성한 인프라 설정을 *배포 전에* 검증하는 보안 게이트"**. (바이브 스택은 *현재의 주 적용처*일 뿐, 본질은 "AI 생성 인프라 거버넌스")
>
> 📚 **학술 위치(§3.0):** *IaC security smell 정적 탐지*의 확립된 계보(Rahman & Williams ICSE 2019; GLITCH/ASE 2022; IntelliSA 2025; War et al. 2025) 위에 있음 — "혼자 만든 개념"이 아니라 정립된 연구 영역을 *바이브 스택+크로스포맷+교육*으로 확장.

---

## 1. 포지셔닝 — 왜 이게 수상권인가 (근거)

수상작 분석에서 수상을 가른 2가지 기준에 맞춤:

| 가르는 기준 | secoach v2 | 판정 |
|---|---|---|
| **재사용 OSS 컴포넌트**(앱 아님) | pip 라이브러리 + CLI | 🟢 |
| **단단한 기술 코어**(LLM 래퍼 아님) | Attack Path Analysis 엔진(정적·크로스포맷) | 🟢 ← v2의 핵심 보강 |
| 사회적 가치(플러스) | AI 코딩 대중화 → 보안 교육 민주화 | 🟢 |

- Taint-Bomb(보안 수상작)이 "taint 분석" 기법으로 수상한 것처럼, secoach는 **"공격경로 분석(Attack Path Analysis)"이 후크.**
- ⚠️ **정직: 공격경로/도달성 분석은 secoach가 발명한 게 아님.** Wiz·Orca·Microsoft Defender·Checkov가 다 쓰는 **성숙한 보안 기법**이야. secoach의 차별점은 *발명*이 아니라 **그 검증된 기법을 아무도 안 한 자리에 적용**하는 것 → ① 완전 정적(배포 전 파일만, 클라우드 계정 0) ② 크로스포맷(compose↔supabase SQL↔vercel을 *연결*) ③ 개인 개발자/학습자용 ④ 교육 결합. (§3.0 참조)
- AccessibilityFixer(수상작)가 eslint를 래핑하되 *퀵픽스·교육*으로 가치를 더했듯, secoach도 파서는 빌려오되 **그래프·도달성·교육은 직접.**
- 비수상작 함정("스캐너 돌려서 LLM이 설명")을 **공격경로 엔진으로 회피.**
- 💡 "Wiz/Defender가 쓰는 Attack Path Analysis를 바이브스택에 정적 적용"은 심사위원이 *알아보는 정통 패러다임* → "혼자 만든 개념"보다 신뢰도 높음.

---

## 1.5 ⭐ 미래 정합성 — 왜 11~12월 심사 시점에도 안 낡는가

> secoach는 7월 접수→12월 시상. *지금*이 아니라 *6~12개월 뒤* 동향에 베팅해야 함. 결론: **방향은 미래와 정렬, 단 "바이브"라는 *단어*에 의존하면 안 됨.**

**(a) 미래의 큰 줄기 = "거버넌스 격차(governance gap)" — secoach가 정확히 그 쪽.**
- 2026~27 모든 업계 리포트가 한 목소리: 병목이 "AI 코드 *생성*"에서 "AI 코드 *통제·보안·검증*"으로 이동. (채택 92% vs 신뢰 29%, 채택 후 버그율 +41% = 거버넌스 격차)
- AI 생성 코드 취약점 비율 ~50%(인간 15~20%) → **"2027년 사이버보안이 개발자 #1 요구 스킬"**. → secoach의 탐지+교육이 정조준 + 정원 커리어(SOC/DevSecOps)와 일치.

**(b) ⚠️ "바이브코딩" 단어는 죽고 있음 → 라벨 격상 필수.**
- Karpathy가 2026.2 "바이브코딩 한물갔다" 선언. IBM은 "vibe coding → Objective-Validation Protocol(목표정의·검증+에이전트실행+체크포인트 승인)"로 진화 예측.
- → **secoach를 "바이브코딩 보안도구"로 묶지 말 것.** 청중(AI로 인프라 짜는 사람)은 남지만 *라벨*은 바뀜. → 포지션을 **"AI가 생성한 인프라를 배포 전에 검증하는 게이트"**(지속 개념)로. ("바이브"는 예시로만 사용)

**(c) 미래가 secoach 설계 결정을 *검증*:**
- "형식 검증 루프 = AI를 컴파일러·테스트·린팅 게이트 뒤에 두고 통과까지 반복" → **secoach CI 게이트(§6.1)가 바로 이 미래.**
- "부상 베스트프랙티스 = policy-as-code + AI-aware 테스트" → **secoach 룰/Datalog 엔진 = policy-as-code.**
- "바이브 결과물은 독점 런타임 아니라 *배포 가능 코드*" → **secoach의 '파일 스캔' 전제가 갈수록 유효.**
- "참신함 아니라 엔지니어링 규율이 해자" → **secoach 정밀도·벤치마크·Datalog 엄밀함 집중이 정답.**

**(d) ⭐ 미래 확장 레인 = 에이전트 권한/도달성** (향후계획 §10):
- 미래엔 "자율 에이전트의 신원·접근 관리"가 이사회급 관심사("모든 에이전트가 *무엇에 접근*하는가"). 에이전트 권한 오용=권한 상승.
- → **secoach의 도달성/공격경로 엔진은 "인터넷→DB"에서 "에이전트→접근 가능 자원"으로 그대로 확장.** 에이전트 폭증 시대(2026 G2000 직무 40%가 에이전트와 협업)에 *같은 엔진이 미래 질문을 푼다* = 강력한 확장성 서사.

→ **요약: secoach 방향은 미래적합(거버넌스·CI게이트·policy-as-code·규율 해자 모두 정렬). 언어만 "바이브코딩"→"AI 생성 인프라 검증 게이트"로 올리면 심사 시점(11~12월)에도 안 낡고, 에이전트 권한 확장 레인이 future-proofing.**

---

## 2. 타깃 — 선언적 바이브 배포 스택 (확정)

**대상(메인):** AI/바이브코더가 실제로 짜는 *선언적* 배포 설정만.
- `docker-compose.yml`, `Dockerfile`
- `*.sql` (Supabase/Postgres — RLS 누락이 바이브 사고 #1)
- `next.config.js`, `vercel.json`
- (옵션) 간단한 K8s YAML

**의도적으로 제외:**
- ❌ Terraform/OpenTofu 만능 스캔 → Checkov·Trivy·KICS 레드오션 (1000~2400개 룰)
- ❌ Pulumi/CDK 풀 분석 → synth(실행) 필요·재현 어려움·청중(고급 개발자)이 바이브코더 아님
- ❌ 살아있는 서버 점검(SSH/Lynis) → root·GPL·비결정적·2차 테스트 불가

**근거:** 엔터프라이즈 스캐너는 Terraform/CFN/K8s에 집중 → **바이브 스택(compose·supabase·vercel)은 상대적 빈자리** + 크로스포맷 공격경로는 *아무도 안 함*.

**⚠️ "바이브 보안" 코드 SAST는 이미 레드오션 (2025~26 폭발) → 거기 가지 말 것:**
- VibeSec(ferg-cod3s, npm CLI 93룰 코드 SAST), vibesec.sh(AI 스킬, Next.js/Supabase RLS 안다는 24+취약점), vibeappscanner.com(라이브 앱 스캔 $19), vibesecurity.net(IDE+실시간+AI픽스), 0x8506·BehiSecc·benavlabs(AI 스킬/체크리스트) … **떼거리.**
- 이들은 전부 **① 코드 SAST ② AI 코딩 스킬 ③ 라이브 앱 스캔** 중 하나. → **secoach가 "또 하나의 바이브 코드 스캐너"면 즉사.**
- **빈 레인 = 바이브 스택 *인프라 설정* 보안 탐지(compose·SQL·env·vercel은 Trivy도 기본 룰 없음) + 크로스포맷 toxic combination + 교육.** (§3.0 학술 근거 + §3.3 룰 카탈로그가 증거)

---

## 3. 핵심 코어 — 인프라 설정 보안 탐지 엔진

### 3.0 문제 정의 & 학술적 근거 (왜 이게 정통인가)

**A. "security smell" — 우리가 탐지하는 것의 학술 명칭.**
- Rahman & Williams, *"The Seven Sins: Security Smells in Infrastructure as Code Scripts"* (ICSE 2019)이 IaC 보안 결함을 **security smell**(= 취약점을 유발하는 나쁜 설정 패턴)으로 정식화하고 **CWE에 매핑**함. 이후 Kubernetes manifest(ACM TOSEM 2023), Ansible/Chef로 확장.
- → secoach의 "탐지 룰"은 *임의 규칙*이 아니라 **이 security smell 카탈로그의 계보**를 따른다. 각 룰 = 하나의 smell, CWE에 매핑(§3.3).

**B. "정적 분석 + 룰" — 검증된 탐지 패러다임, 단 한계도 명확.**
- 정적 룰 기반 탐지는 표준이지만(tfsec·Checkov·Trivy·KICS), **IntelliSA**(2025)가 정량적으로 보였듯 *룰만 쓰면 과탐(over-approximation)으로 false positive가 폭증*함. IntelliSA는 **symbolic 룰 + neural 추론**을 결합해 F1 83%, 코드의 2%만 검사하고도 smell의 60% 탐지.
- War et al. *"Detection of Security Smells in IaC through Semantics-Aware Processing"* (arXiv 2509.18790, 2025)는 **구문만 보면 FP가 많고, 의미를 이해하면 정밀도가 급등**함을 실증: Ansible에서 precision/recall이 **0.46/0.79 → 0.92/0.88**로 상승.
- → **이 두 논문이 secoach의 핵심 설계(룰 + 의미기반 탐지 + 확신도 계층)를 *직접* 정당화한다.** "룰로 시작하되, 의미 파싱과 확신도로 FP를 잡는다"는 게 SOTA 방향과 일치.

**C. "크로스포맷(polyglot)" — secoach 차별점의 학술 선례.**
- **GLITCH** (Saavedra & Ferreira, ASE 2022)가 *polyglot* security smell 탐지(여러 IaC 언어를 *중간표현으로 통일*해 한 룰셋으로 검사)를 제시. secoach의 "여러 설정 포맷을 공통 Fact로 정규화"가 바로 이 polyglot 접근.
- → secoach = "GLITCH식 polyglot 정규화 + 바이브 스택(compose·SQL·env·vercel)으로 영역 이동 + 그 위 toxic combination 분석 + 교육."

**D. 실세계 동기 (사고 사례 — 보고서 도입부용).**
- 문헌이 인용하는 IaC 미설정 사고: Capital One AWS S3 오설정 유출, Uber 공개 레포 시크릿 노출(2017). 바이브 영역의 현대판 = **CVE-2025-48757** (Lovable 앱 1,645개 중 170개(10.3%)가 anon 키로 DB 노출, §4.3).
- → "설정 하나가 대규모 유출로 전파"는 학술·산업 공통 인식. secoach는 *배포 전*에 그걸 잡는다.

---

### 3.1 탐지 엔진 아키텍처 — 6단 파이프라인

Trivy·Checkov·tfsec의 표준 4단 위에, secoach의 차별점인 **정확도 레이어**(⑤)와 **재발 추적**(⑥)을 더함:

```
① 파일 감지 (Detection)
   디렉토리 순회 → 파일 타입 판별 (compose/Dockerfile/SQL/vercel/env/k8s)
   확장자 + 내용 시그니처(예: "services:" 키 → compose)

② 파싱 → 정규화 (Parse → unified Fact)
   포맷별 파서로 구조화 → 공통 Fact 스키마로 변환 (= GLITCH식 polyglot 중간표현)
   "설정이 없으면 기본값 가정"(Trivy 원칙): Dockerfile에 USER 없음 → root로 간주

②' 통합 탐지 — Trivy/Checkov 번들 (기본 포함)  ⭐ §3.4a
   `secoach scan ./` 하나로 [자체 룰 + Trivy + Checkov] 모두 실행 → 결과 통합·중복제거
   첫 실행 시 Trivy/Checkov 바이너리 자동 다운로드(사용자는 따로 설치 불필요)
   → 자체 룰(compose·sql·env·vercel 빈자리) + 외부 도구(TF·K8s·CFN 수백 룰)를 하나로
   ※ Apache 2.0 다운로드+호출이라 라이선스 안전 / 네트워크 없으면 자체 룰로 폴백

③ 룰 평가 (Rule Evaluation) — 넓은 1차 탐지
   각 룰 = Fact를 받아 위반 검사하는 함수. 룰 레지스트리를 순회.
   ├─ (a) 단일-Fact 룰: 개별 미설정 탐지 (인프라 전반)
   ├─ (b) 의미기반 룰: 정책식·역할·관계 파싱 (§3.5)
   └─ (c) 다중-Fact 룰: toxic combination = 경로 분석 (§3.6)
   + ②'의 외부 finding도 같은 Finding 타입으로 병합

④ ⭐ 정확도 레이어 (secoach 고유 가치 — 빌린 탐지 위에 *얹는* 것)  §3.5~3.6
   A. FP 필터링: 맥락 보고 오탐 강등 (internal망·공개카탈로그 등) ← IntelliSA식
   B. 경로 기반 탐지: 개별 finding을 연결해 toxic combination 격상 ← 아무도 안 함
   C. 의미 심화: Trivy가 놓치는 USING(true)·뷰우회·함수우회 ← CVE 명분
   → "Trivy보다 정확 + Trivy가 못 보는 경로 + Trivy가 놓친 의미"

⑤ ⭐ 재발 동적 감지 (시간축 — stateless 스캐너가 못 하는 것)  §3.6a
   .secoach/history.json과 대조 → "전에도 탐지됨(N회)" 판정
   재발 = 학습 미정착 → 레벨 추가 감점 + 교육 강화(§7)

⑥ 결과 + 메타데이터 (Findings)
   위반 + severity + CWE + 위치 + 레슨ID + 재발이력 → 콘솔/JSON/SARIF
   severity 게이팅(기본 CRITICAL,HIGH) + 인라인 suppression
```

→ **구조 요약:** ①②②'③ = 넓은 1차 탐지(자체 룰 + Trivy/Checkov 번들 통합). **④ = 정확도 레이어(고유 가치).** ⑤ = 재발 추적(시간축). ⑥ = 출력. **커버리지는 검증된 도구를 포함해 기본 제공, 차별점은 ④⑤(정확도+경로+의미+재발)에 집중** — AccessibilityFixer가 eslint를 포함하고 퀵픽스·AI·IDE로 차별화한 것과 같은 전략. (Trivy/Checkov는 *결정적* 도구라 같은 입력=같은 출력 → 번들해도 2차 재현성 안전. LLM과 달리 외부 *비결정* 의존 아님)

---

### 3.2 Fact — 공통 정규화 스키마 (polyglot 중간표현)

모든 포맷을 **하나의 Fact 타입**으로 환원 → 룰은 포맷을 몰라도 됨(GLITCH 원리).

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Fact:
    kind: str          # 정규화된 사실 종류 (아래 표)
    subject: str       # 대상 리소스 (예: "db", "users", "api", "web")
    attrs: dict        # 의미를 담는 속성 (문법이 아니라 의미!)
    file: str
    line: int
    source_format: str # 출처 포맷 (compose/sql/env/...) — 추적용

# 정규화 Fact 종류 (kind) — security smell 카탈로그에 대응
#   bind(subject=db, attrs={host:0.0.0.0, port:5432})        ← 네트워크 노출
#   run_as(subject=web, attrs={user:root})                   ← 권한
#   rls_policy(subject=users, attrs={role:anon, predicate:"true", cmd:SELECT})  ← 인가
#   grant(subject=users, attrs={role:anon, op:SELECT})       ← 인가
#   secret(subject=anon_key, attrs={location:frontend})      ← 시크릿 노출
#   cors(subject=api, attrs={origin:"*"})                    ← 접근제어
#   header(subject=web, attrs={csp:false, hsts:false})       ← 전송보안
#   tls(subject=web, attrs={enabled:false})                  ← 암호화
#   view(subject=v_users, attrs={target:users, security_invoker:false})  ← RLS 우회
#   definer_func(subject=get_users, attrs={guarded:false})   ← RLS 우회
```

**왜 `attrs`에 *의미*를 담나 (War et al. 근거):** `rls:OFF`(문법)가 아니라 `rls_policy(users, role=anon, predicate="true")`(의미)로 저장해야 §3.5의 미묘한 취약(`USING(true)` 등)을 잡는다. 구문 토큰만 보면 FP↑(precision 0.46), 의미를 담으면 precision 0.92. **Fact 스키마 설계 = 정밀도의 출발점.**

---

### 3.3 룰 — 플러그인 인터페이스 (smell 1개 = 룰 1개 = 파일 1개)

각 룰은 **정해진 인터페이스만 구현** → 누구나 PR로 추가(§6.2 기여 구조와 직결).

```python
@dataclass
class Finding:
    rule_id: str       # "DB_EXPOSED"
    severity: str      # CRITICAL|HIGH|MEDIUM|LOW
    cwe: str           # "CWE-1327" — Rahman 계보의 CWE 매핑
    subject: str
    file: str
    line: int
    message: str
    lesson_id: str     # 교육 연결 (§5)
    evidence: list[Fact] = field(default_factory=list)  # 근거 Fact(들)

class Rule(Protocol):
    id: str
    severity: str
    cwe: str
    def detect(self, facts: list[Fact]) -> list[Finding]: ...

# 예시 1) 단일-Fact 룰 — 개별 미설정 (인프라 전반 탐지의 기본 단위)
class DbExposedRule:
    id, severity, cwe = "DB_EXPOSED", "HIGH", "CWE-1327"
    def detect(self, facts):
        out = []
        for f in facts:
            if f.kind == "bind" and f.attrs.get("host") == "0.0.0.0" \
               and f.attrs.get("port") in DB_PORTS:
                out.append(Finding(self.id, self.severity, self.cwe,
                    f.subject, f.file, f.line,
                    f"{f.subject} DB 포트가 외부(0.0.0.0)에 바인딩됨",
                    lesson_id="CWE-1327_db_exposed", evidence=[f]))
        return out
```

**룰 카탈로그 (인프라 전반 — security smell 계보 따라 CWE 매핑):**

| 룰 ID | smell / 잡는 것 | CWE | 분류 | 타입 |
|---|---|---|---|---|
| `RLS_MISSING` | RLS 미적용 테이블 | CWE-862 | 인가 | 단일/의미 |
| `RLS_PERMISSIVE` | RLS 있으나 `USING(true)` | CWE-862 | 인가 | 의미(§3.5) |
| `DB_EXPOSED` | DB 0.0.0.0 바인딩 | CWE-1327 | 네트워크 노출 | 단일 |
| `ANON_KEY_FRONTEND` | 공개키/시크릿 프론트 노출 | CWE-200 | 정보노출 | 단일 |
| `CORS_WILDCARD` | `origin:"*"` | CWE-942 | 접근제어 | 단일 |
| `MISSING_SEC_HEADERS` | CSP/HSTS 부재 | CWE-693 | 방어부재 | 단일 |
| `CONTAINER_ROOT` | USER 미지정/root | CWE-250 | 과대권한 | 단일(기본값가정) |
| `PLAINTEXT_TLS` | TLS/SSL 미설정 | CWE-319 | 암호화 | 단일 |
| `HARDCODED_SECRET` | 키/비번 평문 | CWE-798 | 시크릿 | 단일(정규식+엔트로피) |
| `VIEW_BYPASS_RLS` | 뷰가 RLS 우회 | CWE-862 | 인가 | 의미(§3.5) |
| `DEFINER_FUNC_UNGUARDED` | SECURITY DEFINER 무가드 | CWE-862 | 인가 | 의미(§3.5) |

→ **이게 "인프라 보안 전반 탐지"의 실체.** 룰을 추가할수록 커버리지가 넓어짐(Trivy/Checkov가 룰 수백 개로 하는 것과 동일 구조, secoach는 바이브 스택에 집중). 단일-Fact 룰은 쉬워서 *분량*만 들고, 의미 룰(§3.5)이 *전문성*.

**실전 디테일 (Trivy/Checkov에서 가져온 실사용 요소):**
- **"없으면 기본값 가정"**: 리소스에 설정이 명시 안 되면 *안전하지 않은 기본값*으로 간주(예: `USER` 없음=root). 미설정도 탐지 대상.
- **severity 게이팅**: 기본 `--severity CRITICAL,HIGH`. 전부 켜면 노이즈로 사용자가 일괄 무시 → 점진 확대 권장.
- **인라인 suppression**: `# secoach:ignore:DB_EXPOSED` 주석으로 개별 무시(.trivyignore식 디렉토리 단위도 지원).
- **출력 = SARIF**: GitHub code scanning 표준(CodeQL·Trivy·Checkov 공통) → Security 탭 통합.

---

### 3.4 파서 (빌려옴 — 바퀴 재발명 X)

| 대상 | 파서 | 산출 |
|---|---|---|
| docker-compose / k8s / yaml | `PyYAML` | dict → Fact |
| Dockerfile | `dockerfile-parse` | 명령 리스트 → Fact |
| `*.sql` (Supabase/Postgres) | `sqlparse` | 토큰트리 → **의미 파싱**(§3.5) |
| next.config.js / vercel.json / .env | `json` + 정규식 | dict → Fact |
| (향후) `*.tf` | `python-hcl2` | dict → Fact |

→ **secoach가 직접 만드는 것 = ① Fact 정규화 로직 ② 룰셋 ③ 의미 파싱(§3.5) ④ toxic combination 분석(§3.6) ⑤ 교육 매핑.** 파싱은 라이브러리, *가치는 정규화·룰·의미·연결*. (특히 compose·vercel·env·SQL은 Trivy가 기본 룰을 안 제공 → secoach의 빈자리.)

---

### 3.4a ⭐ 통합 탐지 — 자체 룰 + Trivy + Checkov를 하나로 (번들·기본 포함)

> 전략: **탐지 커버리지(레드오션)는 검증된 도구를 *번들로 포함*해 항상 쓰고, 차별점(정확도·경로·의미·재발·교육)을 그 위에 얹는다.** 수상 선례 = AccessibilityFixer가 eslint를 *의존성으로 자동 포함*하고 퀵픽스·AI·IDE로 차별화해 수상 — secoach도 같은 전략을 Trivy/Checkov로.

**한 명령으로 다 돈다:**
```
$ secoach scan ./
  → [자체 룰] + [Trivy] + [Checkov]가 모두 실행되고 결과가 하나로 통합됨
```
`--with-trivy` 같은 플래그 불필요. **기본이 통합 스캔.** (끄려면 `--no-external`로 자체 룰만 — 디버그/오프라인용)

**번들 — 사용자는 Trivy를 따로 안 깔아도 됨 (자동 다운로드):**
- `pip install secoach` 후 **첫 실행 시 Trivy/Checkov 바이너리를 자동 다운로드·캐시**(`~/.secoach/bin/`). 이후 항상 포함.
- Playwright가 브라우저를, Pyright가 Node를 자동 설치하는 것과 동일한 검증된 패턴.
- → 사용자·심사위원 모두 `pip install secoach` 하나로 풀스캔(Trivy 존재를 몰라도 됨). **2차 기능테스트(10/12~28)도 INSECT만 설치하면 작동.**
- 폴백: 네트워크 없음/다운로드 실패 시 자체 룰로 자동 축소 실행(완전 불능 방지) + 경고.

**통합 메커니즘 — 결과를 하나로 합치는 법 (③ 룰 평가 단계):**
```
① 자체 룰 실행      → Finding[] (compose·SQL·env·vercel = Trivy 빈자리)
② Trivy 호출        → SARIF → Finding[]로 정규화
③ Checkov 호출      → SARIF → Finding[]로 정규화
④ 병합 + 중복제거    → 같은 (룰계열, 대상, 위치)는 하나로 (provenance 보존)
⑤ 정확도 레이어(§3.5~3.6) 적용 → FP필터·경로·의미·재발
```
- **중복제거**: Trivy·Checkov·자체 룰이 *같은 취약*을 각각 경고할 수 있음(예: S3 public). `(취약 부류 + 대상 리소스)`로 묶어 **하나의 Finding**으로, "어느 엔진이 잡았나(provenance)"는 메타로 보존.
- → 사용자는 "S3 public" 경고를 3번이 아니라 1번 봄. (env zero가 지적한 "두 스캐너가 같은 버킷 두 번 경고하는 노이즈"를 secoach가 흡수)

**라이선스 (2차 게이트 — 번들이라 더 신경 씀):**
| 항목 | 라이선스 | 번들 방식 | 안전성 |
|---|---|---|---|
| Trivy | Apache 2.0 | 첫 실행 시 *다운로드*(배포 패키지에 미포함) → 호출 | 🟢 |
| Checkov | Apache 2.0 | 동일 | 🟢 |
| secoach 자체 | MIT | — | 🟢 |
- **다운로드+호출**은 *배포 포함*보다 가벼움(NOTICE 고지는 README에 명시). Apache 2.0은 호출·재배포 자유 → 2차 라이선스 검증(10/12~28) 통과.
- ⚠️ 만약 바이너리를 패키지에 *동봉*하게 되면 Apache LICENSE/NOTICE 동봉 의무 발생 → **다운로드 방식 유지**가 깔끔.

**역할 분담 (통합 안에서):**
| 영역 | 누가 | 이유 |
|---|---|---|
| Terraform·K8s·CFN·Dockerfile 점 검사 | **Trivy/Checkov**(번들) | 이미 수백~수천 룰, 레드오션 |
| **compose·SQL(RLS)·env·vercel** | **secoach 자체 룰**(§3.3) | Trivy 기본 룰 없음 = 빈자리 |
| FP필터·경로(toxic combination)·의미(USING(true))·재발 | **secoach 직접**(§3.5~3.6a) | 고유 가치 |
| 교육(레슨·레벨·퀴즈) | **secoach 직접**(§5,§7) | 아무도 안 함 |

→ **핵심: `secoach scan ./` 하나로 [자체 룰 + Trivy + Checkov]가 통합 실행 → 넓은 커버리지를 기본 제공하고, 그 위에 정확도·경로·재발·교육으로 차별화.** "또 하나의 Trivy"가 아니라 "Trivy/Checkov를 *포함하면서* 정확도·경로·교육을 더한 상위 도구" — AccessibilityFixer가 eslint를 포함하며 가치를 얹은 것과 동일.

---

### 3.5 ⭐ 의미기반 정밀 탐지 — "문법이 아니라 의미" (정밀도 레이어)

> **여기가 전문성이 갈리는 곳.** War et al.(2025)이 정량 입증: 구문만 → precision 0.46 / 의미 이해 → 0.92. secoach는 ML 대신 **도메인 특화 의미 파싱**으로 같은 효과를 결정적으로 달성.

**핵심 원칙: 키워드 매칭 ❌ → 정책식·역할·관계 파싱 ⭕.**

가장 ROI 높은 도메인 = **Supabase RLS**(바이브 사고 #1, CVE-2025-48757). "RLS 켜졌나?"만 보면 미탐·오탐 둘 다 발생:

| 패턴 | 왜 grep이 실패 | 의미 탐지법 | 룰 |
|---|---|---|---|
| RLS 켜고 `USING(true)` | "ENABLE RLS" 있어서 통과시킴 | 정책 *식* 파싱 → 무조건 허용 판정 | `RLS_PERMISSIVE` |
| 뷰가 RLS 우회 | 테이블만 보면 안전해 보임 | 뷰의 `security_invoker` 확인 | `VIEW_BYPASS_RLS` |
| SECURITY DEFINER 함수 | 함수 정의는 평범 | `auth.uid()` 가드 유무 검사 | `DEFINER_FUNC_UNGUARDED` |
| `auth.uid()` 쓰나 `TO authenticated` 없음 | 정책 존재해서 통과 | 역할 명시 검사 | `RLS_ROLE_UNSCOPED` |
| 정책이 `user_metadata` 의존 | 정책 있어서 통과 | 술어가 사용자수정가능 claim인지 | `RLS_USER_METADATA` |

**오탐 억제(정밀도 — IntelliSA 교훈: 룰만으론 과탐):**
- 진짜 공개 데이터(국가목록 등) RLS off = 의도됨 → LOW로 강등(필드 민감도로 테이블 의미 구분).
- `service_role` 명시 정책 = "아무것도 안 함"(혼동 신호지 취약 자체 아님) → 노이즈 제거.

→ 상세 구현·전체 패턴은 **부록 A §4**. 핵심: **의미 파싱이 secoach를 "순진한 스캐너"에서 "정밀 탐지기"로 격상**(War et al. 0.46→0.92가 학술 근거).

---

### 3.6 ⭐ Toxic Combination 분석 — 개별 룰을 *연결*하는 상위 레이어 (경로)

> **경로는 메인이 아니라 *상위 분석 능력 하나*.** 개별 룰(§3.3)이 찾은 Fact들을 *연결*해, 각각은 저위험이어도 *조합되면* 위험한 경우를 탐지. 업계 정식 용어 = **toxic combination / attack path / reachability**(Wiz·Orca·Defender·Checkov 그래프 정책).

**A. 무엇인가 (정통 기법, 발명 아님).**
- **toxic combination**: 개별로는 저위험인데 *함께 있으면* 악용 경로가 되는 설정 조합.
- **choke point**: 여러 경로가 지나는 길목 — 하나 끊으면 다중 차단.
- secoach는 이를 *바이브 스택 + 정적 + 크로스포맷*에 적용. (Checkov의 cross-resource 그래프 정책 CKV2_*과 같은 계열, 단 포맷을 가로지름)

**B. 어떻게 (Fact 그래프 + 도달성).**
```
개별 룰이 만든 Fact들 → 신뢰 그래프 구성
  노드: [인터넷] [프론트] [API] [DB] [시크릿]
  엣지: Fact가 함의하는 "도달 가능" 관계
        bind(0.0.0.0)        → 인터넷→DB 엣지
        rls_policy(anon,true)→ DB→테이블(익명) 엣지
        secret(frontend)     → 프론트→키 엣지
→ 도달성 질의: 신뢰X 출발점(인터넷/익명)에서 민감 도착점(DB/시크릿)까지 경로?
  경로 존재 = toxic combination = 개별 경고보다 높은 severity로 격상
```

**C. 차단 모델링 (FP 억제 — 부록 A §1).**
- 단순 "포트 열림"이 아니라 *차단 요소*를 negation으로 모델링: `internal:true` 네트워크, 인증 프록시 뒤 → `blocked`. "포트 떴지만 실제 막힘"(오탐 #1원) 제거.
- 엔진: 손코딩 BFS로 시작 → 선택적 **Datalog(Soufflé)** 이관(재귀 도달성 + negation + `explain`으로 유도트리=경로설명 공짜). 선례 **Semia**(arXiv 2605.00314).

**D. 출력 — 개별 Finding과 *함께* (둘 다 보여줌).**
```
$ secoach scan ./my-vibe-app

═══ 🔴 Toxic Combination (CRITICAL) — 익명 사용자가 회원 DB 유출 가능 ═══
  [인터넷] ─ compose:14 ports "0.0.0.0:5432" ─▶ [Postgres]
           ─ schema.sql:1 users RLS 미적용     ─▶ [users]
           ◀─ .env:3 ANON_KEY 프론트 노출
  ▸ 왜: 세 설정 각각은 흔한 실수지만 *연결되면* 익명 인터넷 사용자가 전체 조회.
  ▸ 원리: 신뢰경계 — 인터넷↔DB 사이 인증/격리 0.
  ▸ 차단: 셋 중 하나만 끊어도 경로 차단(포트 내부전용 OR RLS OR 키 권한). choke point=RLS.

═══ ⚠️ 개별 점검 (경로에 안 엮인 smell) ═══
  • Dockerfile:1  root 실행            (CWE-250, HIGH)
  • next.config   보안헤더 누락         (CWE-693, MEDIUM)
  • nginx.conf    TLS 미설정            (CWE-319, HIGH)

  점수: 64/100 (D)  ·  CRITICAL 1, HIGH 2, MEDIUM 1
```

→ **이게 "둘 다"의 통일된 형태:** 같은 엔진이 ①개별 smell을 다 찾고(인프라 전반) ②연결되는 것은 toxic combination으로 격상(경로). **경로가 안 나와도 개별 탐지는 항상 작동** → 경로는 *부가가치 레이어*지 의존 대상 아님.

**E. 확신도 계층 (경로의 신뢰도 — 부록 A §2).**

| 등급 | 조건 | 표시 |
|---|---|---|
| 🔴 exploitable | 경로 + 무차단 + 익명 source | CRITICAL(단정) |
| 🟡 reachable | 경로 있으나 차단 불확실 | "가정: 외부 방화벽 없음"(확인필요) |
| ⚪ point | 나쁜 설정이나 경로 미성립 | 개별 severity |

→ 개별 smell(point)과 toxic combination(exploitable)을 *다른 확신도*로 표기 → "오탐처럼 안 느끼게"(IntelliSA의 FP 문제의식과 동일 해법).

---

### 3.6a ⭐ 재발 동적 감지 — 시간축 추적 (stateless 스캐너가 못 하는 것)

> Trivy·Checkov는 **상태 없음(stateless)** — 매번 0부터, "전에 지적했는데 또?"를 모름. secoach는 **스캔 이력을 기억**해 "이거 전에도 탐지됐던 패턴(N회)"을 감지. → 교육 도구의 핵심: "한 번 가르치고 끝"이 아니라 *학습이 정착됐는지* 추적.

**A. 재발 판정 키 = `룰 ID + 대상(subject)`.**
- `RLS_MISSING:users`가 또 나오면 = 재발. 줄 번호가 바뀌어도 추적되고, 다른 테이블(`RLS_MISSING:orders`)은 별개로 봄.
- (룰 ID만 = 너무 거침 / 룰+줄번호 = 줄 바뀌면 놓침 → **룰+대상**이 균형)

**B. 이력 저장 — `.secoach/history.json` (로컬, DB 없음).**
```json
{
  "RLS_MISSING:users": {
    "first_seen": "2026-07-01",
    "occurrences": [
      {"date": "2026-07-01", "status": "detected"},
      {"date": "2026-07-08", "status": "fixed"},      // 사라짐(고쳐짐)
      {"date": "2026-07-20", "status": "regressed"}   // 다시 나타남 ⚠️
    ],
    "count": 3
  }
}
```
- 매 스캔: 이번 finding 집합 vs 직전 집합 비교 → `detected`(신규) / `fixed`(사라짐) / `regressed`(고쳤다 재발) / `persistent`(계속 있음) 분류.

**C. 출력 — 재발은 다르게 경고 + 교육 강화.**
```
⚠️ RLS_MISSING @ users — 재발 3회 (07-01 최초 → 07-08 수정 → 07-20 재발)
   "이 패턴을 반복해서 놓치고 있어. 같은 부류가 또 나왔다는 건
    원리가 아직 안 잡혔다는 신호 → 다른 각도로 다시:"
   → 교육: 기초 설명이 아니라 '왜 자꾸 이걸 빠뜨리나'의 근본 원리 + 체크리스트
   → 레벨(§7): 기본 감점 + 재발 페널티 (반복할수록 누적)
```

**D. 왜 강력한 차별점인가:**
- **교육 정착 추적**: 재발 = 아직 학습 안 됨 → *맞춤 재교육*(같은 레슨 반복이 아니라 다른 각도). 적응형 교육의 핵심 신호.
- **추세 가시화**: 정적 스캔에 *시간축*을 더해 "이 프로젝트 보안이 나아지나/나빠지나"를 봄(`fixed` 증가 = 학습 중, `regressed` 증가 = 위험).
- **레벨 게임화와 결합**: 재발 페널티 = "같은 실수 반복하면 등급 하락" → 행동 교정 동기(§7).
- **아무도 안 함**: 기존 스캐너는 stateless라 구조적으로 불가. CI에 붙이면 "PR마다 재발 여부"까지 추적(§6.1).

**E. 정직한 한계:**
- 로컬 `history.json` 기반 → 협업 시 공유 필요(향후: CI 아티팩트나 레포 커밋으로 이력 공유).
- 대상(subject) 식별이 모호한 경우(익명 리소스) 키 안정성 ↓ → 지문(fingerprint) 폴백 옵션.

---

### 3.7 LLM의 자리 (옵션 — 코어는 결정적)

> War et al./IntelliSA가 ML/LLM으로 정밀도를 올렸지만, secoach 코어는 **결정적(deterministic)**으로 유지(2차 기능테스트 재현성). LLM은 *옵션 레이어*:
- `--explain`: 탐지된 smell을 이 코드 맥락으로 설명(RAG, BYOK). 1차 영상 데모용.
- `--deep`: 커스텀 설정(예: 비표준 프록시가 DB로 포워딩?)을 LLM이 *후보 Fact로 표면화* → 결정적 엔진이 판정(neuro-symbolic, IntelliSA/Semia 패턴). 재현율↑, 단 코어 밖.

→ **코어(파싱·룰·의미·경로) = LLM 0, 매번 같은 출력.** LLM은 설명·재현율 보강의 옵션. (근거: §5.1b)

---

## 4. 탐지 룰 — 카탈로그 상세

> §3.3이 룰 *인터페이스와 핵심 카탈로그*(11종), 이 절은 *도메인별 심화 패턴*. 룰셋의 전체 그림 = §3.3 표 + 아래 의미기반 RLS 전체 패턴 + 향후 코드형 IaC.

### 4.1 의미기반 RLS 룰 — 전체 패턴 (성능 ROI 최고, §3.5 심화)

> §3.5에서 핵심 5패턴을 다뤘고, 여기 *전체*를 정리. "RLS 켜졌나?"는 미탐·오탐 둘 다 냄 → **정책식·역할·뷰·함수·grant를 파싱**. 상세 구현은 부록 A §4.

**미탐(FN) 방지 — grep으로 못 잡는 진짜 취약:**
| 패턴 | 왜 위험 | 탐지법 | 룰 ID |
|---|---|---|---|
| RLS 켜고 `USING(true)` | RLS 없는 것과 동일 (**AI 생성기 #1 실수**) | 정책 *식* 파싱 → 무조건 허용 탐지 | `RLS_PERMISSIVE` |
| RLS 미적용 테이블 | anon 키로 전체 SELECT | CREATE TABLE에 ENABLE RLS 결합 확인 | `RLS_MISSING` |
| SQL editor 생성 테이블 | 대시보드와 달리 RLS 기본 OFF | 명시적 ENABLE 확인 | `RLS_MISSING` |
| GRANT + RLS off | 신규 테이블 anon auto-grant → 노출 | `GRANT...TO anon` + RLS상태 결합 | `RLS_GRANT_LEAK` |
| 뷰(View) | 기본 security definer라 RLS 우회 (PG15+ `security_invoker=true` 필요) | 뷰가 보호테이블 노출하는지 | `VIEW_BYPASS_RLS` |
| SECURITY DEFINER 함수/RPC | anon 호출 시 RLS 우회 | `auth.uid() IS NOT NULL` 가드 유무 | `DEFINER_FUNC_UNGUARDED` |
| Storage 버킷 public | 같은 RLS 엔진 — 전체 읽기 | 버킷 public 여부 | `STORAGE_PUBLIC` |

**오탐/심각도 뉘앙스(정밀도 — IntelliSA 교훈: 룰만으론 과탐):**
- 진짜 공개 데이터(국가목록 등) RLS off = 의도됨 → LOW (필드 민감도로 테이블 의미 구분)
- 정책이 `auth.uid()` 쓰는데 `TO authenticated` 없음 → anon에도 실행(null) — `RLS_ROLE_UNSCOPED`
- 정책이 `user_metadata`(사용자 수정가능 JWT) 의존 → 권한상승 — `RLS_USER_METADATA`
- 정책에 `service_role` 명시 → "아무것도 안 함"(혼동 신호지 취약 자체 아님) → 노이즈 제거

**실세계 근거 (보고서 킬러):** CVE-2025-48757 (2025.5) — 분석한 Lovable 앱 1,645개 중 **170개(10.3%)·엔드포인트 303개가 anon 키로 테이블 노출.** "AI 빌더+Supabase면 검증 전엔 RLS 미설정이라 가정하라." → secoach 타깃이 *실재·거대*하다는 정량 증거. (학술 계보: Capital One S3·Uber 시크릿 노출의 바이브 영역 현대판)

→ Supabase 앱 top 취약 3종(① RLS 미설정 ② service_role 키 노출 ③ 허용적 정책) — 개별 탐지(§3.3) + 연결 시 toxic combination(§3.6)으로 격상.

### 4.2 코드형 IaC — AST 패턴 (향후 확장)

- synth(실행) ❌ → **Semgrep식 AST 패턴매칭으로 흔한 안티패턴 몇 개만** 결정적으로:
  - 보안그룹 `cidrBlocks: ["0.0.0.0/0"]` / S3 `publicReadAccess: true` / 하드코딩 시크릿
- 대상: Pulumi/CDK의 TS/Python 소스 (3~5개 룰만, "맛보기")
- 💡 **AST 패턴매칭(검색모드)은 Semgrep OSS로 됨** — 파일 간 흐름(테인트 인터프로시저)만 Pro라, 단일 패턴 룰은 무료로 직접 작성/호출 가능.
- **위치: MVP 미포함, "향후 계획"(§10).** Pulumi Neo 같은 *AI 생성 코드형 IaC* 트렌드 인용 → 시의성·확장성.

## 5. 교육 엔진 — 결정적 레슨 DB

### 5.1 두 모드 — 결정적 코어(주인공) + RAG `--explain`(조연)

**핵심 원칙: LLM API를 *쓰되* 메인이 아니라 옵션 자리에 둔다.**
("LLM 쓰지 마"가 아님 — "LLM이 *핵심 동작*이면 안 됨".)

```
secoach scan ./              → 결정적 레슨 (키 없이, 매번 같은 출력, 항상 작동) ← 기본
secoach scan ./ --explain    → + RAG로 이 코드 맞춤 설명 (네 키 있을 때만) ← 옵션
```

- **코어(노출경로 탐지 + 결정적 레슨) = LLM 無.** 입력→고정출력이라 테스트 가능·외부의존 없음.
- **`--explain` = RAG 레이어.** BYOK(환경변수 키), LiteLLM, 코드해시 캐시. 이 코드 맥락 맞춤 설명.

### 5.1a 평가 단계별 전략 (왜 이 구조인가)

| 단계 | 무엇 | secoach 모드 | 이유 |
|---|---|---|---|
| **1차 (9/3~4) = 서면+영상** | 심사위원이 *네 시연영상* 시청 | **`--explain` RAG를 메인 셀링포인트로 시연** | 네 컴퓨터/네 키로 녹화 → **LLM API 전혀 문제없음.** 동적 맞춤설명을 화려하게 보여줌 |
| **2차 (10/12~28) = 기능테스트** | "실제 구현 검증" (재현성 중요) | **결정적 모드로 검증 보장** | 키 없이·매번 같은 출력 → 검증 깔끔. 외부 API 장애에도 코어 작동 |

→ **즉 RAG 동적은 버리는 게 아니라 `--explain`으로 살아있고, 1차 영상의 주력 데모가 됨.** 2차는 결정적 코어가 받쳐서 안전.

### 5.1b LLM을 메인에 안 두는 진짜 이유 (키 문제 아님)
1. **재현성**: LLM은 같은 입력에 매번 다른 출력 → 2차 기능테스트에서 "정확히 작동"을 검증하기 어려움. 결정적은 깔끔.
2. **외부 의존**: 기능테스트 기간 중 API 장애·rate limit·키 만료 시 데모 사망 → 통제 밖. 결정적은 오프라인도 작동.
3. **"LLM 래퍼" 인상**: 비수상작 다수가 "스캐너+LLM 설명"으로 떨어짐 → LLM이 핵심이면 그 부류로 묶임. 노출경로(직접 코어)가 주인공이어야 함.

### 5.2 레슨 4단 표준구조 (CWE/경로타입별)
```yaml
# lessons/CWE-862_rls_missing.yaml
cwe: CWE-862
title: "Row Level Security 누락"
steps:
  why:    "RLS 없으면 anon 키만으로 테이블 전체 SELECT 가능..."
  attack: "supabase.from('users').select('*')  // 익명 키로 전체 조회"
  fix:    "ALTER TABLE users ENABLE ROW LEVEL SECURITY;\nCREATE POLICY ..."
  principle: "신뢰경계: 데이터 접근은 '누가'에 따라 격리돼야. 인증≠인가."
```
- 30~50개 CWE 레슨을 difficulty 태그(기초/심화)와 함께.
- 적응형: 레벨 낮으면 기초, 높으면 심화, 반복 부류는 다른 각도(옵션).

---

## 6. 형태 & 배포

- **메인: pip 라이브러리 + CLI** (재사용 OSS = 수상측). `pip install secoach` → `secoach scan ./`
- 라이브러리 API도 노출: `from secoach import scan; paths = scan("./")`
- **IDE 플러그인(VSCode)은 향후 옵션** — 보안 수상작 2개(Taint-Bomb·AccessibilityFixer)가 다 IDE라 데모엔 강하지만, 1달 솔로엔 CLI가 안전. 여유 되면 v2.
- 한 줄 가치: **"스캔이 인프라 보안을 가르친다."** (itdoc "테스트가 문서를 쓴다" 식)

### 6.1 사용 방식 — 수동 + 자동(옵션)

**수동(기본):** `secoach scan ./` — 개발자가 직접 실행.

**자동 실행(옵션) — 결정적 코어라 가능 ⭐:**

| 방법 | 동작 | 비고 |
|---|---|---|
| **pre-commit 훅** | 커밋마다 자동 스캔, 취약경로 시 차단 | `.pre-commit-config.yaml` 등록. 로컬 자동화 |
| **GitHub Actions (CI)** ⭐ | PR마다 자동 스캔 → 코멘트 + 체크 실패 | 데모의 중심. shift-left 보안 |
| **SARIF 출력** | GitHub Security 탭 + 인라인 경고 통합 | CodeQL·Semgrep·Trivy 표준 통로 |

```yaml
# .github/workflows/secoach.yml — PR 자동 스캔
on: [pull_request]
jobs:
  secoach:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install secoach
      - run: secoach scan ./ --fail-on critical --format sarif
```

→ **자동화는 "결정적 코어" 결정의 직접 결과:** 키 없이·매번 같은 결과·<1초·표준출력(`--fail-on`/`--format sarif`)이라 CI에서 돎. (LLM이 메인이었으면 키·비결정성으로 불가). **RAG `--explain`은 자동화에서 빠지고 로컬 옵션으로만.**

**왜 수상 포인트인가:** ① "PR마다 자동 도는 보안 게이트" = 재사용 OSS 증명(수상 공통점) ② 시연영상서 "PR→자동 경로탐지+교육코멘트" = 데모 임팩트 ③ shift-left = DevSecOps 명분(스패로우 어필).

### 6.2 ⭐ 오픈소스 기여 구조 — "혼자 만든 도구"가 아니라 "생태계 씨앗"

> 오픈소스 대회의 *더 깊은* 취지 = "커뮤니티가 함께 키우는". secoach는 솔로지만 **기여하기 쉬운 구조를 설계로 박아** 그 취지를 살림. (이게 확장성 점수 + "협업 가능한 OSS" 서사)

**(a) 룰 = 플러그인 (룰 하나 = 파일 하나, PR 한 단위)**
```
secoach/rules/
  rls_missing.py        # 룰 1개 = 파일 1개. 등록만 하면 엔진이 자동 인식
  port_exposed.py
  anon_key_leak.py
```
- 각 룰은 정해진 인터페이스(`detect(facts) -> Finding`)만 구현 → **누구나 새 룰을 PR로 추가.**
- 기여자는 엔진 내부를 몰라도 "이 패턴 잡는 룰" 하나만 짜면 됨.

**(b) 레슨 = YAML 한 개 = 기여 한 단위 (코드 몰라도 기여 가능)**
```
secoach/lessons/
  CWE-862_rls_missing.yaml   # §5.2 4단 구조. 보안 지식만 있으면 기여
```
- **코드 못 짜도 "레슨 YAML"이나 "다국어 번역"으로 기여** → 보안 전문가·교육자·번역가까지 기여 풀이 넓음.
- → secoach의 가치 = 코드뿐 아니라 **커뮤니티가 쌓는 "취약 패턴·레슨 DB"** (오픈소스 협업의 전형).

**(c) 벤치마크 = 커뮤니티 자산**
- 취약/안전 샘플(§8)도 PR로 추가 → 케이스가 늘수록 정밀도·재현율이 *함께* 좋아짐. "기여가 곧 품질 향상"의 선순환.

**(d) 표준 OSS 위생 (기여 환영 신호)**
- `LICENSE`(MIT), `CONTRIBUTING.md`(룰/레슨 기여법 명시), 이슈/PR 템플릿, `good-first-issue` 라벨("첫 룰 추가" 같은).
- README에 **"새 탐지 룰·레슨을 PR로 환영"** 명시 = 커뮤니티가 키우는 그림.

→ **효과:** ① 오픈소스 대회 취지 적중("함께 키우는") ② 확장성 어필(향후 룰 100개를 커뮤니티가) ③ "생태계 씨앗" 서사 — 보고서·발표의 강력한 한 줄.

---

## 7. 점수/레벨/퀴즈 (교육 게임화, 경량)

- **점수**: 100점 시작, severity별 감점(critical-25/high-10/medium-5/low-2) → 등급 A+~F.
- **⭐ 재발 페널티**(§3.6a 연동): 재발(`regressed`)한 finding은 추가 감점 + *재발 횟수만큼 누적*(예: 2회 -3, 3회 -5). → "같은 실수 반복 = 등급 하락" 행동 교정 동기. `fixed`로 전환 시 회복 보너스.
- **레벨**: 누적 점수/해결 이력으로 레벨 산정 → 레벨별 교육 깊이 조절(낮으면 기초, 높으면 요점·심화).
- **레벨별 자주 범하는 실수**: 이력(history.json)에서 *이 사용자가 반복하는 부류*를 집계 → "너는 인가(RLS) 계열을 자주 놓침" 같은 개인화 피드백.
- **퀴즈**: 탐지된 취약 부류에 대해 "이 중 어느 게 취약?"·"고쳐봐" 식 간단 퀴즈 → 학습 정착 확인(재발 감지와 짝).
- **저장**: 로컬 `.secoach/history.json`(재발 이력)·`state.json`(레벨/점수). **DB·대시보드 없음.**
- → 점수/레벨/퀴즈는 교육 레이어(§5)의 게임화. MVP에선 P2(탐지·경로·재발 코어 먼저), 이후 추가.

---

## 8. 퀄리티 계획 (수상작 craft 기준)

- **테스트 ≥ 소스 LOC 목표** (Mocka 119%, atio 120%처럼). 코어가 작아 가능.
  - 취약 샘플 fixture 넣으면 그 경로/Finding 나오는지 검증 (결정적이라 쉬움).
- **⭐ 탐지 벤치마크** = 라벨된 바이브스택 코퍼스(취약 변형 + 안전 변형 + §4.1의 *미묘한* 케이스: RLS-on-but-permissive·뷰우회·함수우회) → **precision/recall/F1 측정.**
  - 선례: OWASP Benchmark(2,740 케이스)로 SAST 도구 비교(arXiv 2601.22952).
  - → ① 회귀 테스트(품질) ② **정량 주장**("우리 벤치 N개에서 precision X%·recall Y%") = Mocka식 craft + 대회 차별점. **벤치가 곧 테스트.**
- **GitHub Actions CI** (pytest + lint).
- **SonarCloud 품질게이트** (무료, badge). → DevSecOps 어필 + 심사 신뢰도.
- 라이선스 깨끗하게(파서·Soufflé 라이선스 확인 — 2차 라이선스 검증 게이트 통과).

---

## 9. MVP 범위 & 빌드 순서 (솔로 1달)

**MVP = "탐지 엔진(파일감지→파싱→룰→출력) + 개별 smell 룰 5~6개 + 의미기반 RLS + toxic combination 경로 1개 + 레슨 3개".**
(엔진이 먼저, 경로는 그 위 레이어. ROI 순서 = 부록 A §6: 의미 RLS → 차단 모델링 → 경로 → 벤치)

1. **엔진 뼈대**(§3.1): 파일 감지 + Fact/Rule/Finding 자료구조(§3.2~3.3) — *의미 담는 attrs*
2. **파서 2개**: PyYAML(compose) + sqlparse(sql) → Fact 정규화 (**정책식까지 파싱** §3.5)
3. **단일-Fact 룰 5~6개**(§3.3): `DB_EXPOSED`·`ANON_KEY_FRONTEND`·`CONTAINER_ROOT`·`CORS_WILDCARD` 등 → **인프라 전반 탐지 작동**(여기까지가 1차 동작)
4. **의미기반 RLS 룰**(§3.5): `RLS_MISSING`·`RLS_PERMISSIVE`(USING(true)) ← 정밀도 핵심·CVE 명분
5. **toxic combination 분석**(§3.6): 손코딩 BFS, 차단(negation) 포함, 엣지 우선 3개(포트노출/RLS/anon키) → 경로 1개 + 확신도 계층 ← **차별적 상위 레이어**
6. **출력**(§3.6D): 개별 Finding + toxic combination 둘 다, severity 게이팅 + CLI(`secoach scan`)
7. **경로→레슨** + 4단 레슨 3개(§5.2) + **벤치마크 코퍼스**(취약/안전/미묘) + 테스트 + CI + Sonar
8. **⭐ 재발 동적 감지**(§3.6a): `.secoach/history.json` 이력 비교 → detected/fixed/regressed 분류 + 재발 경고 (룰+대상 키)
9. **Trivy/Checkov 번들 통합**(§3.4a): 자동 다운로드 + subprocess 호출 + SARIF 정규화 + 중복제거 → 자체 룰과 통합 (커버리지 확장)
10. (확장) 의미 RLS 룰 확장(뷰·함수·grant §4.1) + 파서 확장(Dockerfile·next·vercel·env) + 레슨 30개 + 레벨/퀴즈(§7)
11. (옵션) Datalog(Soufflé) 이관 / 코드IaC AST / `--deep` neuro-symbolic / 자동실행(pre-commit·GitHub Action·SARIF §6.1)

→ **3번까지만 해도 "인프라 보안 전반 탐지"가 작동.** 4~5번이 전문성(의미)+차별점(경로), 8번이 재발 추적(시간축), 9번이 커버리지 확장(번들). 즉 *엔진→전반탐지→정밀→경로→재발→커버리지* 순으로 쌓여서, 어디서 멈춰도 작동하는 도구. **자체 룰이 항상 코어(네트워크/번들 없어도 작동)**, Trivy/Checkov는 커버리지를 넓히는 통합 레이어.

---

## 10. 향후 계획 (보고서에 명시 = 확장성 점수)

- **Datalog(Soufflé) 엔진 이관**: 손코딩 BFS → 형식 도달성 엔진(explain=설명). 선례 Semia(arXiv 2605.00314).
- **Neuro-symbolic 재현율**: LLM 사실표면화(`--deep`) — 커스텀 설정 포착.
- **동적 검증**: `--verify-live` — 정적이 찾은 경로를 실제 요청으로 확인(정확도 보강).
- **RAG 고도화**: `--explain` 캐시·다중 LLM·설명 품질.
- **코드형 IaC**: Pulumi/CDK AST 룰 — *AI 생성 인프라(Pulumi Neo)* 보안.
- **VSCode 확장**: 코어를 라이브러리로 분리해둠 → 실시간 경로 경고+교육 팝업.
- **⭐ 에이전트 권한 도달성**(§1.5): 같은 도달성 엔진을 "인터넷→DB"에서 **"AI 에이전트→접근 가능 자원"**으로 확장 — 에이전트 폭증 시대의 "무엇에 접근하나" 보안 질문을 *동일 엔진*으로 푼다. (미래 정합 + 강력한 확장성 서사)
- **커뮤니티 룰/레슨 확장**(§6.2): 룰 플러그인·레슨 YAML·벤치 케이스를 커뮤니티 PR로 → 솔로의 한계를 협업으로 넘김.
- **Terraform**: (레드오션) 노출경로만 차별화로.

---

## 11. 대회 전략

- **부문/과제:** 학생부문, 자유과제, 세부과제 = **보안/인증.**
- **현실 목표:** 학생부문 입상 + **스패로우(보안 후원사) 후원기업상.** (SAGE·Taint-Bomb이 보안/인증으로 수상 → 카테고리 열림.) 대상은 비현실(괴물급 경쟁).
- **일정 (확정):**
  - **접수 6/15~7/17 18:00** (oss.kr) ← 마감 엄수
  - 출품작 제출 7/18~**8/27 18:00** (결과보고서 + 소스코드 + **시연영상 3분 이내**)
  - 오리엔테이션 7/23 (**실제 평가기준 공개** — 받고 우선순위 재조정) / 온라인 교육 7/23~
  - 1차 서면 9/3~4 (보고서·코드·영상)
  - 멘토링 9/18~10/9 (1차 합격팀, 솔로한테 큰 도움)
  - **2차 기능테스트 + 라이선스검증 10/12~10/28** (결정적 코어로 대비)
  - 2차 발표 11/4~5 / 수상발표 11/11 / 시상 12/4
- **두 게이트 대비:** ① 기능테스트=결정적 모드 작동 보장(§5.1a) — 자체 룰·번들 Trivy/Checkov 모두 *결정적*이라 재현 OK ② 라이선스=빌려쓴 파서(PyYAML MIT·sqlparse BSD·dockerfile-parse)+**번들 Trivy/Checkov(Apache 2.0, 다운로드+호출이라 안전, NOTICE 고지)**+Semgrep(LGPL, 호출만) 충돌 *지금부터* 점검(§3.4a).
- **서사:** "AI 코딩 대중화 → 인프라 보안 모르는 사람 폭증 → 공격경로를 추적하고 원리를 가르쳐 보안 민주화. **룰·레슨을 커뮤니티가 함께 쌓는 오픈소스 생태계로**(§6.2)."

---

## 12. 정직한 리스크 (숨기지 말 것)

| 리스크 | 대응 |
|---|---|
| "포트 published=인터넷 도달"은 단순화(방화벽 등 변수) | 교육도구지 형식검증기 아님 — *가정을 문서화* |
| 설정 변형 많아 파싱 지저분 | 대상 스택 좁혀서 감당, 못 파싱하면 skip |
| 경로가 항상 깔끔히 안 나옴 | 못 찾으면 "점" 검사(개별 Finding)로 폴백 |
| 학습자가 교육형 도구를 실제 쓸지 미검증 | VibeSec은 교육을 뺐음 — 가설. 대회용 데모로 먼저 증명 |
| "바이브 보안" 도구 포화(VibeSec·vibesec.sh 등) | **코드 SAST 절대 안 함** — 인프라 크로스포맷 공격경로로 차별화(§2·§3.0) |
| "바이브코딩" 라벨이 1년 뒤 노후화(Karpathy "passe") | 포지션을 **"AI 생성 인프라 검증 게이트"**로 격상(§1.5) — 청중은 남고 라벨만 교체 |
| 1달 솔로 완성 압박 | MVP(compose+sql 경로 1개)부터, 나머지 점진 |

→ **핵심: 공격경로 코어 = 검증된 정통기법(APA) + 결정적(테스트 가능) + 크로스포맷(아무도 안 함) + 교육. 코드 SAST는 레드오션이라 절대 안 가고, 인프라 크로스포맷 경로 하나로 비수상작의 "LLM 래퍼" 함정과 "바이브 보안 떼거리"를 동시에 벗는다.**


---

# 부록 A. 탐지 엔진 고도화 — 정밀도·재현율 극대화 상세

> 본문 §3.5·§3.6·§4.1·§8의 *상세 근거*. 본문이 요약, 이 부록이 전체.
> (원래 별도 문서 `secoach_탐지엔진_고도화.md`였던 내용을 통합)

## 0. 왜 지금 구조론 성능이 부족한가

- 현재 설계 = 손코딩 BFS + "RLS 있나?" 같은 **문법 검사**.
- 문제: ① 차단요소(방화벽·내부망)를 못 모델링 → **오탐** ② "RLS 켜졌지만 정책이 `USING(true)`" 같은 의미를 못 봄 → **미탐**.
- → 두 축으로 해결: **엔진(Datalog)** + **룰 의미화**.

---

## 1. 엔진 — Datalog(Soufflé)로 도달성 "증명"

### 1.1 왜 Datalog인가
- CodeQL도 Datalog 파생(QL)로 "공격자 입력이 sink에 도달하나"를 *모델링*함 (패턴매칭이 아니라).
- 도달성 = **재귀 규칙 한 줄**: `reachable(x,z) :- edge(x,y), reachable(y,z).` → 전이폐쇄 자동, semi-naïve로 빠름.
- **부정(negation) 지원이 핵심** — 차단요소를 모델링해 오탐을 죽임:
  ```prolog
  // 인터넷이 DB에 도달 = 노출 엣지가 있고, 차단(gate)이 없을 때만
  reachable_internet(db) :- exposed_to_host(db), !blocked(db).
  blocked(svc) :- on_internal_network(svc).      // internal:true 네트워크
  blocked(svc) :- behind_auth_proxy(svc).        // 인증 프록시 뒤
  ```
- Soufflé `explain` = **유도 트리(derivation tree)** 출력 → "왜 이 경로가 성립하나"의 단계별 증명 = **그대로 공격경로 + 레슨.** (설명을 공짜로 얻음)

### 1.2 ⭐ 선례 — Semia (arXiv 2605.00314, 2026)
secoach랑 **구조가 거의 동일한** 논문이 이미 있음 (보고서 인용 강력):
- 아티팩트를 **Datalog fact base로 lift** → 보안 속성을 **Datalog 도달성 질의**로 환원.
- LLM이 *사실을 표면화*하고 **정밀 추론은 형식 엔진(Soufflé)에 위임** (neuro-symbolic).
- 규모: **Python 4,500줄 + Soufflé Datalog 900줄.** temperature=0으로 재현성.
- → "솔로가 못 할 규모"가 아님 + "이 접근이 SOTA 대비 precision/recall/F1 우수"를 학술적으로 입증한 근거.
- 관련: IRIS(LLM이 분석 스펙 생성→CodeQL 평가, recall↑), LLMDFA(dataflow를 LLM 하위작업으로 분해+도구 검증).

### 1.3 구현 선택
- **메인: Soufflé** (C++ 컴파일, 빠름, explain/profiler). Datalog 룰은 사람이 읽기 쉬움.
- 대안(가벼우면): Python `ascent`류 or 구조화된 재귀 fact 유도. 단 Soufflé가 "증명 기반"이라 대회 어필 큼.
- secoach가 직접 만드는 것 = **Fact 스키마 + 도달성/차단 규칙 + 경로→레슨.** (= 단단한 코어)

---

## 2. 정밀도 레버 (오탐 제거)

| 레버 | 방법 | 효과 |
|---|---|---|
| **차단요소 모델링** | internal망·인증프록시·포트 expose-only를 `blocked` fact로 (negation) | #1 오탐원(포트 떴지만 실제 차단) 제거 |
| **Reachable vs Exploitable** | 점(나쁜설정) < 도달가능(경로존재) < 악용가능(경로+무차단+익명source) | 확신도 계층화 |
| **필드 민감도** | *어느* 테이블/역할/조건인지 추적 (users vs 공개카탈로그, anon vs authenticated) | 같은 룰도 대상따라 심각도 차등 |
| **음성결과 활용** | 경로 없으면 "안전(도달경로 없음)" 명시, 노이즈 X | 신뢰↑ (CodeQL "negative result is valuable") |

→ Reachable/Exploitable 구분이 핵심: "RLS 없음"(점)은 LOW, "RLS 없음 + 인터넷도달 + anon키노출"(악용가능)은 CRITICAL. **둘을 같은 경고로 내면 오탐처럼 느껴짐.**

---

## 3. 재현율 레버 (미탐 제거) — Neuro-Symbolic

- 문제: 설정 표현이 수십 변형 + 커스텀 프록시/스크립트는 rigid 파서가 놓침.
- 해법(IRIS/LLMDFA/Semia 패턴): **LLM이 후보 사실을 표면화 → Datalog가 정밀 판정.**
  - 예: "이 커스텀 Express 미들웨어가 DB로 포워딩하나?" / "이 env 변수가 DB 자격증명인가?" → LLM이 *후보 fact* 제안 → Datalog가 도달성 *결정.*
  - → **재현율↑ (rigid 파서가 놓친 것 포착)** 하면서 **결정적 코어 유지** (LLM은 사실 제안만, 판정은 Datalog). temp=0.
- 보조: **Trivy를 fact source로** (점 커버리지 수백 개 공짜), 같은 사실이 여러 파일(마이그레이션·다중 SQL)에 흩어진 것 다 스캔.
- ⚠️ LLM 레이어는 **옵션**(`--deep`) — 코어는 LLM 없이 작동(2차 재현 보장).

---

## 4. ⭐ 의미기반 도메인 룰 — Supabase RLS 정밀 탐지 (성능이 진짜 갈리는 곳)

**"RLS 켜졌나?"만 보면 정밀도·재현율 *둘 다* 망함.** 실제 룰은 의미를 파싱해야 함.

### 4.1 미탐(FN) — grep으로는 못 잡는 진짜 취약
| 패턴 | 왜 위험 | 탐지법 |
|---|---|---|
| **RLS 켜졌는데 `USING(true)`** | RLS 없는 것과 동일 — **AI 생성기 #1 실수** | 정책 *식*을 파싱, `true`/무조건 허용 탐지 |
| **SQL editor 생성 테이블** | 대시보드와 달리 **RLS 기본 OFF** | 생성경로 모르니 명시적 확인 필요 |
| **GRANT + RLS off** | 신규 테이블은 anon에 auto-grant → 노출 | `GRANT ... TO anon` + RLS상태 결합 |
| **뷰(View)** | **기본 security definer라 RLS 우회** (PG15+ `security_invoker=true` 필요) | 뷰가 보호 테이블을 노출하는지 |
| **SECURITY DEFINER 함수/RPC** | anon이 호출 시 RLS 우회 | `auth.uid() IS NOT NULL` 가드 유무 |
| **Storage 버킷 public** | 같은 RLS 엔진 — 누구나 전체 읽기 | 버킷 public 여부 |

### 4.2 오탐/심각도 뉘앙스(정밀도)
| 패턴 | 처리 |
|---|---|
| 진짜 공개 데이터(국가목록·공개카탈로그) RLS off | 의도됨 → LOW (필드 민감도로 테이블 의미 구분) |
| 정책이 `auth.uid()` 쓰는데 `TO authenticated` 없음 | anon에도 실행(null 반환) — 미묘. "authenticated 역할 명시" 룰 |
| 정책이 `user_metadata`(사용자 수정가능 JWT claim) 의존 | 권한상승 — 정책 술어 검사 |
| RLS 정책에 `service_role` 명시 | "아무것도 안 함" — 혼동 신호지 취약 자체는 아님 |

### 4.3 실세계 근거 — CVE-2025-48757 (보고서 킬러 통계)
- 2025년 5월, Matt Palmer 공개: **분석한 Lovable 앱 1,645개 중 170개(10.3%)·엔드포인트 303개가 anon 키로 Supabase 테이블이 읽혔음.**
- "AI 빌더 + Supabase(Lovable·Cursor·Bolt·Replit)면 검증 전까진 RLS 미설정이라 가정하라."
- → **secoach 타깃이 "실재하고 거대한 문제"라는 정량 증거.** 보고서 서두에 인용 = 명분 확정.
- 업계 분류: Supabase 앱 top 취약 = ① RLS 미설정 테이블(가장 빈번·critical) ② service_role 키 노출 ③ 허용적 RLS 정책. **secoach는 이 셋을 *경로*로 묶음.**

→ **결론: 탐지 룰은 문법(grep ENABLE)이 아니라 의미(정책식·역할·뷰·함수·grant 파싱)여야 함.** 순진한 스캐너는 ~절반만 잡고, 의미 엔진이 미묘한 것까지 잡아 — **이게 성능 차별점.**

---

## 5. 측정 — 벤치마크 (메타 레버 + 대회 신뢰도)

- 선례: OWASP Benchmark v1.2(2,740 케이스)로 CodeQL/Semgrep/SonarQube/Joern를 precision/recall 비교한 연구("Sifting the Noise", arXiv 2601.22952).
- **secoach도 라벨된 벤치마크 구축:** 바이브스택 설정 코퍼스 (취약 변형 + 안전 변형 + §4.1의 *미묘한* 케이스: RLS-on-but-permissive·뷰우회·함수우회).
- → **precision/recall/F1 측정** = ① 회귀 테스트(품질) ② 대회 차별점("우리 벤치 N개에서 precision X%·recall Y%" = 정량 주장 = Mocka식 craft).
- 이게 §8 테스트 규율(테스트≥소스)이랑 합쳐짐 — 벤치가 곧 테스트.

---

## 6. 종합 아키텍처 (성능 최적화판)

```
[설정 파일들]                                  [Trivy config] (점 fact 보강)
  compose·sql·env·next·vercel                       │
        │ 파서(PyYAML·sqlparse·...) + (옵션)LLM 사실표면화      │
        ▼                                            ▼
   ┌─────────────────────────────────────────────────────┐
   │  Datalog Fact Base  (bind/expose/rls_policy/grant/   │
   │   secret/view/func/gate/edge ...)  — 의미 파싱됨        │
   └─────────────────────────────────────────────────────┘
        │  재귀 도달성 규칙 + 차단(negation)
        ▼
   reachable_exploitable(internet, users_table)   ← 증명
        │  Soufflé explain = 유도 트리
        ▼
   확신도 계층(점<도달<악용) + 경로 + 4단 레슨
```

**우선순위(성능 ROI 순):**
1. **의미기반 RLS 룰**(§4) — 제일 큰 정밀도·재현율 향상, 솔로 당장 가능, CVE로 명분.
2. **차단 모델링 + Reachable/Exploitable**(§2) — 오탐 급감.
3. **Datalog 엔진**(§1) — 엄밀+설명+대회어필. (시간 빠듯하면 손코딩 BFS로 시작 후 이관)
4. **벤치마크**(§5) — 정량 주장 + 회귀 테스트.
5. **Neuro-symbolic 재현율**(§3) — 옵션, 후순위.

---

## 7. 정직한 한계 (여전히)
- Datalog·의미룰로 *크게* 줄여도, 정적분석인 한 외부 방화벽·런타임 사실은 못 봄(AWS 형식검증기조차 동일). → 확신도 표기 + `--verify-live`(동적 옵션)로 보강.
- 의미 파싱은 SQL/설정 방언이 많아 커버리지 부분적 → 벤치마크로 *측정된 범위*만 주장(과장 금지).
- LLM 사실표면화는 비결정적 → 코어는 LLM 없이 작동 보장(옵션 분리).

→ **핵심: 성능은 "엔진(Datalog 도달성+차단) × 룰 의미화(정책식·역할·뷰·함수) × 측정(벤치 F1)"의 곱이다. 특히 Supabase RLS 의미 탐지가 ROI 최고 — CVE-2025-48757이 명분, Semia가 아키텍처 선례.**
