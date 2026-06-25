# Ticketing Platform

고동시성 환경의 좌석 예약, 주문, 결제, 티켓 발급을 다루는 백엔드 포트폴리오 프로젝트입니다.

## 기술 스택

- Java 21 LTS, Spring Boot 4.1
- Spring MVC, Spring Data JPA, Spring Security
- PostgreSQL 17, Flyway
- Testcontainers, Gradle
- Docker Compose

## 핵심 흐름

1. 사용자가 공연의 좌석을 조회합니다.
2. 예약 API가 요청 좌석을 정렬된 순서로 비관적 잠금하고 5분간 선점합니다.
3. 주문 생성 시 예약 소유자, 만료 시각, 결제 가능 상태를 검증합니다.
4. 결제 API는 `Idempotency-Key`로 재시도를 안전하게 처리합니다.
5. 결제 승인 트랜잭션에서 예약 확정, 주문 결제 완료, 좌석 판매, 티켓 발급을 원자적으로 처리합니다.
6. 만료 작업이 결제되지 않은 예약을 해제합니다.

현재 결제는 외부 PG 연동 전의 승인 시뮬레이터입니다. 다음 단계에서는 PG 호출과 내부 상태 변경을 분리하고 Outbox 및 보상 처리를 추가합니다.

## 실행

```bash
docker compose up -d
./gradlew bootRun
```

Windows에서는 `gradlew.bat bootRun`을 사용합니다.

데모 공연 ID는 `11111111-1111-1111-1111-111111111111`입니다.

### 좌석 조회

```http
GET /api/v1/performances/11111111-1111-1111-1111-111111111111/seats
```

### 좌석 예약

```http
POST /api/v1/performances/11111111-1111-1111-1111-111111111111/reservations
Content-Type: application/json

{
  "customerId": "22222222-2222-2222-2222-222222222222",
  "seatIds": ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1"]
}
```

### 주문 생성

```http
POST /api/v1/reservations/{reservationId}/orders
Content-Type: application/json

{
  "customerId": "22222222-2222-2222-2222-222222222222"
}
```

### 결제 승인

```http
POST /api/v1/orders/{orderId}/payments
Idempotency-Key: payment-request-001
Content-Type: application/json

{
  "amount": 120000
}
```

## 포트폴리오 확장 로드맵

- 동시 예약 통합 테스트와 k6 부하 테스트
- Redis 기반 대기열 및 좌석 조회 캐시
- 외부 PG 어댑터, 승인 타임아웃, 결제 대사 배치
- Transactional Outbox와 Kafka 기반 티켓 발급 이벤트
- 재시도, DLQ, 소비자 멱등성
- OpenTelemetry, Prometheus, Grafana 관측성
- OAuth2 Resource Server와 역할 기반 운영 API
- ArchUnit 기반 모듈 경계 검증
- ADR, 장애 시나리오, 성능 개선 전후 수치 문서화
