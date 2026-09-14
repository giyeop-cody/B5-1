#!/usr/bin/env python3
"""B5-1 SQL을 새 SQLite DB에서 요구사항 순서대로 실행하고 제출 증거를 재생성한다.

실행 흐름은 README의 sqlite3 CLI 안내와 일부러 같다: 새 DB → 스키마 → seed → Q1~Q15 → 보너스·KPI.
Q13/Q14가 바꾼 상태를 보너스가 이어받으므로 증거 파일과 수동 실행 결과가 같은 숫자를 낸다.
검증 대상에는 SQL 실행뿐 아니라 문서 동기화(`bonus_report.md` 인용, README 표기, 링크)도 포함한다.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CORE_MARKER = re.compile(r"-- \[(Q\d{2})\]\[([^\]]+)\] (.+)")
BONUS_MARKER = re.compile(r"-- \[(B\d{2})\]\[([^\]]+)\] (.+)")
FAIL_MARKER = re.compile(r"-- \[(F\d{2})\]\[([^\]]+)\] (.+)")
# 보너스 2(일부러 무결성 깨뜨리기)의 SQL 본문은 4_bonus_queries.sql [F01]~[F04]에 있다.
# 여기에는 "어떤 오류로 차단되어야 하는가"만 대응표로 둔다.
FAIL_EXPECTED = {
    "F01": ("FK 없는 좌석 참조 차단", "FOREIGN KEY"),
    "F02": ("허용되지 않은 status 차단", "CHECK constraint failed"),
    "F03": ("음수 quantity 차단", "CHECK constraint failed"),
    "F04": ("중복 table_number 차단", "UNIQUE constraint failed"),
}
EXPECTED_MINIMUM_ROWS = {
    "menu_categories": 10,
    "store_tables": 10,
    "menus": 10,
    "orders": 10,
}
EXPECTED_COLUMN_TYPES = {
    "menu_categories": {"id": "INTEGER", "name": "TEXT"},
    "store_tables": {"id": "INTEGER", "table_number": "INTEGER", "capacity": "INTEGER"},
    "menus": {"id": "INTEGER", "name": "TEXT", "price": "INTEGER", "category_id": "INTEGER"},
    "orders": {
        "id": "INTEGER",
        "table_id": "INTEGER",
        "menu_id": "INTEGER",
        "quantity": "INTEGER",
        "order_time": "DATETIME",
        "status": "TEXT",
    },
}
EXPECTED_CORE_CATEGORIES = Counter({
    "기본조회": 4,
    "INNER JOIN": 2,
    "LEFT JOIN": 2,
    "집계": 3,
    "서브쿼리": 1,
    "수정": 1,
    "삭제": 1,
    "인덱스": 1,
})


@dataclass
class SqlCase:
    number: str
    category: str
    description: str
    sql: str


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def split_cases(path: str, marker: re.Pattern[str]) -> list[SqlCase]:
    cases: list[SqlCase] = []
    buffer = ""
    for line in read(path).splitlines(keepends=True):
        buffer += line
        if not sqlite3.complete_statement(buffer):
            continue
        match = marker.search(buffer)
        if match:
            cases.append(SqlCase(match.group(1), match.group(2), match.group(3), buffer.strip()))
        buffer = ""
    if buffer.strip():
        raise AssertionError(f"완성되지 않은 SQL 문장이 있습니다: {path}")
    return cases


def new_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(read("1_schema.sql"))
    connection.executescript(read("2_data.sql"))
    connection.commit()
    return connection


def tsv(columns: list[str], rows: list[sqlite3.Row | tuple]) -> str:
    lines = ["\t".join(columns), "-" * max(40, sum(map(len, columns)) + len(columns) * 4)]
    if not rows:
        lines.append("(0 rows)")
    else:
        lines.extend("\t".join("NULL" if value is None else str(value) for value in row) for row in rows)
    return "\n".join(lines)


def clean_sql(sql: str) -> str:
    lines = [line for line in sql.splitlines() if not line.startswith("-- ===")]
    return "\n".join(lines).strip()


def leading_keyword(sql: str) -> str:
    """주석을 건너뛰고 SQL의 첫 키워드를 돌려준다. DDL과 DML의 증거 표기를 구분한다."""
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        return stripped.split(None, 1)[0].upper()
    return ""


def write_result(case: SqlCase, columns: list[str], rows: list[sqlite3.Row | tuple], extra: str = "") -> None:
    number = int(case.number[1:])
    content = [
        f"=== {case.number} [{case.category}] {case.description} ===",
        "",
        "SQL",
        clean_sql(case.sql),
        "",
        "RESULT",
        tsv(columns, rows),
    ]
    if extra:
        content.extend(["", "VERIFICATION", extra])
    (EVIDENCE / f"query_{number:02d}_result.txt").write_text("\n".join(content) + "\n", encoding="utf-8")


def normalize_sql(sql: str) -> str:
    """주석을 지우고 공백을 한 칸으로 줄여 문서 대조용 문자열로 만든다."""
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)


def verify_docs_sync(core_cases: list[SqlCase], bonus_cases: list[SqlCase]) -> list[str]:
    """문서가 실제 SQL·설명·증거와 어긋나지 않았는지 대조한다.

    문서와 SQL을 따로 고치면 반드시 어긋난다(과거 지적 R1). 이 검사가 그 경로를 차단한다.
    """
    report = normalize_sql(read("bonus_report.md"))
    for case in bonus_cases:
        assert normalize_sql(case.sql).rstrip(";") in report, (
            f"{case.number}의 SQL 본문이 bonus_report.md에 그대로 없다."
        )
    checks = [f"bonus_report_quotes_all_bonus_sql={len(bonus_cases)} PASS"]

    readme = read("README.md")
    for case in core_cases:
        assert case.description in readme, f"{case.number}의 한 줄 설명이 README 표와 다르다."
        for suffix in (f"evidence/query_{int(case.number[1:]):02d}_result.txt",
                       f"evidence/captures/query_{int(case.number[1:]):02d}.png"):
            assert suffix in readme, f"README가 {suffix}를 링크하지 않는다."
    checks.append(f"readme_uses_sql_descriptions_and_links={len(core_cases)} PASS")

    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        assert "/home/" not in text and not re.search(r"\]\(/", text), (
            f"{path.relative_to(ROOT)}: 저장소 밖 절대 경로를 참조한다. 채점자가 열 수 없다."
        )
        for target in re.findall(r"\]\(([^)#][^)]*)\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            assert (path.parent / target).resolve().exists(), (
                f"{path.relative_to(ROOT)}: 끊긴 링크 {target}"
            )
    checks.append(f"markdown_links_and_no_external_paths={len(markdown_files())} PASS")

    assert not (EVIDENCE / "screenshots").exists(), "오래된 evidence/screenshots 디렉터리가 남아 있다."
    captures = sorted((EVIDENCE / "captures").glob("*.png"))
    assert len(captures) == 16 and all(path.stat().st_size > 0 for path in captures)
    checks.append("captures=16_and_screenshots_dir_removed PASS")
    return checks


def verify_schema(connection: sqlite3.Connection) -> list[str]:
    checks: list[str] = []
    tables = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )]
    expected_tables = sorted(EXPECTED_MINIMUM_ROWS)
    assert tables == expected_tables, (tables, expected_tables)
    checks.append(f"tables={len(tables)} PASS: {', '.join(tables)}")

    not_null_count = 0
    unique_count = 0
    column_count = 0
    for table, minimum in EXPECTED_MINIMUM_ROWS.items():
        count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count >= minimum, f"{table}: {count} < {minimum}"
        checks.append(f"{table} rows={count} PASS")

        table_info = connection.execute(f"PRAGMA table_info({table})").fetchall()
        pk_count = sum(row["pk"] > 0 for row in table_info)
        assert pk_count >= 1, f"{table} PK 없음"
        checks.append(f"{table} PK={pk_count} PASS")

        actual_types = {row["name"]: row["type"].upper() for row in table_info}
        assert actual_types == EXPECTED_COLUMN_TYPES[table], (table, actual_types)
        column_count += len(actual_types)
        not_null_count += sum(row["notnull"] == 1 for row in table_info)

        indexes = connection.execute(f"PRAGMA index_list({table})").fetchall()
        unique_count += sum(row["unique"] == 1 for row in indexes)

    assert column_count == 15
    checks.append("column_names_and_types=15 PASS")
    assert not_null_count >= 1
    checks.append(f"NOT_NULL_columns={not_null_count} PASS")
    assert unique_count >= 1
    checks.append(f"UNIQUE_indexes={unique_count} PASS")

    fk_count = sum(
        len(connection.execute(f"PRAGMA foreign_key_list({table})").fetchall())
        for table in EXPECTED_MINIMUM_ROWS
    )
    assert fk_count >= 2
    checks.append(f"foreign_keys={fk_count} PASS")
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    checks.append("PRAGMA foreign_keys=ON PASS")
    return checks


def clause(text: str, keyword: str) -> bool:
    return re.search(rf"\b{keyword}\b", text, re.IGNORECASE) is not None


def verify_rubric_coverage(cases: list[SqlCase], categories: Counter[str]) -> list[str]:
    """범주 수량뿐 아니라 PDF가 괄호에 적은 절(clause) 조건까지 확인한다."""
    by_category: dict[str, list[SqlCase]] = {}
    for case in cases:
        by_category.setdefault(case.category, []).append(case)

    for case in by_category["기본조회"]:
        sql = clean_sql(case.sql).upper()
        assert clause(sql, "WHERE") and clause(sql, "ORDER BY") and clause(sql, "LIMIT"), (
            f"{case.number}: 기본 조회는 WHERE·ORDER BY·LIMIT을 모두 포함해야 합니다."
        )

    aggregate_sql = " ".join(clean_sql(case.sql).upper() for case in by_category["집계"])
    assert clause(aggregate_sql, "GROUP BY")
    assert sum(clause(aggregate_sql, fn) for fn in ("COUNT", "SUM", "AVG")) >= 2, (
        "집계는 COUNT·SUM·AVG 중 2개 이상을 사용해야 합니다."
    )
    assert len(by_category["서브쿼리"]) >= 1 and clause(
        clean_sql(by_category["서브쿼리"][0].sql).upper(), "SELECT"
    )

    mutation_sql = " ".join(
        clean_sql(case.sql).upper()
        for category in ("수정", "삭제")
        for case in by_category[category]
    )
    assert clause(mutation_sql, "UPDATE") and clause(mutation_sql, "DELETE")

    assert any(clause(clean_sql(case.sql).upper(), "INNER JOIN") for case in by_category["INNER JOIN"])
    assert any(clause(clean_sql(case.sql).upper(), "LEFT JOIN") for case in by_category["LEFT JOIN"])
    return [
        "basic_4_all_have_where_orderby_limit PASS",
        "aggregate_group_by_and_2_of_count_sum_avg PASS",
        "subquery_update_delete_present PASS",
    ]


def verify_query_distribution(cases: list[SqlCase]) -> list[str]:
    """공식 요구사항이 정의하는 15개 SQL의 번호·설명·범주 수량과 절 조건을 확인한다."""
    assert [case.number for case in cases] == [f"Q{number:02d}" for number in range(1, 16)]
    assert all(case.description.strip() for case in cases), "모든 쿼리에 한 줄 설명이 필요합니다."

    categories = Counter(case.category for case in cases)
    assert categories == EXPECTED_CORE_CATEGORIES, (categories, EXPECTED_CORE_CATEGORIES)
    join_count = categories["INNER JOIN"] + categories["LEFT JOIN"]
    assert join_count == 4
    return [
        "query_numbers_and_descriptions=15 PASS",
        "query_distribution="
        f"basic:{categories['기본조회']},join:{join_count},aggregate:{categories['집계']},"
        f"subquery:{categories['서브쿼리']},mutation:{categories['수정'] + categories['삭제']},"
        f"index:{categories['인덱스']} PASS",
        *verify_rubric_coverage(cases, categories),
    ]


def execute_core(connection: sqlite3.Connection, cases: list[SqlCase]) -> list[str]:
    assert len(cases) == 15, f"핵심 SQL은 15개여야 합니다: {len(cases)}"
    checks = ["core_queries=15 PASS", *verify_query_distribution(cases)]
    for case in cases:
        cursor = connection.execute(case.sql)
        columns: list[str]
        rows: list[sqlite3.Row | tuple]
        extra = ""
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        elif leading_keyword(case.sql) in {"CREATE", "DROP", "ALTER"}:
            columns = ["statement"]
            rows = [(f"{leading_keyword(case.sql)} 성공 · 반환 행 없음",)]
        else:
            columns = ["rows_affected"]
            rows = [(cursor.rowcount,)]

        if case.number == "Q13":
            status = connection.execute("SELECT status FROM orders WHERE id=18").fetchone()[0]
            assert cursor.rowcount == 1 and status == "SERVED"
            extra = "orders.id=18 status=SERVED PASS"
        elif case.number == "Q14":
            remaining = connection.execute("SELECT COUNT(*) FROM orders WHERE id=25").fetchone()[0]
            assert cursor.rowcount == 1 and remaining == 0
            extra = "orders.id=25 remaining=0 PASS"
        elif case.number == "Q15":
            indexes = connection.execute("PRAGMA index_list('orders')").fetchall()
            index_names = [row[1] for row in indexes]
            assert "idx_order_status" in index_names
            plan_rows = connection.execute(
                "EXPLAIN QUERY PLAN SELECT * FROM orders WHERE status='COOKING'"
            ).fetchall()
            plan = " | ".join(str(row[3]) for row in plan_rows)
            extra = f"idx_order_status exists PASS\nquery_plan={plan}"

        write_result(case, columns, rows, extra)
        checks.append(f"{case.number} PASS rows={len(rows)}")

    expected_texts = {EVIDENCE / f"query_{number:02d}_result.txt" for number in range(1, 16)}
    assert all(path.is_file() and path.stat().st_size > 0 for path in expected_texts)
    checks.append("core_text_evidence=15 PASS")
    connection.commit()
    return checks


def integrity_case(connection: sqlite3.Connection, name: str, sql: str, expected: str) -> str:
    try:
        connection.execute(sql)
    except sqlite3.IntegrityError as error:
        connection.rollback()
        message = str(error)
        assert expected in message, (name, message, expected)
        return f"{name}: PASS\nSQL: {sql}\nERROR: {type(error).__name__}: {message}"
    connection.rollback()
    raise AssertionError(f"{name}: 잘못된 데이터가 허용됐습니다.")


def sql_body(sql: str) -> str:
    """주석 줄을 제거한 순수 SQL 본문만 돌려준다(증거 파일에 주석이 섞이지 않게)."""
    return "\n".join(
        line for line in sql.splitlines() if not line.strip().startswith("--")
    ).strip()


def verify_integrity(connection: sqlite3.Connection) -> list[str]:
    """보너스 2: 4_bonus_queries.sql의 [F01]~[F04]를 읽어 위반이 차단되는지 실증한다.

    SQL 본문은 스크립트가 아니라 SQL 파일이 단일 진실 공급원(SSOT)이다.
    """
    fail_cases = split_cases("4_bonus_queries.sql", FAIL_MARKER)
    assert [case.number for case in fail_cases] == ["F01", "F02", "F03", "F04"], (
        f"무결성 파괴 테스트는 F01~F04 네 개여야 합니다: "
        f"{[case.number for case in fail_cases]}"
    )
    tests = [
        integrity_case(connection, FAIL_EXPECTED[case.number][0],
                       sql_body(case.sql), FAIL_EXPECTED[case.number][1])
        for case in fail_cases
    ]
    (EVIDENCE / "bonus_02_fk_error_test.txt").write_text(
        "=== INTEGRITY CONSTRAINT TESTS ===\n\n" + "\n\n".join(tests) + "\n",
        encoding="utf-8",
    )
    return [test.splitlines()[0] for test in tests]


def execute_bonus(connection: sqlite3.Connection, cases: list[SqlCase]) -> list[str]:
    assert len(cases) == 5, f"보너스 SQL은 5개여야 합니다: {len(cases)}"
    results: dict[str, tuple[list[str], list[sqlite3.Row]]] = {}
    for case in cases:
        cursor = connection.execute(case.sql)
        results[case.number] = ([column[0] for column in cursor.description], cursor.fetchall())

    join_rows = [tuple(row) for row in results["B01"][1]]
    subquery_rows = [tuple(row) for row in results["B02"][1]]
    assert join_rows == subquery_rows
    join_plan = connection.execute(
        "EXPLAIN QUERY PLAN SELECT DISTINCT m.id, m.name, m.price FROM menus m "
        "INNER JOIN orders o ON m.id=o.menu_id WHERE o.status='COOKING' ORDER BY m.id"
    ).fetchall()
    subquery_plan = connection.execute(
        "EXPLAIN QUERY PLAN SELECT m.id, m.name, m.price FROM menus m "
        "WHERE m.id IN (SELECT o.menu_id FROM orders o WHERE o.status='COOKING') ORDER BY m.id"
    ).fetchall()
    compare = [
        "=== BONUS 1: JOIN VS SUBQUERY ===",
        "",
        "JOIN RESULT",
        tsv(results["B01"][0], results["B01"][1]),
        "",
        "SUBQUERY RESULT",
        tsv(results["B02"][0], results["B02"][1]),
        "",
        "SET EQUALITY: PASS",
        "JOIN PLAN: " + " | ".join(str(row[3]) for row in join_plan),
        "SUBQUERY PLAN: " + " | ".join(str(row[3]) for row in subquery_plan),
        "결론: 현재 결과 집합은 같지만 성능은 DB·통계·데이터 분포에 따라 달라져 단정하지 않는다.",
    ]
    (EVIDENCE / "bonus_01_compare_methods.txt").write_text("\n".join(compare) + "\n", encoding="utf-8")

    kpi_sections = ["=== BONUS 3: KPI METRICS ==="]
    for number, title in [
        ("B03", "KPI 1 CATEGORY REVENUE SHARE"),
        ("B04", "KPI 2 AVERAGE REVENUE PER PHYSICAL TABLE"),
        ("B05", "KPI 3 KITCHEN CONGESTION"),
    ]:
        columns, rows = results[number]
        kpi_sections.extend(["", title, tsv(columns, rows)])
    (EVIDENCE / "bonus_03_kpi_metrics.txt").write_text("\n".join(kpi_sections) + "\n", encoding="utf-8")
    return ["bonus_join_subquery_equality PASS", "bonus_kpi_3 PASS"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep-db", type=Path, help="검증 DB를 지정 경로에 보관")
    args = parser.parse_args()
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    temporary = tempfile.TemporaryDirectory(prefix="b5-1-") if args.keep_db is None else None
    db_path = args.keep_db or Path(temporary.name) / "table_order.db"
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_connection = new_database(db_path)
    checks = verify_schema(schema_connection)
    schema_connection.close()

    # README의 sqlite3 CLI 순서(스키마 → seed → Q1~Q15 → 보너스)와 같은 흐름으로 한 연결에서 실행한다.
    # 그래서 Q13/Q14로 바뀐 뒤 상태를 보너스·KPI 증거도 그대로 담는다.
    core_cases = split_cases("3_queries.sql", CORE_MARKER)
    bonus_cases = split_cases("4_bonus_queries.sql", BONUS_MARKER)
    connection = new_database(db_path)
    checks.extend(execute_core(connection, core_cases))
    checks.append("bonus_runs_on_post_mutation_db PASS")
    checks.extend(verify_integrity(connection))
    checks.extend(execute_bonus(connection, bonus_cases))
    connection.close()
    checks.extend(verify_docs_sync(core_cases, bonus_cases))

    # 임시 디렉터리의 무작위 경로를 증거 파일에 쓰면 실행할 때마다
    # 내용이 달라진다. 새 DB를 썼다는 사실만 안정적으로 기록한다.
    summary = [
        "B5-1 AUTOMATED VERIFICATION: ALL PASS",
        f"SQLite version={sqlite3.sqlite_version}",
        "database=fresh SQLite database, one DB reused for core then bonus (README order)",
        "",
        *checks,
    ]
    (EVIDENCE / "verification_summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))

    if temporary is not None:
        temporary.cleanup()


if __name__ == "__main__":
    main()
