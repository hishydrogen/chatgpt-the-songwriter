# claude-the-songwriter

코드로 작곡하고, 실제 샘플 악기와 신디사이저로 렌더링하고, 믹싱과 마스터링까지 하는 작업 환경이에요.

```
song.py (노트를 박자 단위로 작성)
  -> MIDI (트랙별, DAW에서 열 수 있는 전체 파일)
  -> 트랙별 stem 렌더링 (sfizz: SFZ 샘플 악기 / Surge XT: 신디사이저)
  -> 믹싱 (LSP EQ와 컴프레서, Dragonfly 리버브, 딜레이, 사이드체인 덕킹)
  -> 마스터링 (글루 컴프레서, -14 LUFS / -1 dBTP 리미팅)
  -> master.mp3, master.wav, 분석 리포트 (report.png, report.json)
```

## 사용법

```bash
scripts/setup.sh                                   # 새 컨테이너에서 한 번 (20-30분)
python -m songwriter instruments                   # 쓸 수 있는 악기 목록
python -m songwriter surge-patches pad             # Surge XT 패치 검색
python -m songwriter build songs/<곡>              # 렌더링, 믹싱, 마스터링, 분석
python scripts/measure_ref.py refs/ref.wav         # 참고곡의 템포, 박자감, 조성, 구성
python scripts/audition_levels.py songs/<곡>       # 오디션 후보 음량 확인
python scripts/release.py songs/<곡> --title ...   # 24비트, 16비트 ALAC + 메타데이터 + 아트
```

## 새 곡 시작하기

새 세션에서 참고할 노래의 음원을 올리고 "이 노래랑 비슷한 아주 좋은 음악을 만들어 주세요"라고
하면 돼요. AI는 `CLAUDE.md`에 정리된 방식대로 길이와 리드 악기 같은 것을 먼저 묻고, 네 번의
체크포인트(사운드 팔레트, 그루브 스케치, 러프 믹스, 최종 발매)를 거쳐 곡을 완성해요.
붙여 넣을 전문은 `docs/prompts/new-song.md`에 있어요.

## 완성곡

- **Mirage** (`songs/mirage/`): Janet Jackson "Nasty"(1986) 스타일. F단조, 103 BPM, 드럼머신과 8비트 샘플러 사운드.
- **Catalina Blue** (`songs/catalina-blue/`): The Doobie Brothers "What a Fool Believes"(1978) 스타일.
  Eb장조에서 B장조 브리지를 거쳐 E장조로 반음 올라가는 마지막 후렴, 테너 색소폰 리드, 페이드아웃.
  크레딧은 `songs/catalina-blue/CREDITS.md`에 있어요.

## 악기

- **피아노:** Salamander Grand (Yamaha C5), Maestro Concert Grand (Yamaha CF-3), Splendid Grand, 업라이트
- **건반:** Rhodes Mark I, Wurlitzer EP200, Yamaha CP80, Pianet T
- **드럼:** Virtuosity Drums, DrumGizmo DRSKit, SM Drums (모두 멀티 벨로시티, 라운드로빈)
- **베이스:** Black and Blue Basses, 업라이트 베이스 (피치카토, 아르코)
- **기타:** Black and Green Guitars, Emily Guitar, 펑키 뮤트 기타
- **오케스트라 (VSCO 2 CE):** 바이올린, 비올라, 첼로 섹션, 콘트라베이스, 하프, 호른, 트럼펫, 트롬본, 튜바, 플루트, 오보에, 클라리넷, 바순, 말렛 악기
- **솔로:** 첼로, 색소폰 4종
- **신디사이저:** Surge XT 패치 약 3,500개 (패드, 리드, 베이스, 플럭, 시퀀스 등)

샘플 라이브러리는 모두 무료 또는 오픈 라이선스로 배포된 것들이에요. 출처는 `scripts/fetch_libraries.sh`에 있고, 각 라이선스는 `libs/<이름>/` 안의 LICENSE나 README에 있어요. 음원을 공개하기 전에 확인하세요.
