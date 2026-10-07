# 오픈스카이 도티 안내 사이트

회사 앱 안내와 도티두잇 지원 페이지, AdMob 소유권 확인용 `app-ads.txt`를 GitHub Pages로 제공한다. 기존 앱 소스·APK·AAB·광고 모드와 개인정보처리방침 저장소는 이 사이트 배포로 변경되지 않는다.

## 주소

| 용도 | 공개할 주소 |
| --- | --- |
| 회사 앱 안내 | https://opensky-doti.github.io/ |
| 도티두잇 안내 | https://opensky-doti.github.io/dotidoit/ |
| 광고 인증 파일 | https://opensky-doti.github.io/app-ads.txt |
| 기존 개인정보처리방침 | https://kizwond.github.io/dotimoti-legal/dotidoit/privacy/ |

최초 공개 여부와 실제 검증 결과는 [인계 문서](docs/handoffs/2026-10-07-public-site.md)를 확인한다. 저장소에 코드가 있다고 사이트가 이미 공개되었다고 판단하지 않는다.

## 로컬 확인

Python 3.9 이상이면 검사와 미리보기에 별도 패키지가 필요 없다. macOS와 Linux에서 같은 명령을 사용한다.

```sh
git clone git@github.com:opensky-doti/opensky-doti.github.io.git
cd opensky-doti.github.io
python3 -m unittest discover -s tests -v
python3 scripts/validate_site.py site
python3 -m http.server 8765 --bind 127.0.0.1 --directory site
```

브라우저에서 `http://127.0.0.1:8765/`를 연다. 검사 성공 시 테스트 결과는 `OK`, 사이트 검사는 `Site validation passed.`가 표시된다. 로컬 서버의 미존재 경로 응답은 Python 기본 404이며, 사이트용 오류 페이지는 `/404.html`에서 확인한다.

## 파일 수정

- 홈: `site/index.html`
- 도티두잇: `site/dotidoit/index.html`
- 공통 스타일과 아이콘: `site/assets/`
- 광고 인증: `site/app-ads.txt`
- 오류 안내: `site/404.html`
- 배포: `.github/workflows/pages.yml`

아이콘은 도티두잇의 확정된 512px 스토어 이미지 복사본이다. 원본 SHA-256은 `ddbe4e0922e827f9eba167767e9e9907b847fc108143ddd9a037c58453e05d65`다. 아이콘 변경은 브랜드 결정 후 진행한다.

외부 추적 스크립트·광고 SDK·웹 폰트·로그인·입력 폼은 없다. GitHub 호스팅 자체의 접근 로그까지 없다고 설명해서는 안 된다. 웹에 공개할 수 없는 토큰·서명키·사용자 데이터를 이 공개 저장소에 넣지 않는다.

## 최초 Pages 설정과 배포

1. 저장소 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 설정한다.
2. 변경은 별도 브랜치에서 검증하고 검토한 뒤 `main`에 반영한다.
3. `git push origin main`으로 올린다.
4. **Actions → Validate and deploy Doti Pages**에서 `validate`와 `deploy` 작업이 모두 성공했는지 확인한다.
5. 초기 Pages 설정 전에 실행돼 실패했다면 설정 완료 후 **Re-run all jobs**로 재실행하거나 **Run workflow**에서 `main`을 선택한다.

워크플로는 JSON 문법으로 작성된 유효한 YAML이다. Python 표준 라이브러리만으로 파싱해 배포 조건과 산출물 범위를 검사할 수 있도록 선택했다. 수정 시 JSON 문법을 유지한다. PR은 검증만 하며, 수동 실행도 `main`에서만 배포된다. 테스트 실패 시 배포되지 않는다. 업로드 대상은 `site/`뿐이며 문서·테스트·QA 결과는 사이트에 게시하지 않는다.

검증 액션은 읽기 권한만 사용하고 배포 작업에만 Pages 및 OIDC 쓰기 권한을 부여한다. GitHub 환경 보호 규칙이 별도 승인을 요구하면 규칙을 해제하지 말고 승인 절차를 따른다.

## 공개 확인과 AdMob 후속 절차

```sh
curl --fail --show-error --silent --location --max-time 30 https://opensky-doti.github.io/
curl --fail --show-error --silent --location --max-time 30 https://opensky-doti.github.io/dotidoit/
curl --fail --show-error --silent --location --max-time 30 https://opensky-doti.github.io/app-ads.txt
```

마지막 응답은 로그인이나 HTML 화면 없이 다음 한 줄이어야 한다.

```text
google.com, pub-3081928577042149, DIRECT, f08c47fec0942fa0
```

브라우저에서 휴대폰·데스크톱 표시, 다운로드·문의·개인정보처리방침 링크도 확인한다. 임의의 없는 주소는 HTTP 404와 사이트의 오류 안내를 반환해야 한다.

정상 공개 후 Play Console의 도티두잇 **스토어 설정 → 스토어 등록정보 연락처 세부정보 → 웹사이트**에 `https://opensky-doti.github.io/dotidoit/`를 등록하고 변경사항을 공개 반영한다. 여기에 `/app-ads.txt` 주소를 넣지 않는다. Play 스토어의 앱 지원 영역에서 웹사이트 링크가 보이는지도 확인한다.

이후 AdMob의 앱 인증에서 **업데이트 확인**을 요청한다. Google의 탐색·반영에는 대기 시간이 발생할 수 있다. 사이트 공개, AdMob 앱 인증, 앱 준비 상태 심사, 실제 광고 송출은 각각 다른 단계다. 사이트 공개만으로 테스트 광고가 실광고로 전환되거나 인증이 완료되지는 않는다. 실광고 전환은 앱의 별도 체크리스트와 승인에 따라 진행한다.

## 문제 확인과 복구

- 사이트 전체 404: Pages 소스 설정과 최신 Actions 결과부터 확인한다.
- 파일은 있으나 게시자 불일치: AdMob 계정에서 제공한 코드와 공개 응답을 대조한다. 다른 앱의 판매자 정보를 임의로 지우지 않는다.
- 오래된 내용: Actions에서 배포한 커밋과 최신 main을 비교한다. 재빌드 대신 실패 원인을 먼저 확인한다.
- 배포 후 문제가 생김: `git log --oneline`으로 원인 커밋을 식별하고 `git revert <원인커밋>`을 검토·실행한다. 테스트 후 main에 푸시해 재배포한다. 강제 푸시나 기존 기록 삭제로 복구하지 않는다.

## 후속 앱 추가

도티모티 등 공개가 확정된 앱은 `site/<앱이름>/index.html`을 추가하고 홈에서 연결한다. 각 앱은 실제 스토어 링크·정확한 기능 설명·앱별 개인정보처리방침을 사용해야 한다. 도티두잇 방침을 다른 앱 방침으로 재사용하지 않는다.

각 앱의 스토어 웹사이트에 같은 호스트의 앱별 안내 주소를 지정하면 최상위 `app-ads.txt`를 공유할 수 있다. 동일한 회사 AdMob 계정은 같은 게시자 코드를 사용한다. AdMob 앱 등록과 앱 ID·광고 단위 생성은 앱별로 수행한다. 다른 게시자나 광고 네트워크를 추가할 때는 회사 승인 후 인증 파일과 검증 계약을 함께 변경한다.

## 설계와 계획

- [승인된 설계](docs/superpowers/specs/2026-10-07-doti-public-site-design.md)
- [구현 및 검증 계획](docs/superpowers/plans/2026-10-07-doti-public-site.md)
- [GitHub Pages 공식 배포 안내](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [AdMob 공식 인증 파일 안내](https://support.google.com/admob/answer/9363762?hl=ko)
