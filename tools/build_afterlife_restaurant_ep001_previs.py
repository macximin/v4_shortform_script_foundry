#!/usr/bin/env python3
"""Build the locked episode-001 blue-line previs package without touching its source."""

from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/candidates/afterlife_restaurant/episode_001_daily_opening_v0.1.md"
RECEIPT = ROOT / "artifacts/candidates/afterlife_restaurant/episode_001_daily_opening_lock_receipt_v0.1.json"
OUT = ROOT / "artifacts/candidates/afterlife_restaurant/episode_001_daily_opening_previs_v0.1"
FRAMES = OUT / "frames"

INK = "#1155aa"
PAPER = "#f7fbff"
PALE = "#dfeeff"
ACCENT = "#2a75c9"
MUTED = "#5c7190"


# Timing, dialogue, and actions are a direct visual partition of the owner-locked file.
PANELS = [
    ("01", "0:00", "0:03", "ECU", "LOW / TILT", "D: C→L, 팬을 기울임", "푸른 불길이 팬 가장자리를 핥는다.", "SFX 푸슉"),
    ("02", "0:03", "0:06", "CU", "EYE / PUSH", "접시 C, 심사위원 배경", "완성 접시·멈춘 심사위원.", "SFX 플래시·박수"),
    ("03", "0:06", "0:09", "LS", "LOW / STATIC", "D: C, 카메라가 아래 길을 막음", "도윤의 익숙한 영업용 손인사.", "도윤: 하핫, 안녕하세요."),
    ("04", "0:09", "0:15", "MCU", "EYE / PAN R", "전무 L→C, D R", "도시락 시제품·계약금 30억 제시.", "전무: 단독 콜라보를 해 주신다면…"),
    ("05", "0:15", "0:23", "MCU", "EYE / PAN L", "호텔 회장 R→C, D L", "아시아 72개 호텔 지도·100억 제시.", "회장: 저희는 백억을 드리겠습니다!"),
    ("06", "0:23", "0:35", "WS", "EYE / DOLLY IN", "군중 양옆, 만상 C, D 후경", "군중이 갈라지고 지분 50%·300억 증서.", "만상식품 회장: 회장님이 되어 주십시오!"),
    ("07", "0:35", "0:41", "MS", "EYE / TRACK R", "D: C→R, 시선만 직원 통로", "연호 속 영업용 웃음, 발은 멈추지 않는다.", "군중: 식신! / 직원: 이쪽입니다."),
    ("08", "0:41", "0:49", "WS", "REAR / TRACK", "D: R→C, 엘리베이터", "문이 닫히며 금액과 연호가 먹먹해진다.", "SFX 문 닫힘·띵"),
    ("09", "0:49", "0:57", "MCU", "EYE / HOLD", "D C, 휴대폰 화면 L", "딸 영상통화 앞에서 눈매가 편안해진다.", "딸: 케이크 같이 먹는 거다. / D: 금방 갈게."),
    ("10", "0:57", "1:05", "WS", "HIGH / SNAP CUT", "연화 R, D C 엎드림", "엘리베이터 검은 화면 → 쟁반 탁!", "연화: 영업 전에 자는 배짱은 어디서…"),
    ("11", "1:05", "1:13", "TWO", "EYE / STATIC", "D L, 연화 R, 서로 안 봄", "연화는 서 있고 도윤은 몸을 일으킨다.", "D: 오 분만… / 연화: 십 분이니라."),
    ("12", "1:13", "1:20", "WS", "SIDE / PAN R", "연화 R→L, D L→C", "연화는 찻잔, 도윤은 솥 공기구멍.", "인물 슈퍼: 연화 / 삼도식당 홀지기"),
    ("13", "1:20", "1:27", "MS", "SIDE / HOLD", "D C, 연화 R, 둘 다 정면", "도윤이 보지 않고 불을 낮춰 솥뚜껑을 멈춘다.", "SFX 달그락 → 멎음"),
    ("14", "1:27", "1:35", "XCU", "TOP / MATCH", "D 손 L→C, 연화 손 R→C", "행주·쟁반 무시선 핸드오프, 수조가 부푼다.", "SFX 물 울림"),
    ("15", "1:35", "1:41", "WS", "SIDE / TRACK", "망각어 L→R, 연화 R→C", "망각어가 튀고 연화 쟁반이 받아 낸다.", "연화: 오늘 것은 제법 묵직하구나."),
    ("16", "1:41", "1:47", "MS", "SIDE / FOLLOW", "쟁반 C→D 도마, D C", "반 바퀴 돈 쟁반, 물고기가 도마로 미끄러진다.", "행동음: 철판 스르륵"),
    ("17", "1:47", "1:52", "ECU", "TOP / HOLD", "D 손 C, 물고기 C", "배 탄력과 아가미 냄새를 판독한다.", "도윤: 오늘 건 좋네."),
    ("18", "1:52", "1:57", "MCU", "LOW / PUSH", "D C, 칼 수직", "확신 있는 칼 세우기. 연화는 그릇 준비.", "SFX 칼각"),
    ("19", "1:57", "2:04", "TOP", "TOP / TRACK", "칼 L→R, 살 C", "검은 뼈를 따라 한 번, 투명한 살 분리.", "SFX 사각"),
    ("20", "2:04", "2:10", "MS", "SIDE / MATCH", "연화 접시 R→C, D 팬 L→C", "접시·작은 팬이 행동보다 먼저 들어온다.", "무대사"),
    ("21", "2:10", "2:20", "ECU", "LOW / PUSH", "볼살 C, 불 L→C", "물기 제거 → 푸른 불 위에서 가장자리 익힘.", "SFX 지글"),
    ("22", "2:20", "2:28", "ECU", "TOP / HOLD", "푸른 뿌리 C, 숯불 아래", "숯불에 굴린 뿌리의 검은 껍질이 갈라진다.", "SFX 톡"),
    ("23", "2:28", "2:34", "ECU", "SIDE / WHIP", "볼살 C, 불 R", "검은 껍질을 불에 한 번 스쳐 부풀린다.", "SFX 푸슉"),
    ("24", "2:34", "2:38", "TOP", "TOP / SETTLE", "두 접시 L/R, D 손 C", "금빛 뿌리·검은 껍질·투명 살·푸른 소금 완성.", "도윤: 간 봐."),
    ("25", "2:38", "2:49", "MCU", "EYE / HOLD", "연화 C, 발끝 하단", "첫입. 근엄한 표정과 들썩이는 발끝의 충돌.", "연화(M): 맛있다."),
    ("26", "2:49", "2:57", "MCU", "TOP / SNAP", "연화 젓가락 L→C, D 접시 C→R", "연화 젓가락이 멈추고 도윤이 자기 접시를 당긴다.", "도윤: 하나는 내 거야."),
    ("27", "2:57", "3:06", "TWO", "EYE / HOLD", "연화 L, 빈 의자 C, D R→C", "젓가락 끝이 의자를 두드린다. 도윤이 다시 앉는다.", "연화: 식으면 맛없느니라."),
    ("28", "3:06", "3:15", "WS", "SIDE / SLOW PULL", "D·연화 나란히 C, 창밖 안개", "말없이 먹고 두 빈 접시가 거의 동시에 놓인다.", "SFX 낮은 화덕"),
    ("29", "3:15", "3:25", "MS", "SIDE / PAN", "D L→R, 연화 R→L", "도윤은 접시, 연화는 카운터·찻잔을 즉시 리셋.", "SFX 물소리"),
    ("30", "3:25", "3:37", "WS", "TOP / TRACK", "D 보관함 C, 연화 목패 R", "남은 살 보관·뼈 팬·뿌리 덮기·목패 자리 비우기.", "무대사"),
    ("31", "3:37", "3:47", "WS", "INTERIOR→WINDOW / DISSOLVE", "연화 창 R, D 그릇 L", "노을빛이 사라져 깊은 푸른색. 식당은 계속 밝다.", "SFX 찻물 끓음"),
    ("32", "3:47", "3:55", "LS", "EXTERIOR / HOLD", "연화 문 C, D 화덕 L", "목패 걸기·영업등 점등. 푸른 안개와 문종.", "연화: 개점이니라! / SFX 탁"),
    ("33", "3:55", "4:01", "MS", "LOW / PUSH", "김문성 C→L, 시선 화덕 R", "검댕 작업복·그을린 금속. 도윤보다 화덕을 먼저 본다.", "SFX 문종"),
    ("34", "4:01", "4:08", "CU", "TOP / HOLD", "김문성 손 C, 찻잔 C", "오래된 화상·굳은살이 뜨거운 찻잔을 감싼다.", "연화: 어서 오시게."),
    ("35", "4:08", "4:17", "TWO", "EYE / SLOW PUSH", "김문성 L, D R, 화덕 후경", "도윤의 시선: 손 → 검댕 옷깃 → 불을 보는 눈. 암전.", "김문성: 뜨거운 국물로 주시오. / D: 알겠습니다."),
]


def sec(value: str) -> int:
    minute, second = value.split(":")
    return int(minute) * 60 + int(second)


def lines(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def txt(x: int, y: int, content: str, size: int = 28, color: str = INK, anchor: str = "start", weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Apple SD Gothic Neo" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(content)}</text>'


def poly(points: list[tuple[int, int]], stroke: str = INK, fill: str = "none", width: int = 7) -> str:
    flat = " ".join(f"{x},{y}" for x, y in points)
    return f'<polyline points="{flat}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def figure(x: int, y: int, label: str, face: str = "R", scale: float = 1.0, pose: str = "stand") -> str:
    r = int(28 * scale)
    body = int(90 * scale)
    arm = int(62 * scale)
    head = f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{INK}" stroke-width="7"/>'
    eye_dx = int(10 * scale) * (1 if face == "R" else -1)
    eye = f'<circle cx="{x + eye_dx}" cy="{y - 4}" r="4" fill="{INK}"/>'
    torso = f'<path d="M{x},{y+r} L{x},{y+r+body} M{x-int(42*scale)},{y+r+body//2} L{x+int(42*scale)},{y+r+body//2} M{x},{y+r+body} L{x-int(35*scale)},{y+r+body+int(55*scale)} M{x},{y+r+body} L{x+int(35*scale)},{y+r+body+int(55*scale)}" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
    if pose == "reach":
        torso += f'<path d="M{x-int(35*scale)},{y+r+body//2} L{x-int(35*scale)-arm},{y+r+body//2-int(12*scale)} M{x+int(35*scale)},{y+r+body//2} L{x+int(35*scale)+arm},{y+r+body//2-int(12*scale)}" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
    if pose == "sit":
        torso += f'<path d="M{x},{y+r+body} L{x+int(55*scale)},{y+r+body} L{x+int(55*scale)},{y+r+body+int(42*scale)}" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
    return head + eye + torso + txt(x, y - int(42 * scale), label, int(22 * scale), anchor="middle", weight=700)


def arrow(x1: int, y1: int, x2: int, y2: int) -> str:
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{ACCENT}" stroke-width="7" fill="none" marker-end="url(#arrow)" stroke-dasharray="15 12"/>'


def food(x: int, y: int, kind: str = "plate") -> str:
    if kind == "fire":
        return f'<path d="M{x-70},{y+80} Q{x-85},{y+10} {x-20},{y-40} Q{x-10},{y+15} {x+20},{y-70} Q{x+85},{y+5} {x+55},{y+80} Z" fill="none" stroke="{INK}" stroke-width="8"/>'
    if kind == "fish":
        return f'<path d="M{x-95},{y} Q{x-25},{y-55} {x+50},{y} Q{x-25},{y+55} {x-95},{y} M{x+50},{y} L{x+105},{y-58} L{x+92},{y} L{x+105},{y+58} Z" fill="none" stroke="{INK}" stroke-width="8"/><circle cx="{x-42}" cy="{y-12}" r="7" fill="{INK}"/>'
    if kind == "root":
        return f'<path d="M{x-90},{y+25} Q{x-35},{y-55} {x+25},{y+10} Q{x+70},{y+50} {x+105},{y-20}" fill="none" stroke="{INK}" stroke-width="18" stroke-linecap="round"/><path d="M{x-35},{y-10} L{x-8},{y+35} M{x+25},{y+5} L{x+52},{y+44}" stroke="{INK}" stroke-width="6"/>'
    return f'<ellipse cx="{x}" cy="{y}" rx="135" ry="38" fill="none" stroke="{INK}" stroke-width="8"/><path d="M{x-85},{y} Q{x},{y-60} {x+85},{y}" fill="none" stroke="{INK}" stroke-width="7"/>'


def scene_art(no: str) -> str:
    # Reusable rough language: sparse perspective lines, labelled actors, and one readable action vector.
    base = f'<rect x="70" y="140" width="1780" height="625" rx="8" fill="{PAPER}" stroke="{INK}" stroke-width="7"/>'
    base += '<path d="M70,660 L1850,660 M260,765 L820,430 M1660,765 L1100,430" fill="none" stroke="#a9c7e8" stroke-width="4" stroke-dasharray="16 14"/>'
    n = int(no)
    if n <= 2:
        base += food(900, 525, "fire") + food(1030, 610) + figure(1470, 480, "심사", "L", .8, "sit")
    elif n == 3:
        base += figure(960, 430, "도윤", "R", 1.2, "reach") + ''.join(f'<rect x="{x}" y="270" width="90" height="150" fill="none" stroke="{INK}" stroke-width="6"/>' for x in [240, 390, 1540, 1690])
    elif n in (4, 5, 6, 7):
        base += figure(1180 if n != 6 else 960, 400, "도윤", "L", 1.15, "stand")
        if n == 4: base += figure(550, 430, "전무", "R", 1.0, "reach") + '<rect x="400" y="570" width="250" height="120" fill="none" stroke="#1155aa" stroke-width="6"/>' + txt(525, 640, "30억", 46, anchor="middle", weight=700)
        if n == 5: base += figure(1420, 410, "호텔", "L", 1.0, "reach") + '<rect x="1360" y="565" width="270" height="140" fill="none" stroke="#1155aa" stroke-width="6"/>' + txt(1495, 635, "72 호텔", 38, anchor="middle", weight=700)
        if n == 6:
            base += figure(960, 380, "만상", "L", 1.3, "reach") + '<path d="M150,530 L650,530 M1270,530 L1770,530" stroke="#1155aa" stroke-width="10"/>' + txt(960, 690, "지분 50% · 300억", 48, anchor="middle", weight=700)
        if n == 7: base += figure(540, 480, "군중", "R", .8) + '<rect x="1500" y="265" width="190" height="390" fill="none" stroke="#1155aa" stroke-width="8"/>' + arrow(1120, 500, 1460, 500)
    elif n in (8, 9):
        base += '<rect x="650" y="210" width="620" height="450" rx="35" fill="none" stroke="#1155aa" stroke-width="10"/><path d="M960,210 L960,660" stroke="#1155aa" stroke-width="7"/>' + figure(870, 420, "도윤", "R", 1.0)
        if n == 9: base += '<rect x="1080" y="350" width="190" height="265" rx="22" fill="none" stroke="#1155aa" stroke-width="8"/>' + figure(1175, 445, "딸", "L", .45, "sit")
    elif n in (10, 11, 12, 13, 14):
        base += '<rect x="200" y="560" width="1520" height="120" fill="none" stroke="#1155aa" stroke-width="8"/>' + figure(760, 430, "도윤", "R", 1.0, "sit" if n == 10 else "reach") + figure(1250, 400, "연화", "L", 1.0, "reach")
        if n == 10: base += '<rect x="1330" y="330" width="280" height="135" fill="none" stroke="#1155aa" stroke-width="8"/>' + txt(1470, 415, "탁!", 62, anchor="middle", weight=700)
        if n == 14: base += '<ellipse cx="960" cy="590" rx="160" ry="65" fill="none" stroke="#1155aa" stroke-width="8"/>' + arrow(790, 490, 950, 490) + arrow(1180, 490, 990, 490)
    elif n in (15, 16, 17, 18, 19, 20):
        base += '<rect x="350" y="560" width="1220" height="120" fill="none" stroke="#1155aa" stroke-width="8"/>' + food(960 if n != 15 else 750, 480, "fish") + figure(1350, 390, "도윤", "L", .9, "reach")
        if n in (15,16): base += figure(550 if n == 15 else 620, 410, "연화", "R", .9, "reach") + arrow(700, 430, 1050, 500)
        if n == 18: base += '<path d="M950,310 L1010,520" stroke="#1155aa" stroke-width="12"/>'
        if n == 19: base += '<path d="M720,430 L1180,540" stroke="#1155aa" stroke-width="9" stroke-dasharray="18 12"/>'
        if n == 20: base += food(700, 620) + '<rect x="1210" y="575" width="190" height="80" fill="none" stroke="#1155aa" stroke-width="7"/>'
    elif n in (21,22,23,24):
        if n == 21: base += food(960, 500, "fire") + '<path d="M760,560 Q960,390 1160,560" fill="none" stroke="#1155aa" stroke-width="12"/>'
        if n == 22: base += food(960, 500, "root") + '<circle cx="960" cy="610" r="145" fill="none" stroke="#1155aa" stroke-width="8" stroke-dasharray="15 10"/>'
        if n == 23: base += food(950, 505, "fire") + '<path d="M820,550 Q950,430 1090,550" fill="none" stroke="#1155aa" stroke-width="15"/>'
        if n == 24: base += food(620, 540) + food(1300, 540) + '<path d="M520,535 L720,485 M1200,535 L1400,485" stroke="#1155aa" stroke-width="9"/>'
    elif n in (25, 26, 27, 28):
        base += '<rect x="250" y="570" width="1420" height="110" fill="none" stroke="#1155aa" stroke-width="8"/>' + figure(720, 420, "연화", "R", 1.0, "sit") + figure(1210, 420, "도윤", "L", 1.0, "sit") + food(720, 600) + food(1210, 600)
        if n == 25: base += '<path d="M705,640 q18,35 36,0" fill="none" stroke="#1155aa" stroke-width="7"/>' + txt(735, 720, "발끝", 22, anchor="middle")
        if n == 26: base += arrow(790, 520, 1120, 520)
        if n == 27: base += '<rect x="930" y="450" width="140" height="190" fill="none" stroke="#1155aa" stroke-width="7"/>' + txt(1000, 690, "빈 의자", 25, anchor="middle")
        if n == 28: base += '<circle cx="720" cy="600" r="45" fill="none" stroke="#1155aa" stroke-width="7"/><circle cx="1210" cy="600" r="45" fill="none" stroke="#1155aa" stroke-width="7"/>'
    elif n in (29,30,31,32):
        base += '<rect x="250" y="550" width="1420" height="130" fill="none" stroke="#1155aa" stroke-width="8"/>' + figure(700, 410, "도윤", "R", 1.0, "reach") + figure(1280, 400, "연화", "L", 1.0, "reach")
        if n == 30: base += '<rect x="520" y="585" width="250" height="80" fill="none" stroke="#1155aa" stroke-width="7"/>' + '<path d="M1180,300 L1180,550" stroke="#1155aa" stroke-width="10"/>'
        if n == 31: base += '<rect x="1350" y="220" width="250" height="280" fill="none" stroke="#1155aa" stroke-width="8"/>' + '<path d="M1380,350 Q1480,260 1580,350" fill="none" stroke="#1155aa" stroke-width="9" stroke-dasharray="18 12"/>'
        if n == 32: base += '<rect x="700" y="240" width="550" height="420" fill="none" stroke="#1155aa" stroke-width="10"/>' + '<rect x="1270" y="325" width="110" height="75" fill="none" stroke="#1155aa" stroke-width="8"/>' + txt(1325, 380, "영업", 25, anchor="middle")
    else:
        base += '<rect x="280" y="550" width="1400" height="130" fill="none" stroke="#1155aa" stroke-width="8"/>' + food(1450, 440, "fire") + figure(620, 400, "김문성", "R", 1.05, "stand") + figure(1100, 410, "도윤", "L", 1.0, "stand")
        if n == 34: base += '<path d="M510,500 q45,-110 90,0" fill="none" stroke="#1155aa" stroke-width="10"/><circle cx="550" cy="515" r="78" fill="none" stroke="#1155aa" stroke-width="9"/>'
        if n == 35: base += arrow(980, 410, 700, 410) + '<path d="M680,340 q-80,65 0,130" fill="none" stroke="#1155aa" stroke-width="6" stroke-dasharray="12 10"/>'
    return base


def svg(panel: tuple[str, str, str, str, str, str, str, str]) -> str:
    no, start, end, size, camera, position, action, dialogue = panel
    seconds = sec(end) - sec(start)
    footer_action = lines(action, 46)
    footer_dialogue = lines(dialogue, 55)
    action_svg = "".join(txt(100, 885 + i * 33, line, 25, MUTED) for i, line in enumerate(footer_action))
    dialogue_svg = "".join(txt(1000, 885 + i * 33, line, 25, INK, weight=600) for i, line in enumerate(footer_dialogue))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{ACCENT}"/></marker></defs>
<rect width="1920" height="1080" fill="{PAPER}"/>
{txt(70, 70, f'삼도식당 1화 · 파란선 러프 콘티 · CUT {no}', 38, INK, weight=700)}
{txt(1850, 70, f'{start}–{end}  ({seconds:02d}s)', 34, INK, anchor='end', weight=700)}
{scene_art(no)}
<rect x="70" y="795" width="1780" height="220" rx="8" fill="{PALE}" stroke="{INK}" stroke-width="5"/>
{txt(100, 835, f'샷 {size}   |   카메라 {camera}', 28, INK, weight=700)}
{txt(1000, 835, f'인물·시선 {position}', 28, INK, weight=700)}
{action_svg}{dialogue_svg}
{txt(70, 1055, 'LOCKED SCRIPT: episode_001_daily_opening_v0.1.md  ·  PREVIS ONLY / 비정본 디자인', 20, MUTED)}
</svg>'''


def cut_list() -> str:
    rows = [
        "# 삼도식당 애니메이션 1화 — 파란선 프리비즈 컷 목록 v0.1",
        "",
        "- 상태: 후보 프리비즈. 인물·의상·식당 미술의 정본을 확정하지 않는다.",
        "- 화면: 16:9 가로, 무음 자막 애니매틱, 총 4분 17초 (257초).",
        "- 잠금 대조: `episode_001_daily_opening_v0.1.md` / SHA-256 `e3d037e7206f9d0b4fbbe820d77c44778bb6cd640d3a3995390844952cc4d031`.",
        "- 연출 원칙: 도윤·연화는 무시선 핸드오프와 병렬 작업으로 오래 맞춘 동업자임을 보인다. 부녀·보호자·로맨스 구도는 사용하지 않는다.",
        "",
        "| 컷 | TC | 샷 | 카메라 | 인물·시선 | 핵심 행동 | 대사·효과음 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for no, start, end, size, camera, position, action, dialogue in PANELS:
        rows.append(f"| {no} | {start}–{end} | {size} | {camera} | {position} | {action} | {dialogue} |")
    rows += [
        "",
        "## 축·전환 메모",
        "",
        "- 행사장: 도윤의 퇴장 방향은 화면 오른쪽. 엘리베이터 이후 삼도식당에서는 도윤을 화면 왼쪽 작업선, 연화를 화면 오른쪽 홀선으로 고정해 역할과 동선을 읽힌다.",
        "- `0:57`은 닫히는 엘리베이터의 검은 면에서 쟁반의 `탁!`으로 하드 컷한다. 공간은 바뀌지만 리듬은 이어진다.",
        "- 조리부는 `포획(15–16) → 판독(17–18) → 손질(19–20) → 직화(21–23) → 조립(24)`의 다섯 화면 문법으로 분리한다.",
        "- `3:37–3:55`는 조도를 죽이지 않는다. 노을만 빠지고, 내부 기본등·화덕·영업등이 순차적으로 읽히게 한다.",
        "- 마지막은 김문성의 대사 뒤 ‘손 → 검댕 옷깃 → 화덕을 보는 눈’의 도윤 POV로 인물의 주문을 읽어 내는 훅을 만든다.",
    ]
    return "\n".join(rows) + "\n"


def audit() -> str:
    return """# 1화 프리비즈 감리 메모 v0.1

## 초반 후킹

0:00~0:35를 불길·접시·심사 반응·세 차례의 금액 상승으로 압축해, 도윤의 실력과 외부 가치가 한 화면의 행동으로 읽힌다. 0:35부터는 웃는 얼굴과 탈출 방향의 불일치가 다음 정서 비트를 예고한다.

## 딸 장면의 감정 전달

엘리베이터 안에서 휴대폰을 화면 왼쪽, 도윤을 오른쪽에 두어 무대의 카메라 압박과 반대 구도를 만든다. 표정의 작은 이완과 ‘금방 갈게’만 남기며, 대본 밖의 사고·계약·귀환 정보를 덧붙이지 않는다.

## 도윤·연화 케미

12~14, 19~20, 29~30에서 눈을 맞추지 않아도 도구·접시·홀 정리가 먼저 도착한다. 연화는 실제 홀 운영자이고 도윤은 능숙한 조리자이며, 감정 연출은 25~28의 식욕과 식사 행동으로만 처리한다.

## 음식 조리 가독성

100초 직원식 중 조리 변환은 63초를 확보했다. 패널 15~24가 포획·판독·손질·직화·조립을 각각 별도 샷 문법으로 고정하므로, 재료와 완성 접시를 한 화면의 장식으로 뭉개지지 않게 한다.

## 김문성 엔딩 훅

김문성은 얼굴 설명보다 화상·굳은살·검댕·화덕 우선 시선으로 먼저 소개된다. ‘뜨거운 국물로 주시오’ 직후 도윤의 3단 읽기 시선과 장작 파열을 배치해 2화의 조리 행동으로 넘어갈 질문을 남긴다.
"""


def write_manifest() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if source_hash != receipt["source_sha256"]:
        raise SystemExit("Locked source hash mismatch; previs was not created.")
    outputs = {}
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            outputs[str(path.relative_to(OUT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": 1,
        "artifact_id": "afterlife_restaurant:ep001:daily_opening_previs:v0.1",
        "status": "candidate_previs",
        "external_delivery_allowed": False,
        "canonical_promotion_allowed": False,
        "source_file": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "lock_receipt": str(RECEIPT.relative_to(ROOT)),
        "panel_count": len(PANELS),
        "runtime_seconds": 257,
        "animatic_audio": "none (timing subtitles only; no music or final sound design)",
        "design_status": "rough blue-line silhouettes only; no character, costume, or set canon established",
        "outputs_sha256": outputs,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing candidate folder: {OUT}")
    OUT.mkdir(parents=True)
    FRAMES.mkdir()
    for panel in PANELS:
        (FRAMES / f"cut_{panel[0]}.svg").write_text(svg(panel), encoding="utf-8")
    (OUT / "01_cut_list.md").write_text(cut_list(), encoding="utf-8")
    (OUT / "04_supervision_memo.md").write_text(audit(), encoding="utf-8")
    concat = ["ffconcat version 1.0"]
    for no, start, end, *_ in PANELS:
        concat += [f"file 'frames/cut_{no}.png'", f"duration {sec(end) - sec(start)}"]
    # The concat demuxer needs one final duplicate to retain the last still's duration.
    # The encoder is explicitly capped at the locked 257-second runtime.
    concat.append(f"file 'frames/cut_{PANELS[-1][0]}.png'")
    (OUT / "animatic.ffconcat").write_text("\n".join(concat) + "\n", encoding="utf-8")
    write_manifest()


if __name__ == "__main__":
    main()
