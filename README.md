<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
  <img alt="Park Dongkyu — backend engineer. reproduce → trace root cause → measure → fix → write ADR" src="assets/header-light.svg" width="100%">
</picture>

<p align="center">
  <a href="mailto:qkrehdrb0813@gmail.com">Email</a> &nbsp;·&nbsp;
  <a href="https://www.linkedin.com/in/dongkyu-park">LinkedIn</a> &nbsp;·&nbsp;
  <a href="https://github.com/dong99u/tradingpt-docs">Tech Docs</a> &nbsp;·&nbsp;
  <a href="https://solved.ac/eastking7979/">solved.ac</a>
</p>

<br>

장애의 **근본 원인**을 끝까지 추적하고, 기술 선택의 **이유**를 설명할 수 있는 백엔드 개발자입니다.
실서비스에서 측정하고, 고치고, 결정을 문서로 남깁니다.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/impact-dark.svg">
  <img alt="SQL 101→4 (−96%) · p95 40.7s→0.8s (−97%) · 결제 성공률 0%→100% · 실사용자 642명+" src="assets/impact-light.svg" width="100%">
</picture>

## `01` Featured — TradingPT

**Spring Boot 기반 트레이딩 교육 플랫폼 백엔드** &nbsp;`2025.08 – 운영 중`&nbsp; BE 2 · FE 1

20개 도메인을 DDD + CQRS로 설계하고 NicePay 빌링키 정기결제, 카카오·네이버 OAuth2, AWS Multi-AZ 인프라를 구축했습니다.
2025.12 오픈 후 가입자 642명+, 피드백 요청 5,300건+를 처리하고 있습니다. → [기술 문서](https://github.com/dong99u/tradingpt-docs)

<details>
<summary><b>N+1 쿼리 · 커넥션 풀 고갈</b> &nbsp;—&nbsp; 쿼리 101 → 4</summary>
<br>

| | |
|---|---|
| **문제** | 관리자 대시보드 API 1건에 SQL 101개, HikariCP(max 10) 고갈로 3일간 서비스 불가 |
| **원인** | 1-side(Customer) 기준 조회 → 연관관계가 전부 ToMany라 Fetch Join 불가, 루프 안에서 Repository 5개 호출 |
| **해결** | N-side(Subscription)에서 출발해 모든 관계를 ToOne으로 전환 · Fetch Join + IN절 배치 쿼리 + 메모리 조립 · 스케줄러 5분 간격 분산 |
| **결과** | 쿼리 96%↓ · 응답 20s → 2s · 커넥션 풀 사용률 100% → 50% |

</details>

<details>
<summary><b>REQUIRES_NEW × REPEATABLE_READ 격리 충돌</b> &nbsp;—&nbsp; 결제 성공률 0% → 100%</summary>
<br>

| | |
|---|---|
| **문제** | 빌링키 등록은 성공하는데 유료 구독 생성만 100% 실패 (0원 프로모션은 성공) |
| **원인** | 자식 TX(REQUIRES_NEW)가 커밋한 PaymentMethod를 부모 TX의 REPEATABLE_READ 스냅샷이 보지 못함 (MVCC 가시성) |
| **해결** | ID로 재조회하지 않고 엔티티 객체를 직접 전달해 재조회 자체를 제거 |
| **결과** | 결제 성공률 0% → 100% · DB 쿼리 25%↓ |

</details>

<details>
<summary><b>k6 1,000 VU 부하 테스트 · 3-Layer 병목 분석</b> &nbsp;—&nbsp; p95 40.7s → 800ms</summary>
<br>

| | |
|---|---|
| **문제** | p95 40.7초, CPU 96%, t3.medium CPU 크레딧 즉시 소진 |
| **원인** | ① BCrypt CPU-bound (60–70%) ② HikariCP 풀 부족 (20–25%) ③ RDS IOPS 제한 (10–15%) |
| **해결** | EC2 t3.medium → c6i.xlarge · RDS db.t3.micro → db.r6g.large · 풀 크기 (cores×2)+1 재산정 |
| **결과** | p95 97%↓ · TPS 41.7 → 150–200 · CPU 40–60% |

</details>

<details>
<summary><b>SPA ↔ API CSRF 토큰 불일치</b> &nbsp;—&nbsp; 403 에러율 100% → 0%</summary>
<br>

| | |
|---|---|
| **문제** | SPA(localhost:3000) → API(dev.tradingpt.kr) 모든 변경 요청이 403 |
| **원인** | Spring Security 6 기본 `CookieCsrfTokenRepository`는 쿠키로만 전달, SPA는 응답 헤더에서 토큰을 읽어야 함 |
| **해결** | Decorator 패턴의 `HeaderAndCookieCsrfTokenRepository`로 쿠키 + 헤더 동시 전달 |
| **결과** | CSRF 에러 0% · 기존 코드 변경 0줄 |

</details>

<details>
<summary><b>아키텍처 의사결정 7가지</b> &nbsp;—&nbsp; 무엇을, 왜 골랐나</summary>
<br>

| 영역 | 선택 | 근거 |
|---|---|---|
| 인프라 | Multi-AZ | 99.95% SLA, Public/Private Subnet 분리로 장애 격리 |
| 배포 | Blue/Green | 무중단, 롤백 5분, 배포 시간 67%↓ (GitHub Actions + CodeDeploy) |
| 컨테이너 | EC2 + ASG | YAGNI — EKS 대비 연 $1,236 절감, Docker로 ECS 이전 경로 확보 |
| 인증 | Redis Session | JWT 무효화에도 결국 Redis가 필요해 Stateless 이점 상실 → 세션 + 동시접속 제어 |
| 스케줄링 | ShedLock | 테이블 1개 (Spring Batch 6개, Quartz 11개 대비) |
| 모니터링 | CloudWatch | EC2 · ALB · RDS · ElastiCache 메트릭 통합 |
| DDD | Shared Kernel | 독립 Aggregate를 `customer_id` + 기간 복합 키로 논리 연결 |

</details>

## `02` Projects

| | 프로젝트 | 한 줄 요약 | Stack |
|---|---|---|---|
| ◆ | [**Momento**](https://github.com/dong99u/momento) | 가족 대화 플랫폼 · 응답 60s → 9ms | Spring Boot · Kotlin · Redis · GPT-4 |
| ◆ | [**Love Keeper**](https://github.com/dong99u/love_keeper_BE) | 커플 소통 플랫폼 · ECS Fargate MSA | Spring Boot · AWS ECS |
| ◆ | [**Indayvidual**](https://github.com/Indayvidual/Indayvidual-Server) | 커스터마이징 일정 관리 앱 | Spring Boot |
| ◆ | [**Mody**](https://github.com/dong99u/mody-server) | 맞춤형 스타일 추천 | Spring Boot |
| ◇ | [**nugget**](https://github.com/dong99u/Nugget-FE) | 시각장애인 보행 보조 · GSC Global Top 100 | Flutter · TF Lite |
| ◇ | [**chalim**](https://github.com/dong99u/chalim-frontend) | 외국인을 위한 메뉴판 번역 | Flutter |

<sub>◆ 백엔드 &nbsp; ◇ 앱 · ML</sub>

## `03` Stack

<p>
  <img src="https://skillicons.dev/icons?i=java,spring,kotlin,hibernate,mysql,redis&perline=6" alt="Java, Spring, Kotlin, Hibernate, MySQL, Redis" height="40"><br>
  <img src="https://skillicons.dev/icons?i=aws,docker,githubactions,linux,python,flutter&perline=6" alt="AWS, Docker, GitHub Actions, Linux, Python, Flutter" height="40">
</p>

`Spring Security 6` `QueryDSL` `JUnit 5` `k6` `ShedLock` `OAuth2` `DDD` `CQRS`

## `04` Track record

| | |
|---|---|
| **수상** | Google Solution Challenge 2024 Global Top 100 · GBT 학부 해커톤 대상 · 공과대학 코드 페스티벌 알고리즘 1위 |
| **교육** | SSAFY 15기 데이터 트랙 (2026.01 –) · 한국외국어대학교 컴퓨터전자시스템공학부 졸업 |
| **활동** | UMC 4–8기 (8기 Spring Boot 파트장) · GDSC 5기 |
| **자격** | SQLD · TOEIC Speaking Advanced Low |

<br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dong99u/dong99u/output/github-contribution-grid-snake-dark.svg">
  <img alt="contribution snake" src="https://raw.githubusercontent.com/dong99u/dong99u/output/github-contribution-grid-snake.svg" width="100%">
</picture>

<p align="center"><sub>Open to backend engineering opportunities — <a href="mailto:qkrehdrb0813@gmail.com">qkrehdrb0813@gmail.com</a></sub></p>
