# 복잡 쿼리 단계별 분해 분석

## Query 5: 카테고리별 매출 기여 비중 (%)

**목적**: 각 메뉴 카테고리가 전체 매출에서 차지하는 비중을 계산

### 단계별 분해

**Step 1: 각 주문의 금액 계산**
```sql
-- 주문 수량 × 메뉴 가격 = 개별 주문 금액
SELECT o.id, o.quantity * m.price as order_amount
FROM orders o
JOIN menus m ON o.menu_id = m.id
```
중간 결과: 각 주문의 금액이 계산됨

**Step 2: 카테고리별 매출 합계**
```sql
-- 메뉴 → 카테고리 조인 후 카테고리별 합계
SELECT c.name as category, SUM(o.quantity * m.price) as category_sales
FROM orders o
JOIN menus m ON o.menu_id = m.id
JOIN menu_categories c ON m.category_id = c.id
GROUP BY c.name
```
중간 결과: 
| category | category_sales |
|----------|---------------|
| 시그니처 메인 | 285000 |
| 탕/전골 | 192000 |
| 사이드 | 78000 |

**Step 3: 전체 매출 대비 비중 계산 (윈도우 함수)**
```sql
-- 최종: 카테고리 매출 / 전체 매출 * 100
SELECT 
    c.name as category,
    SUM(o.quantity * m.price) as sales,
    ROUND(SUM(o.quantity * m.price) * 100.0 / 
        SUM(SUM(o.quantity * m.price)) OVER(), 1) as percentage
FROM orders o
JOIN menus m ON o.menu_id = m.id
JOIN menu_categories c ON m.category_id = c.id
GROUP BY c.name
ORDER BY percentage DESC
```
최종 결과:
| category | sales | percentage |
|----------|-------|------------|
| 시그니처 메인 | 285000 | 51.3% |
| 탕/전골 | 192000 | 34.6% |
| 사이드 | 78000 | 14.1% |

### 핵심 포인트
- `SUM() OVER()` 윈도우 함수로 전체 매출을 구하면서 동시에 카테고리별 합계도 계산
- `100.0`을 곱하여 소수점 계산 보장 (정수 나눗셈 방지)
- `ROUND()`로 소수점 1자리까지 표시

---

## Query 9: 좌석 수용 규모별 평균 주문 금액

**목적**: 좌석 크기(2인용/4인용/6인용)에 따른 평균 주문 금액 비교

### 단계별 분해

**Step 1: 각 주문의 금액 계산**
```sql
SELECT o.table_id, o.quantity * m.price as amount
FROM orders o
JOIN menus m ON o.menu_id = m.id
```

**Step 2: 좌석 정보와 조인 + 좌석 용량별 그룹화**
```sql
SELECT 
    CASE 
        WHEN t.capacity <= 2 THEN '소형(1-2인)'
        WHEN t.capacity <= 4 THEN '중형(3-4인)'
        ELSE '대형(5인+)'
    END as table_size,
    COALESCE(AVG(o.quantity * m.price), 0) as avg_amount
FROM store_tables t
LEFT JOIN orders o ON o.table_id = t.id
LEFT JOIN menus m ON o.menu_id = m.id
GROUP BY table_size
ORDER BY avg_amount DESC
```

### 핵심 포인트
- `CASE WHEN`으로 좌석 용량을 범주화
- `LEFT JOIN`으로 주문이 없는 좌석도 포함
- `COALESCE()`로 NULL을 0으로 변환

---

## Query 12: 조리 중인 티켓 비중 (조리 병목 지표)

**목적**: 현재 조리 중인 주문이 전체 주문에서 차지하는 비율

### 단계별 분해

**Step 1: 상태별 주문 수 집계**
```sql
SELECT status, COUNT(*) as count
FROM orders
GROUP BY status
```
중간 결과:
| status | count |
|--------|-------|
| COOKING | 8 |
| SERVED | 15 |

**Step 2: 조리 중 비율 계산**
```sql
SELECT 
    COUNT(CASE WHEN status = 'COOKING' THEN 1 END) as cooking_count,
    COUNT(*) as total,
    ROUND(COUNT(CASE WHEN status = 'COOKING' THEN 1 END) * 100.0 / COUNT(*), 1) as cooking_ratio
FROM orders
```
최종 결과:
| cooking_count | total | cooking_ratio |
|---------------|-------|---------------|
| 8 | 23 | 34.8% |

### 핵심 포인트
- `COUNT(CASE WHEN ... THEN 1 END)` 패턴으로 조건부 집계
- 전체 주문 대비 조리 중 비율로 병목 정도 파악
