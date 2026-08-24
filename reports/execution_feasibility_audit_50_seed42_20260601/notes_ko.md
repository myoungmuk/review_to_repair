# 실행 기반 평가 가능성 점검 요약

- 범위: CodeReview-New `crn_all`에서 seed 42로 50건 샘플
- 목적: 실행 기반 평가를 실제로 재구성할 수 있는지 사전 점검
- 수행한 확인: 원본 메타데이터 연결, GitHub review comment 접근, 리뷰 대상 파일 경로 확인, 후보 커밋의 raw 파일에서 `old/new` 스니펫 매칭 여부 확인
- 수행하지 않은 작업: repository clone, 의존성 설치, 실제 테스트 실행

## 주요 결과

| 항목 | 건수 | 비율 |
| --- | ---: | ---: |
| repo/review/commit 메타데이터 존재 | 50/50 | 100.0% |
| GitHub review comment에서 파일 경로 확인 | 43/50 | 86.0% |
| `old` 필드 원문이 파일에 직접 매칭 | 0/50 | 0.0% |
| diff 마커 제거 후 before-code가 파일에 유일 매칭 | 4/50 | 8.0% |
| diff 마커 제거 후 gold after-code가 파일에 매칭 | 4/50 | 8.0% |
| 예측 스니펫을 자동 치환할 수 있는 최소 조건 충족 | 4/50 | 8.0% |

## 해석

현재 CodeReview-New 레코드만으로 전체 실행 기반 평가를 바로 수행하기는 어렵다. 특히 `old/new`가 순수 파일 코드라기보다 diff hunk 형태를 포함하는 경우가 많아, 실제 파일에 적용하려면 diff 마커 제거 및 hunk 재구성이 필요하다. 50건 샘플에서는 diff 마커를 제거해도 before-code가 대상 파일에 유일하게 매칭되는 경우가 4건뿐이었다.

따라서 실행 기반 평가는 이 데이터셋의 기본 평가로 즉시 추가하기보다, 별도의 execution-feasible subset을 먼저 구축해야 한다. 해당 subset 구축에는 repository checkout, 의존성 설치, 테스트 명령 식별, gold patch 적용 sanity check가 추가로 필요하다.

## 주의

이번 점검 중 GitHub 무인증 API 한도 60회가 소진되어 일부 review comment 요청은 403으로 종료됐다. 따라서 파일 경로 확인 43/50은 보수적인 하한으로 보는 것이 적절하다. 다만 핵심 병목은 API 접근보다 스니펫을 실제 파일에 안정적으로 매칭하고 치환하는 단계로 확인된다.

