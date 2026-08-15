#!/usr/bin/env python3
"""B5-1 SQL을 새 SQLite DB에서 실행하고 제출 증거를 재생성한다."""

from __future__ import annotations

import argparse
import re
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CORE_MARKER = re.compile(r"-- \[(Q\d{2})\]\[([^\]]+)\] (.+)")
BONUS_MARKER = re.compile(r"-- \[(B\d{2})\]\[([^\]]+)\] (.+)")
EXPECTED_MINIMUM_ROWS = {
    "menu_categories": 10,
    "store_tables": 10,
    "menus": 10,
    "orders": 10,
}


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


def verify_schema(connection: sqlite3.Connection) -> list[str]:
    checks: list[str] = []
    tables = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )]
    expected_tables = sorted(EXPECTED_MINIMUM_ROWS)
    assert tables == expected_tables, (tables, expected_tables)
    checks.append(f"tables={len(tables)} PASS: {', '.join(tables)}")

    for table, minimum in EXPECTED_MINIMUM_ROWS.items():
        count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count >= minimum, f"{table}: {count} < {minimum}"
        checks.append(f"{table} rows={count} PASS")

        pk_count = sum(row[5] > 0 for row in connection.execute(f"PRAGMA table_info({table})"))
        assert pk_count >= 1, f"{table} PK 없음"
        checks.append(f"{table} PK={pk_count} PASS")

    fk_count = sum(
        len(connection.execute(f"PRAGMA foreign_key_list({table})").fetchall())
        for table in EXPECTED_MINIMUM_ROWS
    )
    assert fk_count >= 2
    checks.append(f"foreign_keys={fk_count} PASS")
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    checks.append("PRAGMA foreign_keys=ON PASS")
    return checks


def execute_core(connection: sqlite3.Connection, cases: list[SqlCase]) -> list[str]:
    assert len(cases) == 15, f"핵심 SQL은 15개여야 합니다: {len(cases)}"
    checks = ["core_queries=15 PASS"]
    for case in cases:
        cursor = connection.execute(case.sql)
        columns: list[str]
        rows: list[sqlite3.Row | tuple]
        extra = ""
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
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


def verify_integrity(connection: sqlite3.Connection) -> list[str]:
    tests = [
        integrity_case(
            connection,
            "FK 없는 좌석 참조 차단",
            "INSERT INTO orders VALUES(999,9999,1,1,'2026-06-24 21:00:00','COOKING')",
            "FOREIGN KEY",
        ),
        integrity_case(
            connection,
            "허용되지 않은 status 차단",
            "INSERT INTO orders VALUES(998,1,1,1,'2026-06-24 21:00:00','INVALID')",
            "CHECK constraint failed",
        ),
        integrity_case(
            connection,
            "음수 quantity 차단",
            "INSERT INTO orders VALUES(997,1,1,-1,'2026-06-24 21:00:00','COOKING')",
            "CHECK constraint failed",
        ),
        integrity_case(
            connection,
            "중복 table_number 차단",
            "INSERT INTO store_tables VALUES(999,1,4)",
            "UNIQUE constraint failed",
        ),
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

    core_connection = new_database(db_path)
    checks.extend(execute_core(core_connection, split_cases("3_queries.sql", CORE_MARKER)))
    core_connection.close()

    bonus_connection = new_database(db_path)
    checks.extend(verify_integrity(bonus_connection))
    checks.extend(execute_bonus(bonus_connection, split_cases("4_bonus_queries.sql", BONUS_MARKER)))
    bonus_connection.close()

    summary = [
        "B5-1 AUTOMATED VERIFICATION: ALL PASS",
        f"SQLite version={sqlite3.sqlite_version}",
        f"database={db_path}",
        "",
        *checks,
    ]
    (EVIDENCE / "verification_summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))

    if temporary is not None:
        temporary.cleanup()


if __name__ == "__main__":
    main()
