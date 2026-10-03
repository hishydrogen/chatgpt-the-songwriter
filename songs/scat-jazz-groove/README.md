# Floating scat — 2단계 그루브 스케치

사용자 선택: 보컬 C(Milk), 건반 B(Splendid Steinway), 베이스 A(업라이트),
드럼 B(DRSKit). 124 BPM, F장조, 60:40 스윙. 1단계의 오리지널 화성과
49음절 스캣 훅을 그대로 사용한다.

각 버전은 반주 8마디, 같은 반주에 Milk 스캣을 얹은 8마디, 소리가
정리되는 1마디로 구성한다. 반주와 보컬을 비교하는 두 구간의 악기 연주는
노트, 타이밍, 강약이 같다. 세 버전의 보컬 연주도 같다.

| 버전 | 반주만 | 스캣 포함 | 편곡의 중심 |
|---|---|---|---|
| A — Airborne swing | 0:00.0-0:15.5 | 0:15.5-0:31.0 | 가볍게 흐르는 워킹 베이스, 라이드 스윙과 피아노 리프 |
| B — Syncopated pocket | 0:32.9-0:48.4 | 0:48.4-1:03.9 | 싱코페이션 베이스와 피아노, 오프비트 기타와 봉고 |
| C — Brass conversation | 1:05.8-1:21.3 | 1:21.3-1:36.8 | 강한 백비트, 라이드 벨과 브라스의 짧은 응답 |

`out/master.mp3`는 전체 비교 파일이다. `out/groove-A.mp3`,
`out/groove-B.mp3`, `out/groove-C.mp3`는 같은 마스터에서 추출한 개별 파일이다.
각 개별 파일에서는 15.5초에 스캣이 들어온다.

## 세션과 MIDI

17트랙, 노트 2,705개. 컴핑 피아노와 응답 리프를 분리했고, 업라이트,
뮤트 기타, 트롬본, 호른, 뮤트 트럼펫, 테너 색소폰을 독립 성부로 썼다.
DRSKit은 킥, 스네어, 라이드, 하이햇, 톰, 심벌로 나눴다. 별도의 봉고와
셰이커만 Virtuosity 샘플을 사용한다.

- 베이스는 화성별로 쓴 연결음과 프레이즈 마지막 F 도착을 사용한다.
- 피아노는 루트리스 보이싱, 작은 분산 어택과 짧은 페달을 사용한다.
- 강박만 반복하지 않도록 드럼 고스트 노트, 라이드 강약과 서로 다른 필인을 썼다.
- 세 음짜리 피아노 리프가 스캣의 문장 끝을 받는다. 테너는 다른 빈자리에 답한다.
- MIDI의 악기 ID, 음절, 피치 벤드와 컨트롤러를 보존한다. 건반 두 성부와
  다른 유음 악기는 독립 MIDI 채널을 사용하므로 페달과 표현이 간섭하지 않는다.

`out/scat-jazz-groove-midi.zip`에는 전체 Type-1 MIDI, 17개 개별 트랙,
각 버전의 스캣 포함 8마디 Type-1 MIDI 3개, 악기와 채널 표가 들어 있다.
이 MIDI의 실제 음색은 지정한 샘플 악기를 연결해야 재현된다.

## 검증과 재현

`score-check.json`은 화성, 음역, 발음 샘플, 동일 연주 비교, MIDI 채널과
노트 종료를 검사한다. `out/audio-check.json`과 `out/vocal-pitch.png`는 실제
보컬 음정, 파형 점프, 구간별 보컬 균형과 비교 음량의 검사 결과다.
마스터는 -14 LUFS, -1 dBTP를 목표로 하며 PLR 12 dB 이상을 유지한다.
보컬은 각 보컬 구간에서 가장 큰 개별 반주 트랙보다 4-6 dB 앞에 둔다.
동시에 연주하는 전체 밴드 합계와의 차이를 뜻하는 수치는 아니다.

반주 비교와 보컬 포함 비교는 각각 공통 기준 음량 ±1 dB 안에 있는지
확인한다. 전체 마스킹 표는 킥과 베이스, 베이스와 컴핑, 서로 다른 구간의
라이드와 하이햇에 대한 청취 점검 지점이다. 음색 선택은 사용자가 판단한다.

최종 검사 통과: -14.01 LUFS, -1.0 dBTP, PLR 13.01 dB, 기술 경고 없음.
보컬 레벨 차이는 A 4.9 dB, B 6.0 dB, C 4.5 dB다. 세 테이크 각각
49음을 측정했으며 음정 중앙 오차 0.9센트, 최대 오차 6.8센트다.
큰 파형 점프는 검출되지 않았다. 반주 후보는 기준에서 최대 0.8 dB,
보컬 포함 후보는 최대 0.4 dB 차이다.

프로젝트 루트에서 설치한 Ubuntu 스튜디오로 실행한다.

```bash
bash scripts/studio.sh --python songs/scat-jazz-groove/check_score.py
bash scripts/studio.sh build songs/scat-jazz-groove
bash scripts/studio.sh --python songs/scat-jazz-groove/check_audio.py
bash scripts/studio.sh --python songs/scat-jazz-groove/export_choices.py
```

1단계 `songs/scat-jazz-palette/song.py`가 원본 화성, 스캣과 MIDI 내보내기
설정을 제공한다. 샘플과 음성 합성 캐시는 `libs/`에 있다.
상업 발매 시 Milk 저작자의 사전 승인이 필요하며 자세한 출처는 `CREDITS.md`에 있다.
