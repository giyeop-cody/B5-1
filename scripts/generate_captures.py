#!/usr/bin/env python3
"""자동 검증 텍스트를 읽어 동일한 내용의 PNG 실행 결과 캡처를 만든다.

`evidence/captures/*.png`는 터미널이나 DBeaver를 사람이 찍은 화면이 아니다.
같은 실행이 만든 텍스트 증거(`evidence/query_NN_result.txt`, `evidence/bonus_02_fk_error_test.txt`)를
그대로 렌더링한 사본이다. 원본은 텍스트 파일이고, 이미지는 README에서 읽기 좋게 만든 복제본이다.
"""

from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CAPTURES = EVIDENCE / "captures"
FONT_CANDIDATES = [
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError("한글 PNG 생성용 Noto Sans CJK 또는 대체 폰트가 필요합니다.")


def visual_lines(text: str, width: int = 118) -> list[str]:
    lines: list[str] = []
    for line in text.expandtabs(4).splitlines():
        if not line:
            lines.append("")
        else:
            lines.extend(textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False) or [""])
    return lines


def render(source: Path, target: Path) -> None:
    lines = visual_lines(source.read_text(encoding="utf-8"))
    body_font = font(19)
    title_font = font(23)
    line_height = 31
    width = 1800
    height = max(360, 80 + line_height * len(lines))
    image = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 58), fill="#1f2937")
    draw.text((28, 15), f"B5-1 실행 결과 캡처 · 스크립트가 텍스트 증거를 렌더링 · {source.name}", font=title_font, fill="#f9fafb")
    y = 78
    for index, line in enumerate(lines):
        color = "#93c5fd" if line in {"SQL", "RESULT", "VERIFICATION"} or line.startswith("===") else "#e5e7eb"
        draw.text((28, y), line, font=body_font, fill=color)
        y += line_height
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, optimize=True)


def main() -> None:
    CAPTURES.mkdir(parents=True, exist_ok=True)
    sources = sorted(EVIDENCE.glob("query_[0-9][0-9]_result.txt"))
    if len(sources) != 15:
        raise AssertionError(f"쿼리 결과 텍스트 15개가 필요합니다: {len(sources)}")
    for source in sources:
        render(source, CAPTURES / f"{source.stem.removesuffix('_result')}.png")
    render(EVIDENCE / "bonus_02_fk_error_test.txt", CAPTURES / "bonus_fk_error.png")
    print(f"captures={len(sources) + 1} PASS")


if __name__ == "__main__":
    main()
