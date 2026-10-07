# Doti Public Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for direct implementation or superpowers:subagent-driven-development if the user selects delegated execution. Steps use checkbox syntax for tracking.

**Goal:** 회사 공용 앱 안내와 도티두잇 소개 및 AdMob 인증 파일을 GitHub Pages에 공개하고 재현 가능한 운영 절차를 남긴다.

**Architecture:** HTML·CSS 정적 사이트를 `site/`에 격리한다. Python 표준 라이브러리로 파일 계약을 검사하고, GitHub Actions에서 검증된 `site/`만 Pages에 배포한다. 앱 코드와 기존 법적 고지 사이트에는 의존성이나 변경을 추가하지 않는다.

**Tech Stack:** HTML5, CSS, Python 3 표준 라이브러리, GitHub Actions, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-10-07-doti-public-site-design.md`

## Global Constraints

- 원격은 `git@github.com:opensky-doti/opensky-doti.github.io.git`, 공개 호스트는 `https://opensky-doti.github.io`다.
- 회사 표기는 `오픈스카이`, 문의는 `eonseok.yoon@opensky.co.kr`이다.
- Play 링크는 `https://play.google.com/store/apps/details?id=com.doti.doit`다.
- 법적 고지는 `https://kizwond.github.io/dotimoti-legal/dotidoit/privacy/`에 연결하며 개정하지 않는다.
- `app-ads.txt`는 `google.com, pub-3081928577042149, DIRECT, f08c47fec0942fa0`와 LF 한 개로 구성한다.
- 기존 앱·공유 모듈·백엔드·법적 고지 저장소와 APK·AAB·서명키·광고 설정을 변경하지 않는다.
- 프레임워크·외부 폰트·추적 SDK·로그인·결제·폼을 추가하지 않는다.
- 공개 배포는 `main`에만 허용하며 PR이나 다른 브랜치는 검증만 한다.

## Review Focus

- 하위 페이지에서 상대 경로가 깨지는 경우: 모든 로컬 링크와 리소스를 페이지 위치 기준으로 검사한다. Task 1.
- 잘못된 게시자 ID 또는 HTML로 대체된 인증 파일: 정확한 파일 바이트 검사를 실패시킨다. Task 1.
- 좁은 화면과 큰 글자: 320px 화면·200% 확대에서 버튼과 이메일이 잘리지 않는다. Task 2.
- PR·비 main 실행에서 배포 권한이 노출되는 경우: 배포 작업의 조건과 권한을 검사한다. Task 3.
- 코드 푸시는 성공했으나 Pages 설정이나 실제 공개가 실패한 경우: HTTPS 검증 결과를 분리해 보고한다. Task 4.

## 파일 구성

| 파일 | 책임 |
| --- | --- |
| `site/index.html` | 회사 앱 안내와 도티두잇 상세 링크 |
| `site/dotidoit/index.html` | 기능 소개·Play·문의·기존 법적 고지 링크 |
| `site/404.html` | 없는 주소 안내와 홈 복귀 |
| `site/assets/styles.css` | 공통 반응형·접근성 스타일 |
| `site/assets/dotidoit-icon.png` | 확정된 앱 아이콘 복사본 |
| `site/app-ads.txt` | 공개 판매자 정보 |
| `scripts/validate_site.py` | 파일·링크·공개 정보 계약 검사 및 CLI |
| `tests/test_validate_site.py` | 검증기 정상·오류 입력 회귀 테스트 |
| `tests/test_workflow.py` | 배포 조건·권한·산출물 범위 정적 검사 |
| `.github/workflows/pages.yml` | PR 검증과 main Pages 배포 |
| `.gitignore` | Python 캐시와 로컬 QA 산출물 제외 |
| `README.md` | 로컬 확인·배포·복구·후속 앱 추가 방법 |
| `docs/handoffs/2026-10-07-public-site.md` | 실제 커밋·배포 결과와 콘솔 후속 단계 |

## Task 1 인증 파일과 페이지 계약 검사

**Interfaces:** `validate_site(root: pathlib.Path) -> list[str]`는 오류 메시지 목록을 반환한다. `python3 scripts/validate_site.py site`는 오류가 있으면 종료 코드 1, 정상이면 0을 반환한다. HTML은 표준 라이브러리 `HTMLParser`로 읽는다.

- [ ] `tests/test_validate_site.py`에서 임시 디렉터리에 최소 정상 사이트를 만드는 fixture와 다음 검사를 작성한다: `test_valid_fixture`는 빈 오류 목록, `test_wrong_publisher`, `test_missing_final_newline`, `test_html_in_ads_file`, `test_missing_required_page`, `test_broken_nested_link`, `test_link_outside_site`는 오류 목록을 반환해야 한다. 상수와 외부 링크는 Global Constraints의 정확한 값을 사용한다.
- [ ] `python3 -m unittest discover -s tests -v`로 미구현 모듈 때문에 실패함을 확인한다.
- [ ] `scripts/validate_site.py`를 구현한다. 필수 페이지·인증 파일·한국어 문서·제목·단일 h1·설명·viewport·필수 외부 링크를 검사한다. 로컬 href/src는 URL 인코딩과 fragment를 분리하고 현재 문서 기준으로 해석해 존재 여부와 site 내부 경계를 확인한다. 이메일·외부 HTTPS 링크는 로컬 파일로 검사하지 않는다. 자동 테스트에서 인터넷에 접속하지 않는다.
- [ ] 정상 fixture가 통과하고 각 잘못된 fixture가 검출되는지 전체 테스트로 확인한다. 실제 `site/`에 대한 CLI는 아직 파일이 없어 실패해야 한다.
- [ ] 검증기·테스트·캐시 제외 설정만 커밋한다.

## Task 2 안내 사이트와 광고 인증 파일

**Interfaces:** Task 1의 `validate_site(Path('site'))` 계약을 만족하는 정적 파일을 제공한다. 모든 페이지는 `/assets/styles.css`를 사용하고 서버 API나 JavaScript를 요구하지 않는다.

- [ ] `test_site_on_disk`를 추가해 실제 `site/`가 오류 목록 없이 통과해야 한다고 단언하고, 페이지가 없어 실패함을 확인한다.
- [ ] 세 HTML 페이지와 CSS, 정확한 `app-ads.txt`를 작성한다. 도티두잇 소개는 미션·수행툴·기록으로 제한한다. 다운로드는 Play에만 연결한다. 홈과 상세에 문의 및 개인정보처리방침 링크를 제공하고 404에는 `/` 복귀 링크를 둔다.
- [ ] `/Users/opensky/doti/doti_doit/output/google-play/dotidoit-store-icon-512.png`를 이미지 뷰어로 확인한 후 새 사이트에 복사한다. 원본과 복사본 해시를 대조하고 원본은 수정하지 않는다. 이미지에는 크기와 적절한 대체 텍스트를 설정한다.
- [ ] `python3 -m unittest discover -s tests -v` 및 `python3 scripts/validate_site.py site`가 모두 통과하는지 확인한다.
- [ ] `python3 -m http.server 8765 --bind 127.0.0.1 --directory site`로 로컬 제공하고, 브라우저 스킬을 사용해 320px·390px·1280px 화면, 200% 확대, Tab 이동과 초점, 링크 동작을 확인한다. `scrollWidth <= clientWidth`를 확인하고 스크린샷을 로컬 QA 폴더에 남긴다. 404 페이지는 직접 열어 확인하며 실제 없는 URL의 사용자 정의 404는 배포 후 확인한다.
- [ ] UI에서 발견된 문제를 수정하고 검증기 및 관련 브라우저 검사를 재실행한 후 사이트와 테스트를 커밋한다.

## Task 3 안전한 Pages 배포와 운영 문서

**Interfaces:** 워크플로는 Task 1 검증 명령을 실행하고 `site/`만 업로드한다. `README.md`는 같은 명령을 제공한다.

- [ ] `tests/test_workflow.py`에 main push·PR·수동 실행 트리거, 검증 명령, `path: site`, `needs: validate`, `github-pages` 환경 및 배포 main 조건의 존재를 검사하는 테스트를 작성한다. `pull_request_target`을 허용하지 않고 쓰기 권한은 배포 작업에만 있음을 검사한다. YAML 블록 경계를 기준으로 검사하며 원문 일부 존재만으로 전체 의미 검증을 대신했다고 주장하지 않는다.
- [ ] 워크플로가 없어 테스트가 실패하는지 확인한다.
- [ ] `.github/workflows/pages.yml`을 작성한다. 전역 `contents: read`, 검증 작업과 배포 작업을 분리한다. 배포 작업은 `github.ref == 'refs/heads/main' && github.event_name != 'pull_request'` 조건, `needs: validate`, `pages: write`, `id-token: write`, `github-pages` 환경을 사용한다. 배포 동시 실행은 직렬화하며 실행 중인 배포를 취소하지 않는다.
- [ ] 공식 문서에서 확인한 `actions/checkout@v6`, `actions/configure-pages@v5`, `actions/upload-pages-artifact@v4`, `actions/deploy-pages@v4`를 사용한다. Python은 Ubuntu runner의 `python3`를 사용한다. 실제 실행 시 액션 지원 여부와 YAML 유효성을 다시 확인한다.
- [ ] README에 Pages 소스 `GitHub Actions` 선택, 로컬 검사·미리보기, main 반영, 배포 로그, 세 공개 URL, revert 기반 복구, 동일 호스트의 후속 앱 추가, AdMob 인증과 실광고 전환의 차이를 작성한다. 초기 배포 전에는 공개 완료로 표시하지 않는다.
- [ ] 전체 Python 테스트와 CLI, `git diff --check`를 실행한다. 지원되는 workflow 검증 도구가 있으면 추가 검사하고, 최종 YAML 의미와 최소 권한은 직접 리뷰한다. 통과 후 커밋한다.

## Task 4 원격 반영과 공개 확인

**Interfaces:** 승인된 사이트 브랜치를 검증 후 main에 반영하고 GitHub Pages의 공개 응답을 확인한다. 앱 Preview 배포와 Play 업로드는 수행하지 않는다.

- [ ] 실행 시 `using-git-worktrees`로 사이트 저장소의 격리된 작업 브랜치를 사용한다. main으로 합치기 전 원격 변경과 사용자 변경을 확인하며 강제 푸시·reset·clean을 사용하지 않는다.
- [ ] 전체 테스트·시각 검증·설계 충족 여부를 재확인하고, 선택한 실행 방식의 코드 리뷰 절차를 완료한다. 승인된 작업 커밋만 main에 반영해 원격에 푸시한다.
- [ ] 인증된 GitHub 도구에서 Pages 설정·Actions 결과를 확인한다. 설정 권한이 없다면 사용자에게 이 저장소의 `Settings → Pages → Build and deployment → Source → GitHub Actions` 설정을 안내한다. 사용자 비밀번호·토큰을 요청하거나 기존 인증 정보를 출력하지 않는다. 공개를 확인할 수 없으면 이 단계는 미완료로 남긴다.
- [ ] Pages 작업 성공 후 `curl --fail --show-error --silent --location --max-time 30`으로 `/`, `/dotidoit/`, `/app-ads.txt`를 확인한다. 인증 파일은 상태 200, 일반 텍스트, 정확한 코드인지 검사한다. 임의의 존재하지 않는 경로는 404 상태이며 홈 링크가 있는 사용자 정의 오류 페이지인지 확인한다. 반복 확인 중에도 60초 이내로 진행 상황을 전달한다.
- [ ] 공개 사이트도 휴대폰과 데스크톱에서 확인한다. 배포된 링크, 이미지, 스타일, 한글 표시를 확인하고 앱 소개·광고 파일이 실제 제공되는지 판단한다.
- [ ] 인계 문서에 실제 소스 커밋, 검증 명령과 결과, 배포 URL, 남은 콘솔 설정을 기록하고 문서도 푸시한다. 완료 보고는 코드 푸시·Pages 공개·AdMob 인증을 구분한다. Play Console에는 `https://opensky-doti.github.io/dotidoit/`를 등록하도록 안내하되 직접 콘솔을 변경하지 않는다.

## 실행 선택

사용자 검토 후 실행한다. 작은 단일 사이트이고 작업들이 같은 파일 계약에 의존하므로 이 세션에서 직접 구현하는 방식을 권장한다. 사용자가 원하면 작업별 구현·리뷰를 분리하는 방식도 가능하다. 아직 구현 또는 배포를 완료한 상태가 아니다.

## 참고 자료

- [GitHub Pages 사용자 정의 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
